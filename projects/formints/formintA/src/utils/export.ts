import * as XLSX from 'xlsx';
import jsPDF from 'jspdf';
import { save } from '@tauri-apps/plugin-dialog';
import { writeFile } from '@tauri-apps/plugin-fs';

export interface ExportColumn<T = Record<string, unknown>> {
  header: string;
  key: string;
  accessor?: (row: T) => string | number | null | undefined;
}

function rowsToArrays<T>(rows: T[], columns: ExportColumn<T>[]): (string | number)[][] {
  return rows.map(row =>
    columns.map(col => {
      if (col.accessor) {
        const value = col.accessor(row);
        return value === null || value === undefined ? '' : value;
      }
      const value = (row as Record<string, unknown>)[col.key];
      return value === null || value === undefined ? '' : (value as string | number);
    })
  );
}

export function downloadCSV<T>(filename: string, columns: ExportColumn<T>[], rows: T[]): void {
  const headers = columns.map(c => c.header);
  const data = rowsToArrays(rows, columns);
  const csv = [headers, ...data]
    .map(row =>
      row
        .map(cell => {
          const text = String(cell).replace(/"/g, '""');
          return `"${text}"`;
        })
        .join(',')
    )
    .join('\n');

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export async function downloadExcel<T>(
  filename: string,
  sheetName: string,
  columns: ExportColumn<T>[],
  rows: T[]
): Promise<void> {
  const headers = columns.map(c => c.header);
  const data = rowsToArrays(rows, columns);
  const worksheet = XLSX.utils.aoa_to_sheet([headers, ...data]);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });

  const filePath = await save({
    defaultPath: filename,
    filters: [{ name: 'Excel', extensions: ['xlsx'] }],
  });

  if (filePath) {
    await writeFile(filePath, new Uint8Array(excelBuffer));
  }
}

export async function exportPDF(
  filename: string,
  title: string,
  sections: { title: string; rows: string[][] }[]
): Promise<void> {
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
  let y = 15;
  const margin = 15;
  const pageWidth = pdf.internal.pageSize.getWidth();

  pdf.setFontSize(18);
  pdf.setFont('helvetica', 'bold');
  pdf.text(title, pageWidth / 2, y, { align: 'center' });
  y += 10;

  pdf.setFontSize(10);
  pdf.setFont('helvetica', 'normal');
  pdf.text(`Generated: ${new Date().toLocaleString()}`, pageWidth / 2, y, { align: 'center' });
  y += 15;

  for (const section of sections) {
    pdf.setFontSize(14);
    pdf.setFont('helvetica', 'bold');
    pdf.text(section.title, margin, y);
    y += 8;

    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    for (const row of section.rows) {
      const line = row.join('  ');
      const lines = pdf.splitTextToSize(line, pageWidth - margin * 2);
      if (y > 270) {
        pdf.addPage();
        y = 15;
      }
      pdf.text(lines, margin, y);
      y += lines.length * 5 + 2;
    }
    y += 5;
  }

  const pdfBlob = pdf.output('arraybuffer');
  const filePath = await save({
    defaultPath: filename,
    filters: [{ name: 'PDF', extensions: ['pdf'] }],
  });

  if (filePath) {
    await writeFile(filePath, new Uint8Array(pdfBlob));
  }
}
