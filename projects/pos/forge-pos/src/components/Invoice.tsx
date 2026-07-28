import { forwardRef } from 'react';
import { useTranslation } from 'react-i18next';
import { InvoiceType, INVOICE_TYPE_LABELS } from '../types';

// ---- Types -----------------------------------------------------------------

export type PageDesign = 'modern' | 'classic' | 'minimal';

export interface InvoiceItem {
  name: string;
  quantity: number;
  unit: string;
  price: number;
}

export interface InvoiceParty {
  name: string;
  address?: string;
  phone?: string;
  email?: string;
  taxId?: string;
  logo?: string;
}

export interface InvoiceProps {
  invoiceType: InvoiceType;
  pageDesign?: PageDesign;
  invoiceNumber: string;
  date: string;
  dueDate?: string;
  from: InvoiceParty;
  to?: InvoiceParty;
  items: InvoiceItem[];
  currency: string;
  taxRate?: number;
  notes?: string;
  /** Custom footer message (e.g. "Thank you for your business") */
  footer?: string;
  /** Invoice category ID for categorization badge */
  category?: string;
}

// ---- Constants -------------------------------------------------------------

const TYPE_ACCENT: Record<string, { badge: string; total: string; border: string }> = {
  tax:        { badge: 'badge badge-primary',                total: 'badge badge-primary',       border: 'border-teal-200' },
  commercial: { badge: 'badge badge-secondary',              total: 'badge badge-secondary',     border: 'border-indigo-200' },
  proforma:   { badge: 'badge badge-warning',                total: 'badge badge-warning',       border: 'border-amber-200' },
  credit:     { badge: 'badge badge-error',                  total: 'badge badge-error',         border: 'border-rose-200' },
  receipt:    { badge: 'badge badge-success',                total: 'badge badge-success',       border: 'border-emerald-200' },
  selling:    { badge: 'badge badge-info',                   total: 'badge badge-info',          border: 'border-sky-200' },
  goods_transfer: { badge: 'badge badge-accent',             total: 'badge badge-accent',        border: 'border-violet-200' },
};

const CATEGORY_LABELS: Record<string, string> = {
  get_goods: 'Get Goods',
  transfer_goods: 'Transfer In',
  products: 'Products',
  production_creation: 'Production',
  employee_meal: 'Employee Meal',
  all_transactions: 'All Transactions',
  pay_supplier: 'Pay Supplier',
  transfer_out: 'Transfer Out',
};

// ---- Design wrappers -------------------------------------------------------

/** Returns the outer page className depending on the chosen design. */
function pageClass(design: PageDesign): string {
  const base = 'invoice-page bg-white text-slate-900 max-w-[210mm] mx-auto shadow-2xl';
  switch (design) {
    case 'modern':  return `${base} rounded-none`;
    case 'classic': return `${base} rounded-sm border border-slate-300`;
    case 'minimal': return `${base} rounded-lg`;
  }
}

/** Returns the header section className per design. */
function headerClass(design: PageDesign, accent: string): string {
  switch (design) {
    case 'modern':
      return `flex flex-col md:flex-row justify-between items-start gap-6 mb-8 p-8 -mx-0 bg-gradient-to-br from-slate-900 to-teal-900 text-white rounded-none`;
    case 'classic':
      return `flex flex-col md:flex-row justify-between items-start gap-6 mb-8 pb-6 border-b-4 ${accent}`;
    case 'minimal':
    default:
      return `flex flex-col md:flex-row justify-between items-start gap-6 mb-8 pb-5 border-b border-slate-200`;
  }
}

// ---- Component -------------------------------------------------------------

const Invoice = forwardRef<HTMLDivElement, InvoiceProps>(
  (
    {
      invoiceType,
      pageDesign = 'modern',
      invoiceNumber,
      date,
      dueDate,
      from,
      to,
      items,
      currency,
      taxRate = 0,
      notes,
      footer,
      category,
    },
    ref
  ) => {
    const { t } = useTranslation();

    const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const taxAmount = (subtotal * taxRate) / 100;
    const total = subtotal + taxAmount;

    const accent = TYPE_ACCENT[invoiceType] || TYPE_ACCENT['commercial'];
    const catLabel = category ? (CATEGORY_LABELS[category] || category) : null;
    const isModern = pageDesign === 'modern';
    const textMuted = isModern ? 'text-white/70' : 'text-slate-500';
    const textHeading = isModern ? 'text-white' : 'text-slate-900';

    return (
      <div ref={ref} className="invoice-container font-sans">
        <div className={pageClass(pageDesign)}>

          {/* ---------------------------------------------------------------- */}
          {/* HEADER                                                            */}
          {/* ---------------------------------------------------------------- */}
          <div className={headerClass(pageDesign, accent.border)}>
            {/* Company / from block */}
            <div className="flex items-start gap-4">
              {from.logo && (
                <img
                  src={from.logo}
                  alt={`${from.name} logo`}
                  className="w-16 h-16 object-contain rounded-lg border border-white/20 bg-white/10 p-1 shrink-0"
                />
              )}
              <div>
                <h1 className={`text-2xl font-extrabold tracking-tight leading-tight ${textHeading}`}>
                  {from.name || 'Forge POS'}
                </h1>
                {from.address && <p className={`text-sm mt-0.5 ${textMuted}`}>{from.address}</p>}
                {from.phone   && <p className={`text-sm ${textMuted}`}>{from.phone}</p>}
                {from.email   && <p className={`text-sm ${textMuted}`}>{from.email}</p>}
                {from.taxId   && <p className={`text-sm ${textMuted}`}>{t('invoice.taxId')}: {from.taxId}</p>}
              </div>
            </div>

            {/* Invoice type badge + category + meta */}
            <div className="text-right shrink-0">
              <div className="flex items-center justify-end gap-2 mb-2">
                <span className={`inline-block px-4 py-1.5 text-xs font-bold tracking-widest uppercase rounded-md shadow ${accent.badge}`}>
                  {INVOICE_TYPE_LABELS[invoiceType] || String(invoiceType).toUpperCase()}
                </span>
                {catLabel && (
                  <span className="inline-block px-3 py-1.5 text-[10px] font-semibold tracking-wide uppercase rounded-md bg-slate-100 dark:bg-white/10 text-slate-600 dark:text-white/60 border border-slate-200 dark:border-white/10">
                    {catLabel}
                  </span>
                )}
              </div>
              <div className="mt-3 space-y-1">
                <p className={`text-sm ${textMuted}`}>
                  <span className={`font-semibold ${textHeading}`}>{t('invoice.invoiceNumber')}:</span>{' '}
                  {invoiceNumber}
                </p>
                <p className={`text-sm ${textMuted}`}>
                  <span className={`font-semibold ${textHeading}`}>{t('invoice.date')}:</span>{' '}
                  {date}
                </p>
                {dueDate && (
                  <p className={`text-sm ${textMuted}`}>
                    <span className={`font-semibold ${textHeading}`}>{t('invoice.dueDate')}:</span>{' '}
                    {dueDate}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Padding wrapper for the body when using modern (header uses negative margins) */}
          <div className={isModern ? 'px-8 pb-8' : 'px-8 pb-8'}>

            {/* -------------------------------------------------------------- */}
            {/* FROM / TO CARDS                                                 */}
            {/* -------------------------------------------------------------- */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8">
              <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2">
                  {t('invoice.from')}
                </h3>
                <p className="font-semibold text-slate-900">{from.name}</p>
                {from.address && <p className="text-sm text-slate-600 whitespace-pre-line mt-0.5">{from.address}</p>}
                {from.phone   && <p className="text-sm text-slate-600">{from.phone}</p>}
                {from.email   && <p className="text-sm text-slate-600">{from.email}</p>}
              </div>

              {to ? (
                <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
                  <h3 className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-2">
                    {t('invoice.to')}
                  </h3>
                  <p className="font-semibold text-slate-900">{to.name}</p>
                  {to.address && <p className="text-sm text-slate-600 whitespace-pre-line mt-0.5">{to.address}</p>}
                  {to.phone   && <p className="text-sm text-slate-600">{to.phone}</p>}
                  {to.email   && <p className="text-sm text-slate-600">{to.email}</p>}
                  {to.taxId   && <p className="text-sm text-slate-600">{t('invoice.taxId')}: {to.taxId}</p>}
                </div>
              ) : (
                <div className="bg-slate-50/50 rounded-lg p-4 border border-dashed border-slate-200 flex items-center justify-center">
                  <p className="text-xs text-slate-400 italic">{t('invoice.noBillTo', 'No bill-to party specified')}</p>
                </div>
              )}
            </div>

            {/* -------------------------------------------------------------- */}
            {/* ITEMS TABLE                                                     */}
            {/* -------------------------------------------------------------- */}
            <div className="mb-8 overflow-hidden rounded-xl border border-slate-200 shadow-sm">
              <table className="w-full text-sm">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="text-left px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wider">
                      {t('invoice.item')}
                    </th>
                    <th className="text-center px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wider">
                      {t('invoice.qty')}
                    </th>
                    <th className="text-right px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wider">
                      {t('invoice.unitPrice')}
                    </th>
                    <th className="text-right px-4 py-3 font-semibold text-slate-600 text-xs uppercase tracking-wider">
                      {t('invoice.amount')}
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {items.map((item, i) => (
                    <tr key={i} className={i % 2 === 0 ? 'bg-white' : 'bg-slate-50/60'}>
                      <td className="px-4 py-3 font-medium text-slate-800">{item.name}</td>
                      <td className="px-4 py-3 text-center text-slate-600">
                        {item.quantity} <span className="text-slate-400 text-xs">{item.unit}</span>
                      </td>
                      <td className="px-4 py-3 text-right text-slate-600">
                        {currency} {item.price.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 text-right font-semibold text-slate-800">
                        {currency} {(item.price * item.quantity).toFixed(2)}
                      </td>
                    </tr>
                  ))}

                  {items.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-4 py-8 text-center text-slate-400 italic text-sm">
                        No items added yet
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* -------------------------------------------------------------- */}
            {/* TOTALS                                                          */}
            {/* -------------------------------------------------------------- */}
            <div className="flex justify-end mb-8">
              <div className="w-full md:w-72 space-y-0 rounded-xl overflow-hidden border border-slate-200 shadow-sm">
                <div className="flex justify-between px-4 py-2.5 bg-white border-b border-slate-100">
                  <span className="text-slate-500 text-sm">{t('invoice.subtotal')}</span>
                  <span className="font-semibold text-slate-800 text-sm">{currency} {subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between px-4 py-2.5 bg-white border-b border-slate-100">
                  <span className="text-slate-500 text-sm">{t('invoice.tax')} ({taxRate}%)</span>
                  <span className="font-semibold text-slate-800 text-sm">{currency} {taxAmount.toFixed(2)}</span>
                </div>
                <div className={`flex justify-between px-4 py-3 ${accent.total}`}>
                  <span className="font-bold">{t('invoice.total')}</span>
                  <span className="font-bold text-lg">{currency} {total.toFixed(2)}</span>
                </div>
              </div>
            </div>

            {/* -------------------------------------------------------------- */}
            {/* NOTES                                                           */}
            {/* -------------------------------------------------------------- */}
            {notes && (
              <div className="mb-8 bg-amber-50 border border-amber-100 rounded-lg p-4">
                <h3 className="text-[10px] font-bold uppercase tracking-widest text-amber-500 mb-1.5">
                  {t('invoice.notes')}
                </h3>
                <p className="text-sm text-slate-600 whitespace-pre-line">{notes}</p>
              </div>
            )}

            {/* -------------------------------------------------------------- */}
            {/* STRUCTA.CLOUD BRANDED FOOTER                                   */}
            {/* -------------------------------------------------------------- */}
            <div className="mt-auto pt-6 border-t-2 border-slate-100">
              {footer && (
                <p className="text-center text-sm text-slate-500 italic mb-4">{footer}</p>
              )}

              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                {/* Brand */}
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-teal-500 to-teal-700 flex items-center justify-center shadow-md shrink-0">
                    {/* Inline SVG fallback logo — shows if remote logo fails */}
                    <img
                      src="https://structa.cloud/favicon.ico"
                      alt="Structa Cloud"
                      className="w-6 h-6 object-contain"
                      onError={(e) => {
                        const el = e.currentTarget as HTMLImageElement;
                        el.style.display = 'none';
                        if (el.parentElement) {
                          el.parentElement.innerHTML =
                            '<span class="text-white font-black text-base">S</span>';
                        }
                      }}
                    />
                  </div>
                  <div>
                    <p className="font-bold text-slate-900 text-sm leading-tight">Structa Cloud</p>
                    <p className="text-[10px] text-slate-400 leading-tight">
                      {t('invoice.poweredBy', 'Powered by POS')} &mdash; structa.cloud
                    </p>
                  </div>
                </div>

                {/* Invoice type pill + url */}
                <div className="flex flex-col items-end gap-1">
                  <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${accent.badge}`}>
                    {INVOICE_TYPE_LABELS[invoiceType] || String(invoiceType).toUpperCase()}
                  </span>
                  <p className="text-[10px] text-slate-400 tracking-wide">https://structa.cloud</p>
                </div>
              </div>
            </div>

          </div>{/* end body padding wrapper */}
        </div>

        {/* ------------------------------------------------------------------ */}
        {/* PRINT STYLES                                                        */}
        {/* ------------------------------------------------------------------ */}
        <style dangerouslySetInnerHTML={{
          __html: `
          @media print {
            @page { size: A4; margin: 0; }
            html, body {
              width: 210mm; height: 297mm;
              margin: 0; padding: 0; background: white;
            }
            body * { display: none !important; }
            .invoice-container {
              display: block !important;
              position: static !important;
              visibility: visible !important;
              width: 210mm !important;
              min-height: 297mm !important;
              margin: 0 !important; padding: 0 !important;
              background: white !important;
            }
            .invoice-container * {
              display: revert !important;
              visibility: visible !important;
            }
            .invoice-page {
              box-shadow: none !important;
              border: none !important;
              width: 210mm !important;
              min-height: 297mm !important;
              margin: 0 !important;
            }
          }
        ` }} />
      </div>
    );
  }
);

Invoice.displayName = 'Invoice';

export default Invoice;
