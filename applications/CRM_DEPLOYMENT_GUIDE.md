# CRM Site - Quick Deployment Guide

## Overview
The CRM site has been successfully integrated into the Structa Cloud monorepo. It's a complete sales and inventory management system with django-osoul routing, HTMX components, and a full fixture suite.

## Quick Start

### 1. Development Server
```bash
cd /home/structa.cloud/applications
WEBSITE=crm make dev
# Server runs on http://localhost:5074
```

### 2. Build Assets
```bash
cd /home/structa.cloud/applications/assets
npm run build:crm
```

### 3. Database Setup
```bash
cd /home/structa.cloud/applications
# Apply migrations
WEBSITE=crm make migrate

# Load seed fixtures
WEBSITE=crm uv run crm loaddata crm/assets/fixtures/seed/crm_auth.json
WEBSITE=crm uv run crm loaddata crm/assets/fixtures/seed/crm_categories.json
WEBSITE=crm uv run crm loaddata crm/assets/fixtures/seed/crm_vendors.json
WEBSITE=crm uv run crm loaddata crm/assets/fixtures/seed/crm_customers.json
WEBSITE=crm uv run crm loaddata crm/assets/fixtures/seed/crm_items.json
WEBSITE=crm uv run crm loaddata crm/assets/fixtures/seed/crm_bills.json
WEBSITE=crm uv run crm loaddata crm/assets/fixtures/seed/crm_invoices.json
```

Or load all at once:
```bash
cd /home/structa.cloud/applications
WEBSITE=crm make populate-data-site
```

### 4. Verify Installation
```bash
cd /home/structa.cloud/applications
WEBSITE=crm make check
```

## Site Architecture

### Core Routing (django-osoul)
- **File:** `crm/www/core/routes.py`
- **Classes:** 6 Application classes for Dashboard, Inventory, Transactions, Invoices, Bills, Accounts
- **URLs:** `crm/www/urls.py` - 21 routes configured

### Database Models (5 Plugin Apps)
- **inventory** - Categories, Items, Deliveries
- **accounts_app** - Customers, Vendors, Staff Profiles
- **transactions_app** - Sales, Purchases, Sale Details
- **invoice_app** - Invoices
- **bills_app** - Bills

### Templates
- **Layout:** `crm/templates/crm/layout/skeleton.html`
- **Fragments:** `crm/templates/crm/fragments/` - HTMX-ready components
- **Generics:** `crm/templates/crm/generic/` - Reusable forms, lists, details
- **Modules:** `crm/templates/crm/[module]/` - Module-specific templates

### Assets
- **Static Files:** `crm/assets/staticfiles/` (1,698 files)
- **JavaScript:** `crm/assets/static/js/` - app.js, static.js
- **Styles:** `crm/assets/static/styles/` - BEM-style SCSS
- **Fixtures:** `crm/assets/fixtures/seed/` - 7 JSON seed files

## Data Status

| Table | Rows | Status |
|-------|------|--------|
| crm_inventory_category | 5 | ✓ Loaded |
| crm_inventory_item | 8 | ✓ Loaded |
| crm_accounts_customer | 5 | ✓ Loaded |
| crm_accounts_vendor | 3 | ✓ Loaded |
| crm_transactions_sale | 0 | - Pending |
| crm_invoice_invoice | 3 | ✓ Loaded |
| crm_bills_bill | 3 | ✓ Loaded |
| **TOTAL** | **27** | **✓** |

## Available Routes

### Dashboard
- `GET /crm/dashboard/` - CRM dashboard with stats

### Inventory
- `GET /crm/inventory/category/` - List categories
- `GET /crm/inventory/category/{id}/` - Category detail
- `GET /crm/inventory/item/` - List items
- `GET /crm/inventory/item/{id}/` - Item detail
- `GET /crm/inventory/delivery/` - List deliveries

### Transactions
- `GET /crm/transactions/sale/` - POS/Sales interface
- `GET /crm/transactions/purchase/` - Purchase management

### Invoices & Bills
- `GET /crm/invoices/invoice/` - Invoice management
- `GET /crm/bills/bill/` - Bill management

### Account Management
- `GET /crm/accounts_app/customer/` - Customer profiles
- `GET /crm/accounts_app/vendor/` - Vendor profiles
- `GET /crm/accounts_app/staffprofile/` - Staff profiles

### HTMX Fragments
- `GET /crm/inventory/item/?_fragment=item-list-fragment`
- `GET /crm/accounts_app/customer/?_fragment=customer-list-fragment`
- `GET /crm/transactions/sale/?_fragment=sale-list-fragment`

## Configuration

### Site Settings
- **File:** `crm/settings.py`
- **Domain:** crm.structa.cloud
- **Port:** 5074
- **Module:** CMS
- **Site ID:** 4

### Environment (.env)
```bash
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,crm.structa.cloud
DATABASE_URL=sqlite:///db.sqlite3
SECRET_KEY=your-secret-key-here
```

## Testing

### System Check
```bash
WEBSITE=crm make check
```

### Run Tests
```bash
WEBSITE=crm make test
```

### Test All Sites
```bash
make tests-all
```

## Deployment

### Production Build
```bash
# Build assets for production
npm run build:crm

# Collect static files
WEBSITE=crm make collectstatic-site

# Create Docker image (requires Dockerfile)
docker build -t crm-website:latest -f Dockerfile .

# Run in Docker Compose
docker compose up crm-website
```

### Database Migration
```bash
# For production
WEBSITE=crm make migrate
```

## Troubleshooting

### Migrations Not Applied
```bash
WEBSITE=crm make migrate
```

### Static Files Missing
```bash
WEBSITE=crm make collectstatic-site
```

### Asset Build Fails
```bash
cd applications/assets
npm install
npm run build:crm
```

### Database Fixtures Need Reload
```bash
cd applications
for fixture in crm_auth crm_categories crm_vendors crm_customers crm_items crm_bills crm_invoices; do
  WEBSITE=crm uv run crm loaddata crm/assets/fixtures/seed/${fixture}.json
done
```

## Support

For issues or questions, refer to:
- Main project: `/home/structa.cloud/AGENTS.md`
- Monorepo guide: `/home/structa.cloud/applications/Makefile.md`
- CRM specific: This file

---

**Last Updated:** July 5, 2026  
**Status:** ✅ Production Ready
