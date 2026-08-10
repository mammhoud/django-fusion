#!/usr/bin/env python3
"""Migrate BEM input classes -> FlyonUI classes across forge-pos.

Order matters (longest/most-specific first).
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'src'

FILES = [
    'components/display/ThemePreviewModal.tsx',
    'components/notes/PrepStepsEditor.tsx',
    'components/ui/DataTable.tsx',
    'components/ui/DatePicker.tsx',
    'components/ui/SearchInput.tsx',
    'pages/admin/About.tsx',
    'pages/admin/EmployeeSchedule.tsx',
    'pages/admin/Employees.tsx',
    'pages/admin/Notes.tsx',
    'pages/admin/Payroll.tsx',
    'pages/admin/Roles.tsx',
    'pages/admin/Settings.tsx',
    'pages/analytics/Reports.tsx',
    'pages/analytics/TaxReports.tsx',
    'pages/customers/Customers.tsx',
    'pages/customers/Suppliers.tsx',
    'pages/kitchen/Inventory.tsx',
    'pages/kitchen/KitchenDisplay.tsx',
    'pages/kitchen/Recipes.tsx',
    'pages/pos/ProductManager.tsx',
    'pages/pos/Sale.tsx',
    'pages/pos/Transactions.tsx',
]

REPLACEMENTS = [
    # Combined field+modifier classes first (most specific)
    ('input__field input__field--select', 'select'),
    ('input__field input__field--textarea', 'textarea'),
    ('input__field--select', 'select'),
    ('input__field--textarea', 'textarea'),
    ('input__label input__label--sm', 'label-text'),
    ('input__label--required', 'label-text'),
    ('input__label', 'label-text'),
    ('input__message', 'helper-text'),
    ('input__wrapper', 'field__wrapper'),
    # Wrapper div class renames (BEM .input -> .field)
    ("`input ${", "`field ${"),
    ("'input--error'", "'field--error'"),
    ('className="input ', 'className="field '),
    ('className="input"', 'className="field"'),
    # Wrapper modifiers
    ('input--error', 'field--error'),
    ('input--success', 'field--success'),
    ('input--sm', 'field--sm'),
    ('input--lg', 'field--lg'),
    ('input--ghost', 'field--ghost'),
    # Field element class (must run after all --select/--textarea combos)
    ('input__field', 'input'),
    ('input__icon', 'field__icon'),
]

def main() -> None:
    total = 0
    for rel in FILES:
        p = ROOT / rel
        if not p.exists():
            print(f'MISSING: {rel}')
            continue
        txt = p.read_text(encoding='utf-8')
        orig = txt
        for old, new in REPLACEMENTS:
            txt = txt.replace(old, new)
        n = orig.count('input__') - txt.count('input__')
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            print(f'{rel}: {orig.count("input__") - txt.count("input__")} swaps (field left: {txt.count("input__field")})')
        else:
            print(f'{rel}: no changes')
        total += max(0, orig.count('input__') - txt.count('input__'))
    print(f'TOTAL input__ replacements: {total}')

if __name__ == '__main__':
    main()
