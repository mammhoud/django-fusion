export type ExportResource = 'products' | 'sales' | 'customers' | 'inventory';
export type ExportFormat = 'csv' | 'json';

export function exportUrl(baseUrl: string, resource: ExportResource, format: ExportFormat = 'csv'): string {
  const root = baseUrl.replace(/\/$/, '');
  return format === 'json'
    ? `${root}/export/${resource}.csv?format=json`
    : `${root}/export/${resource}.csv`;
}
