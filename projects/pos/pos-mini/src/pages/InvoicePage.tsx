/**
 * InvoicePage
 * ===========
 * Full-featured invoice builder / viewer page.
 *
 * Left sidebar  — controls: invoice type, page design, customer, free-form items
 * Right panel   — live A4 Invoice preview (uses Invoice.tsx component)
 *
 * Actions available:
 *   - Browser print  (window.print())
 *   - PDF download   (jsPDF html() method)
 *   - Open sidecar   (opens the rendered HTML invoice from the Sanic server
 *                     via the system browser when the sidecar is running)
 *
 * The page can be opened in two modes:
 *   1. /invoice             — blank invoice builder
 *   2. /invoice?sale=<id>   — pre-filled from an existing sale record
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { invoke } from '@tauri-apps/api/core';

import {
  MdDownload, MdPrint, MdAdd, MdDelete,
  MdOpenInNew, MdRefresh, MdArrowDropDown,
} from 'react-icons/md';
import { FaFileInvoiceDollar } from 'react-icons/fa';
import jsPDF from 'jspdf';

import PageLayout from '../components/PageLayout';
import Invoice, { PageDesign, InvoiceItem } from '../components/Invoice';
import { Customer, Settings, InvoiceType as AppInvoiceType, INVOICE_TYPE_LABELS } from '../types';
import { sidecar, data } from '../api';
import type { InvoiceType, InvoiceDesign } from '../api';

// ---- Constants -------------------------------------------------------------

const INVOICE_TYPES: AppInvoiceType[] = ['tax', 'commercial', 'proforma', 'credit', 'receipt'];
const PAGE_DESIGNS: { value: PageDesign; label: string; desc: string }[] = [
  { value: 'modern',  label: 'Modern',  desc: 'Dark gradient header' },
  { value: 'classic', label: 'Classic', desc: 'Bordered with teal rule' },
  { value: 'minimal', label: 'Minimal', desc: 'Clean & lightweight' },
];

const CURRENCIES = ['USD', 'EUR', 'GBP', 'SAR', 'AED', 'EGP', 'MAD', 'TND'];

// ---- Empty item factory ----------------------------------------------------

const newItem = (): InvoiceItem & { id: number } => ({
  id: Date.now() + Math.random(),
  name: '',
  quantity: 1,
  unit: 'pc',
  price: 0,
});

// ---- Component -------------------------------------------------------------

export default function InvoicePage() {

  const [searchParams] = useSearchParams();
  const invoiceRef = useRef<HTMLDivElement>(null);

  // ---- Settings -----
  const [settings, setSettings] = useState<Settings | null>(null);

  // ---- Invoice form state -----
  const [invoiceType, setInvoiceType]   = useState<AppInvoiceType>('commercial');
  const [pageDesign, setPageDesign]     = useState<PageDesign>('modern');
  const [invoiceNumber, setInvoiceNumber] = useState(`INV-${Date.now().toString().slice(-6)}`);
  const [date, setDate]                 = useState(new Date().toISOString().split('T')[0]);
  const [dueDate, setDueDate]           = useState('');
  const [currency, setCurrency]         = useState('USD');
  const [taxRate, setTaxRate]           = useState(0);
  const [notes, setNotes]               = useState('');
  const [footer, setFooter]             = useState('Thank you for your business!');

  // ---- Items -----
  const [items, setItems] = useState<(InvoiceItem & { id: number })[]>([newItem()]);

  // ---- Customer (bill-to) -----
  const [customers, setCustomers]         = useState<Customer[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState<number | null>(null);
  const [toName, setToName]   = useState('');
  const [toEmail, setToEmail] = useState('');
  const [toPhone, setToPhone] = useState('');
  const [toAddress, setToAddress] = useState('');

  // ---- UI state -----
  const [sidebarTab, setSidebarTab] = useState<'invoice' | 'items' | 'customer'>('invoice');
  const [sidecarRunning, setSidecarRunning] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [toast, setToast] = useState<{ msg: string; type: 'ok' | 'err' } | null>(null);

  // ---- Load settings + customers on mount -----
  useEffect(() => {
    invoke<Settings>('get_settings').then(s => {
      setSettings(s);
      if (s.tax_rate) setTaxRate(parseFloat(s.tax_rate) || 0);
      if (s.currency) setCurrency(s.currency);
    }).catch(() => {});

    invoke<Customer[]>('get_customers').then(setCustomers).catch(() => {});

    sidecar.healthCheck().then(setSidecarRunning);
  }, []);

  // ---- Pre-fill from sale query param -----
  useEffect(() => {
    const saleId = searchParams.get('sale');
    if (!saleId) return;

    const loadFromSidecar = async () => {
      const { data: sale, ok } = await data.getSale(parseInt(saleId));
      if (ok && sale) {
        setInvoiceNumber(`INV-${sale.id}`);
        setDate(sale.date ?? date);
        setCurrency(sale.currency ?? 'USD');
        setItems(sale.items.map((it) => ({
          id: Date.now() + Math.random(),
          name: it.product_name,
          price: it.price,
          quantity: it.quantity,
          unit: it.unit,
        })));
        if (sale.customer_id) setSelectedCustomerId(sale.customer_id);
        return;
      }
      // Fallback: load from Rust backend
      try {
        const sales = await invoke<any[]>('get_sales');
        const sale = sales.find(s => s.id === parseInt(saleId));
        if (sale) {
          setInvoiceNumber(`INV-${sale.id}`);
          setDate(sale.date ?? date);
          setCurrency(sale.currency ?? 'USD');
          if (sale.customer_id) setSelectedCustomerId(sale.customer_id);
        }
      } catch { /* silent */ }
    };
    loadFromSidecar();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  // ---- Sync selected customer to to-fields -----
  useEffect(() => {
    if (selectedCustomerId == null) return;
    const c = customers.find(c => c.id === selectedCustomerId);
    if (c) {
      setToName(c.name ?? '');
      setToEmail(c.email ?? '');
      setToPhone(c.phone ?? '');
    }
  }, [selectedCustomerId, customers]);

  // ---- Toast helper -----
  const showToast = useCallback((msg: string, type: 'ok' | 'err' = 'ok') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3200);
  }, []);

  // ---- Items CRUD -----
  const addItem   = () => setItems(prev => [...prev, newItem()]);
  const removeItem = (id: number) => setItems(prev => prev.filter(i => i.id !== id));
  const updateItem = (id: number, field: keyof InvoiceItem, value: string | number) =>
    setItems(prev => prev.map(i => i.id === id ? { ...i, [field]: value } : i));

  // ---- Print -----
  const handlePrint = () => window.print();

  // ---- PDF export -----
  const handlePdfExport = async () => {
    if (!invoiceRef.current) return;
    setIsExporting(true);
    try {
      const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' });
      await pdf.html(invoiceRef.current, {
        callback: (doc) => {
          doc.save(`invoice-${invoiceNumber}.pdf`);
        },
        x: 0,
        y: 0,
        width: 210,
        windowWidth: invoiceRef.current.offsetWidth,
      });
      showToast('PDF saved successfully');
    } catch {
      showToast('PDF export failed', 'err');
    } finally {
      setIsExporting(false);
    }
  };

  // ---- Open sidecar-rendered invoice in system browser -----
  const handleOpenSidecar = async () => {
    const saleId = searchParams.get('sale');
    if (!saleId) {
      showToast('Load a sale first to use sidecar preview', 'err');
      return;
    }
    const url = data.getInvoiceUrl(parseInt(saleId), invoiceType as InvoiceType, pageDesign as InvoiceDesign);
    try {
      const { openPath } = await import('@tauri-apps/plugin-opener');
      await openPath(url);
    } catch {
      window.open(url, '_blank');
    }
  };

  // ---- Derived to-party -----
  const toParty = toName ? { name: toName, email: toEmail, phone: toPhone, address: toAddress } : undefined;

  // ---- Render -----
  return (
    <PageLayout title={<><FaFileInvoiceDollar className="w-5 h-5 text-teal-500" /> Invoice Builder</>}>
      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 px-5 py-2.5 rounded-full text-sm font-semibold shadow-lg ${
              toast.type === 'ok'
                ? 'bg-teal-600 text-white'
                : 'bg-rose-600 text-white'
            }`}
          >
            {toast.msg}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex flex-col xl:flex-row gap-6">

        {/* SIDEBAR */}
        <aside className="w-full xl:w-80 shrink-0 space-y-4">

          {/* Action buttons */}
          <div className="grid grid-cols-3 gap-2">
            <motion.button
              whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.96 }}
              onClick={handlePrint}
              className="flex flex-col items-center gap-1 py-3 rounded-xl bg-slate-800 text-white text-xs font-semibold shadow hover:bg-slate-700"
            >
              <MdPrint className="w-5 h-5" />
              Print
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.96 }}
              onClick={handlePdfExport}
              disabled={isExporting}
              className="flex flex-col items-center gap-1 py-3 rounded-xl bg-teal-600 text-white text-xs font-semibold shadow hover:bg-teal-700 disabled:opacity-60"
            >
              {isExporting
                ? <MdRefresh className="w-5 h-5 animate-spin" />
                : <MdDownload className="w-5 h-5" />}
              {isExporting ? 'Saving…' : 'PDF'}
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.96 }}
              onClick={handleOpenSidecar}
              title={!sidecarRunning ? 'Sidecar not running' : 'Open in browser'}
              className={`flex flex-col items-center gap-1 py-3 rounded-xl text-xs font-semibold shadow ${
                sidecarRunning
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                  : 'bg-slate-200 text-slate-400 dark:bg-slate-700 cursor-not-allowed'
              }`}
            >
              <MdOpenInNew className="w-5 h-5" />
              Preview
            </motion.button>
          </div>

          {/* Sidecar status badge */}
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium ${
            sidecarRunning
              ? 'bg-teal-50 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400'
              : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${sidecarRunning ? 'bg-teal-500' : 'bg-slate-400'}`} />
            Sanic sidecar: {sidecarRunning ? 'running' : 'stopped'}
          </div>

          {/* Sidebar tabs */}
          <div className="flex rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700">
            {(['invoice', 'items', 'customer'] as const).map(tab => (
              <button
                key={tab}
                onClick={() => setSidebarTab(tab)}
                className={`flex-1 py-2 text-xs font-semibold capitalize transition-colors ${
                  sidebarTab === tab
                    ? 'bg-teal-600 text-white'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* TAB: Invoice */}
          {sidebarTab === 'invoice' && (
            <div className="card--glass rounded-xl p-4 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Invoice Type</label>
                <div className="grid grid-cols-1 gap-1.5">
                  {INVOICE_TYPES.map(type => (
                    <button
                      key={type}
                      onClick={() => setInvoiceType(type)}
                      className={`w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        invoiceType === type
                          ? 'bg-teal-600 text-white shadow-sm'
                          : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                      }`}
                    >
                      {INVOICE_TYPE_LABELS[type]}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">Page Design</label>
                <div className="grid grid-cols-1 gap-1.5">
                  {PAGE_DESIGNS.map(d => (
                    <button
                      key={d.value}
                      onClick={() => setPageDesign(d.value)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-all ${
                        pageDesign === d.value
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200'
                      }`}
                    >
                      <span className="font-medium text-sm">{d.label}</span>
                      <span className={`block text-[11px] ${pageDesign === d.value ? 'text-indigo-200' : 'text-slate-400'}`}>
                        {d.desc}
                      </span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <FormField label="Invoice #" value={invoiceNumber} onChange={setInvoiceNumber} />
                <FormField label="Date" type="date" value={date} onChange={setDate} />
                <FormField label="Due Date" type="date" value={dueDate} onChange={setDueDate} />
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">Currency</label>
                  <div className="relative">
                    <select value={currency} onChange={e => setCurrency(e.target.value)}
                      className="w-full appearance-none bg-slate-100 dark:bg-slate-700 border-0 rounded-lg px-3 py-2 text-sm text-slate-800 dark:text-slate-200 pr-8 focus:ring-2 focus:ring-teal-500 outline-none"
                    >
                      {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                    <MdArrowDropDown className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5 pointer-events-none" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 mb-1">Tax Rate (%)</label>
                  <input type="number" min="0" max="100" step="0.5" value={taxRate}
                    onChange={e => setTaxRate(parseFloat(e.target.value) || 0)}
                    className="w-full bg-slate-100 dark:bg-slate-700 border-0 rounded-lg px-3 py-2 text-sm text-slate-800 dark:text-slate-200 focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>
                <FormField label="Notes" value={notes} onChange={setNotes} multiline />
                <FormField label="Footer Message" value={footer} onChange={setFooter} />
              </div>
            </div>
          )}

          {/* TAB: Items */}
          {sidebarTab === 'items' && (
            <div className="card--glass rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Line Items ({items.length})</span>
                <motion.button
                  whileHover={{ scale: 1.06 }} whileTap={{ scale: 0.93 }}
                  onClick={addItem}
                  className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-teal-600 text-white text-xs font-semibold"
                >
                  <MdAdd className="w-4 h-4" /> Add Item
                </motion.button>
              </div>
              <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
                {items.map((item, idx) => (
                  <motion.div key={item.id}
                    initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
                    className="bg-slate-50 dark:bg-slate-800 rounded-xl p-3 space-y-2 border border-slate-200 dark:border-slate-700"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Item {idx + 1}</span>
                      <button onClick={() => removeItem(item.id)} className="text-rose-400 hover:text-rose-600 transition-colors" aria-label="Remove item">
                        <MdDelete className="w-4 h-4" />
                      </button>
                    </div>
                    <input placeholder="Item name" value={item.name}
                      onChange={e => updateItem(item.id, 'name', e.target.value)}
                      className="w-full bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-2.5 py-1.5 text-sm text-slate-800 dark:text-slate-200 focus:ring-2 focus:ring-teal-500 outline-none"
                    />
                    <div className="grid grid-cols-3 gap-2">
                      <div>
                        <label className="block text-[10px] text-slate-400 mb-0.5">Qty</label>
                        <input type="number" min="1" value={item.quantity}
                          onChange={e => updateItem(item.id, 'quantity', parseInt(e.target.value) || 1)}
                          className="w-full bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-2 py-1.5 text-sm text-center focus:ring-2 focus:ring-teal-500 outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] text-slate-400 mb-0.5">Unit</label>
                        <input placeholder="pc" value={item.unit}
                          onChange={e => updateItem(item.id, 'unit', e.target.value)}
                          className="w-full bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-2 py-1.5 text-sm text-center focus:ring-2 focus:ring-teal-500 outline-none"
                        />
                      </div>
                      <div>
                        <label className="block text-[10px] text-slate-400 mb-0.5">Price</label>
                        <input type="number" min="0" step="0.01" value={item.price}
                          onChange={e => updateItem(item.id, 'price', parseFloat(e.target.value) || 0)}
                          className="w-full bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg px-2 py-1.5 text-sm text-center focus:ring-2 focus:ring-teal-500 outline-none"
                        />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
              <div className="mt-2 pt-3 border-t border-slate-200 dark:border-slate-700">
                {(() => {
                  const sub = items.reduce((s, i) => s + i.price * i.quantity, 0);
                  const tax = sub * taxRate / 100;
                  return (
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-slate-500">Estimated Total</span>
                      <span className="font-bold text-teal-600">
                        {currency} {(sub + tax).toFixed(2)}
                      </span>
                    </div>
                  );
                })()}
              </div>
            </div>
          )}

          {/* TAB: Customer */}
          {sidebarTab === 'customer' && (
            <div className="card--glass rounded-xl p-4 space-y-3">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Select Customer</label>
              <div className="relative">
                <select value={selectedCustomerId ?? ''}
                  onChange={e => setSelectedCustomerId(e.target.value ? parseInt(e.target.value) : null)}
                  className="w-full appearance-none bg-slate-100 dark:bg-slate-700 border-0 rounded-lg px-3 py-2 text-sm text-slate-800 dark:text-slate-200 pr-8 focus:ring-2 focus:ring-teal-500 outline-none"
                >
                  <option value="">— manual entry —</option>
                  {customers.map(c => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
                <MdArrowDropDown className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5 pointer-events-none" />
              </div>
              <div className="space-y-2.5">
                <FormField label="Name"    value={toName}    onChange={setToName} />
                <FormField label="Email"   value={toEmail}   onChange={setToEmail} type="email" />
                <FormField label="Phone"   value={toPhone}   onChange={setToPhone} type="tel" />
                <FormField label="Address" value={toAddress} onChange={setToAddress} multiline />
              </div>
            </div>
          )}
        </aside>

        {/* PREVIEW PANEL */}
        <main className="flex-1 min-w-0">
          <div className="overflow-x-auto">
            <Invoice
              ref={invoiceRef}
              invoiceType={invoiceType}
              pageDesign={pageDesign}
              invoiceNumber={invoiceNumber}
              date={date}
              dueDate={dueDate || undefined}
              from={{
                name: settings?.restaurant_name ?? 'POS',
                address: settings?.address ?? '',
                phone: settings?.phone ?? '',
                email: settings?.email ?? '',
                logo: settings?.logo ?? undefined,
              }}
              to={toParty}
              items={items}
              currency={currency}
              taxRate={taxRate}
              notes={notes || undefined}
              footer={footer || undefined}
            />
          </div>
        </main>
      </div>
    </PageLayout>
  );
}

// ---- Reusable small field component ----------------------------------------

function FormField({
  label, value, onChange, type = 'text', multiline = false,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  multiline?: boolean;
}) {
  const sharedClass =
    'w-full bg-slate-100 dark:bg-slate-700 border-0 rounded-lg px-3 py-2 text-sm text-slate-800 dark:text-slate-200 focus:ring-2 focus:ring-teal-500 outline-none';
  return (
    <div>
      <label className="block text-xs font-semibold text-slate-500 mb-1">{label}</label>
      {multiline ? (
        <textarea rows={2} value={value} onChange={e => onChange(e.target.value)}
          className={`${sharedClass} resize-none`}
        />
      ) : (
        <input type={type} value={value} onChange={e => onChange(e.target.value)}
          className={sharedClass}
        />
      )}
    </div>
  );
}
