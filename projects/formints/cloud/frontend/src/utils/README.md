# 📁 POS-KO Utilities (`src/utils/`)

> **Related Names:** `utils`, `PDF`, `Excel`, `export`, `invoice`, `jspdf`, `xlsx`, `report generation`
> **Tags:** #utils #pdf #excel #invoice #export

2 utility modules for PDF/Excel export and invoice generation.

```
utils/
├── export.ts            # 🟢 PDF/Excel report export
└── invoicePdf.ts        # 🟢 Invoice PDF generation (jsPDF)
```

## Customization Tags

| Module | Tag | How to customize |
|--------|-----|-----------------|
| `export.ts` | 🟢 `customizable` | Add export formats, change styling |
| `invoicePdf.ts` | 🟢 `customizable` | Change invoice layout, branding, fields |

## export.ts

Exports data in PDF (via jsPDF) or Excel (via xlsx) format:

```typescript
import { exportToPDF, exportToExcel } from '../utils/export';

// Export sales report
await exportToPDF(sales, 'Sales Report', columns);
await exportToExcel(sales, 'Sales Report', columns);
```

Used by pages: `Reports.tsx`, `Analytics.tsx`, `Transactions.tsx`, `Payroll.tsx`, `TaxReports.tsx`.

## invoicePdf.ts

Generates downloadable invoice PDFs using jsPDF:

```typescript
import { generateInvoicePDF } from '../utils/invoicePdf';

generateInvoicePDF({
  sale: { id: 42, total_amount: 45.50, ... },
  items: [{ product_name: 'Latte', quantity: 2, unit_price: 5.50 }],
  settings: { restaurant_name: 'My Cafe', tax_rate: 15 },
});
```

## Dependencies

| Package | Purpose |
|---------|---------|
| `jspdf` | PDF generation |
| `xlsx` | Excel export |

## Reference

- [Reports Page →](../pages/Reports.tsx)
- [Invoice Renderer →](invoicePdf.ts)
- [Dependencies →](../../docs/packages.md)
