import jsPDF from 'jspdf';
import { InvoiceType, INVOICE_TYPE_LABELS } from '../types';

export interface InvoicePdfData {
  invoiceType: InvoiceType;
  invoiceNumber: string;
  date: string;
  dueDate?: string;
  from: {
    name: string;
    address?: string;
    phone?: string;
    email?: string;
    taxId?: string;
    logo?: string;
  };
  to?: {
    name: string;
    address?: string;
    phone?: string;
    email?: string;
    taxId?: string;
  };
  items: { name: string; quantity: number; unit: string; price: number }[];
  currency: string;
  taxRate?: number;
  notes?: string;
  footer?: string;
}

export function generateInvoicePDF(data: InvoicePdfData): jsPDF {
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 15;
  const contentWidth = pageWidth - margin * 2;
  let y = margin;

  const subtotal = data.items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const taxRate = data.taxRate ?? 0;
  const taxAmount = (subtotal * taxRate) / 100;
  const total = subtotal + taxAmount;

  // --- Header background accent ---
  pdf.setFillColor(13, 148, 136); // teal-600
  pdf.rect(0, 0, pageWidth, 12, 'F');

  // --- Logo (if provided as data URL) ---
  let logoY = y + 18;
  if (data.from.logo && data.from.logo.startsWith('data:')) {
    try {
      const mimeMatch = data.from.logo.match(/data:([^/]+\/[^;]+);/);
      const format = mimeMatch && mimeMatch[1].includes('png') ? 'PNG' : 'JPEG';
      pdf.addImage(data.from.logo, format, margin, y + 14, 22, 22, undefined, 'FAST');
      logoY = y + 14 + 24;
    } catch {
      // Logo could not be embedded; continue without it.
    }
  }

  // --- From / Title ---
  pdf.setFontSize(22);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(17, 24, 39);
  pdf.text(data.from.name || 'POS', margin, logoY);

  pdf.setFontSize(11);
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(100, 116, 139);
  let infoY = y + 25;
  if (data.from.address) {
    pdf.text(data.from.address, margin, infoY);
    infoY += 5;
  }
  if (data.from.phone) {
    pdf.text(data.from.phone, margin, infoY);
    infoY += 5;
  }
  if (data.from.email) {
    pdf.text(data.from.email, margin, infoY);
    infoY += 5;
  }
  if (data.from.taxId) {
    pdf.text(`Tax ID: ${data.from.taxId}`, margin, infoY);
    infoY += 5;
  }

  // --- Invoice type badge ---
  pdf.setFillColor(13, 148, 136);
  pdf.setTextColor(255, 255, 255);
  pdf.setFontSize(12);
  pdf.setFont('helvetica', 'bold');
  const label = INVOICE_TYPE_LABELS[data.invoiceType];
  const labelWidth = pdf.getTextWidth(label) + 10;
  pdf.roundedRect(pageWidth - margin - labelWidth, y + 14, labelWidth, 8, 2, 2, 'F');
  pdf.text(label, pageWidth - margin - labelWidth / 2, y + 19, { align: 'center' });

  // --- Invoice meta ---
  pdf.setTextColor(17, 24, 39);
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(10);
  pdf.text(`${label} #: ${data.invoiceNumber}`, pageWidth - margin, y + 32, { align: 'right' });
  pdf.text(`Date: ${data.date}`, pageWidth - margin, y + 37, { align: 'right' });
  if (data.dueDate) {
    pdf.text(`Due Date: ${data.dueDate}`, pageWidth - margin, y + 42, { align: 'right' });
  }

  y = Math.max(infoY, y + 45);

  // --- Bill To / From boxes ---
  const boxHeight = 35;
  pdf.setDrawColor(226, 232, 240);
  pdf.setFillColor(248, 250, 252);
  pdf.roundedRect(margin, y, contentWidth / 2 - 5, boxHeight, 3, 3, 'FD');
  pdf.roundedRect(margin + contentWidth / 2 + 5, y, contentWidth / 2 - 5, boxHeight, 3, 3, 'FD');

  pdf.setFontSize(9);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(148, 163, 184);
  pdf.text('FROM', margin + 4, y + 7);
  pdf.text('BILL TO', margin + contentWidth / 2 + 9, y + 7);

  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(17, 24, 39);
  pdf.setFontSize(10);
  pdf.text(data.from.name || 'POS', margin + 4, y + 14);
  pdf.text(data.to?.name || 'Walk-in Customer', margin + contentWidth / 2 + 9, y + 14);

  pdf.setFontSize(9);
  pdf.setTextColor(71, 85, 105);
  if (data.from.address) pdf.text(data.from.address, margin + 4, y + 20);
  if (data.from.phone) pdf.text(data.from.phone, margin + 4, y + 26);
  if (data.to?.address) pdf.text(data.to.address, margin + contentWidth / 2 + 9, y + 20);
  if (data.to?.phone) pdf.text(data.to.phone, margin + contentWidth / 2 + 9, y + 26);

  y += boxHeight + 10;

  // --- Items table header ---
  pdf.setFillColor(241, 245, 249);
  pdf.setDrawColor(203, 213, 225);
  pdf.rect(margin, y, contentWidth, 10, 'FD');
  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(51, 65, 85);
  pdf.text('Item', margin + 3, y + 7);
  pdf.text('Qty', margin + contentWidth * 0.45, y + 7);
  pdf.text('Unit Price', margin + contentWidth * 0.62, y + 7);
  pdf.text('Amount', margin + contentWidth * 0.82, y + 7);
  y += 10;

  // --- Items ---
  pdf.setFont('helvetica', 'normal');
  pdf.setTextColor(17, 24, 39);
  data.items.forEach((item) => {
    const amount = item.price * item.quantity;
    pdf.text(item.name, margin + 3, y + 6);
    pdf.text(`${item.quantity} ${item.unit}`, margin + contentWidth * 0.45, y + 6);
    pdf.text(`${data.currency} ${item.price.toFixed(2)}`, margin + contentWidth * 0.62, y + 6);
    pdf.text(`${data.currency} ${amount.toFixed(2)}`, margin + contentWidth * 0.82, y + 6);
    pdf.setDrawColor(226, 232, 240);
    pdf.line(margin, y + 8, margin + contentWidth, y + 8);
    y += 10;
  });

  // --- Totals ---
  const totalsX = pageWidth - margin - 70;
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(10);
  pdf.setTextColor(71, 85, 105);
  pdf.text('Subtotal:', totalsX, y + 6);
  pdf.text(`${data.currency} ${subtotal.toFixed(2)}`, pageWidth - margin, y + 6, { align: 'right' });
  y += 7;
  pdf.text(`Tax (${taxRate}%):`, totalsX, y + 6);
  pdf.text(`${data.currency} ${taxAmount.toFixed(2)}`, pageWidth - margin, y + 6, { align: 'right' });
  y += 9;

  pdf.setFillColor(240, 253, 250);
  pdf.setDrawColor(13, 148, 136);
  pdf.roundedRect(totalsX - 5, y, 75, 10, 2, 2, 'FD');
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(13, 148, 136);
  pdf.text('Total:', totalsX, y + 7);
  pdf.text(`${data.currency} ${total.toFixed(2)}`, pageWidth - margin, y + 7, { align: 'right' });
  y += 18;

  // --- Notes ---
  if (data.notes) {
    pdf.setFontSize(9);
    pdf.setFont('helvetica', 'bold');
    pdf.setTextColor(148, 163, 184);
    pdf.text('NOTES', margin, y);
    y += 6;
    pdf.setFont('helvetica', 'normal');
    pdf.setTextColor(71, 85, 105);
    const notesLines = pdf.splitTextToSize(data.notes, contentWidth);
    pdf.text(notesLines, margin, y);
    y += notesLines.length * 5 + 4;
  }

  // --- Footer branding ---
  const footerY = pageHeight - margin - 18;
  pdf.setDrawColor(13, 148, 136);
  pdf.setLineWidth(0.5);
  pdf.line(margin, footerY, pageWidth - margin, footerY);

  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'bold');
  pdf.setTextColor(17, 24, 39);
  pdf.text('Structa Cloud', margin, footerY + 7);
  pdf.setFont('helvetica', 'normal');
  pdf.setFontSize(8);
  pdf.setTextColor(100, 116, 139);
  pdf.text('Powered by Structa Cloud', margin, footerY + 12);
  if (data.footer) {
    pdf.text(data.footer, margin, footerY + 17);
  }
  pdf.text('https://structa.cloud', pageWidth - margin, footerY + 7, { align: 'right' });

  return pdf;
}

export async function downloadInvoicePDF(data: InvoicePdfData, filename?: string): Promise<void> {
  const { save } = await import('@tauri-apps/plugin-dialog');
  const { writeFile } = await import('@tauri-apps/plugin-fs');

  const pdf = generateInvoicePDF(data);
  const pdfBlob = pdf.output('arraybuffer');
  const pdfArray = new Uint8Array(pdfBlob);

  const defaultName = filename || `invoice-${data.invoiceNumber}.pdf`;
  const filePath = await save({
    defaultPath: defaultName,
    filters: [{ name: 'PDF', extensions: ['pdf'] }],
  });

  if (filePath) {
    await writeFile(filePath, pdfArray);
  }
}
