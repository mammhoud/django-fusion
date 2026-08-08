# 📁 POS-KO Pages (`src/pages/`)

> **Related Names:** `pages`, `routes`, `views`, `screens`, `POS terminal`, `dashboard`, `inventory`, `employees`, `customers`, `reports`
> **Tags:** #pages #react #routes #pos-ko

22 route-level page components. Each maps to a route in `src/App.tsx`.

```
pages/
├── Auth.tsx               # 🟢 Login/setup screen
├── Home.tsx               # 🟢 Landing page + navigation tiles
├── Sale.tsx               # 🟢 POS terminal + cart
├── Analytics.tsx          # 🟢 Dashboard with Recharts
├── Transactions.tsx       # 🟢 Transaction history
├── Inventory.tsx          # 🟢 Stock management + alerts
├── ProductManager.tsx     # 🟢 Product & category CRUD
├── Customers.tsx          # 🟢 Customer CRM + loyalty points
├── Suppliers.tsx          # 🟢 Supplier management
├── Employees.tsx          # 🟢 Employee CRUD
├── Recipes.tsx            # 🟢 Recipe builder
├── Reports.tsx            # 🟢 PDF/Excel export
├── Settings.tsx           # 🟢 Restaurant configuration
├── KitchenDisplay.tsx     # 🟢 Kitchen order display
├── EmployeeSchedule.tsx   # 🟢 Shift scheduling
├── Payroll.tsx            # 🟢 Payslip management
├── ReceiptTemplates.tsx   # 🟢 Receipt designer
├── TaxReports.tsx         # 🟢 Tax summaries
├── Roles.tsx              # 🟢 Role-based access control
├── InvoicePage.tsx        # 🟢 Invoice viewer
├── SupportChat.tsx        # 🟢 Chat support widget
└── About.tsx              # 🟢 About page
```

## Customization Tags

| Tag | Pages |
|-----|-------|
| 🟢 `customizable` | All 22 pages — freely modify UI, logic, data fetching |

## Patterns

Every page follows the same structure:

```tsx
import { invoke } from '@tauri-apps/api/core';
import { useTranslation } from 'react-i18next';

export default function MyPage() {
  const { t } = useTranslation();
  const [data, setData] = useState<DataType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    invoke<DataType[]>('get_data').then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <TableSkeleton />;

  return (
    <div className="p-6">
      <h1 className="text-xl font-semibold">{t('myPage.title')}</h1>
      {/* page content */}
    </div>
  );
}
```

## Adding a New Page

1. Create `src/pages/MyNewPage.tsx`
2. Add route in `src/App.tsx` with `routeOrder` entry
3. Add nav link in `src/components/SideNav.tsx`
4. Add translations in `src/i18n/en.json`, `ar.json`, `fr.json`

## Reference

- [Customization Guide →](../../docs/customization-react.md)
- [Components →](../components/README.md)
- [Docs Index →](../../docs/README.md)
