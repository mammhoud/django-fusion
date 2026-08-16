import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import Card from '../../../components/ui/Card';
import PageLayout from '../../../components/layout/PageLayout';
import RoleGate from '../../../components/RoleGate';
import { ReportMetadata } from '../../../types';

type Resource = 'products' | 'sales' | 'customers' | 'inventory';
type Format = 'csv' | 'json';

export default function Export() {
  const [resource, setResource] = useState<Resource>('products');
  const [format, setFormat] = useState<Format>('csv');
  const [result, setResult] = useState<ReportMetadata | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runExport = async () => {
    setIsExporting(true);
    setError(null);
    setResult(null);
    try {
      const metadata = await invoke<ReportMetadata>('export_resource', { resource, format });
      setResult(metadata);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      setIsExporting(false);
    }
  };

  const copyPath = async () => {
    if (result?.file_path) await navigator.clipboard?.writeText(result.file_path);
  };

  return (
    <PageLayout title="Export" background="bg-base-200/50">
      <div className="mx-auto max-w-3xl space-y-5">
        <div><h1 className="text-2xl font-bold text-base-content">Export data</h1><p className="text-sm text-base-content/55">Create an offline CSV or JSON snapshot from the local SQLite database.</p></div>
        <Card padding="lg">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <label className="form-control"><span className="label-text mb-2 font-medium">Resource</span><select className="select" value={resource} onChange={event => setResource(event.target.value as Resource)}><option value="products">Products</option><option value="sales">Sales</option><option value="customers">Customers</option><option value="inventory">Inventory</option></select></label>
            <label className="form-control"><span className="label-text mb-2 font-medium">Format</span><select className="select" value={format} onChange={event => setFormat(event.target.value as Format)}><option value="csv">CSV</option><option value="json">JSON</option></select></label>
          </div>
          <RoleGate permission="view:reports"><button type="button" className="btn btn-primary mt-5 gap-2" onClick={runExport} disabled={isExporting}><span className="ri-download-2-line" />{isExporting ? 'Exporting…' : `Export ${resource} as ${format.toUpperCase()}`}</button></RoleGate>
        </Card>
        {error && <div role="alert" className="alert alert-error">{error}</div>}
        {result && <Card padding="md" className="border-success/30 bg-success/5"><div className="flex items-start gap-3"><span className="ri-checkbox-circle-line ri-24px text-success" /><div className="min-w-0"><h2 className="font-semibold">Export ready</h2><p className="mt-1 break-all text-sm text-base-content/65">{result.file_path}</p><div className="mt-3 flex gap-2"><button className="btn btn-sm btn-outline" type="button" onClick={copyPath}>Copy file path</button><span className="badge badge-success badge-soft self-center">{result.format.toUpperCase()}</span></div></div></div></Card>}
      </div>
    </PageLayout>
  );
}
