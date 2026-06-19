# VResume Testing Suite - Quick Start

## 🚀 Get Started in 3 Steps

### Step 1: Setup
```bash
cd v1
make setup
```

### Step 2: Run Tests
```bash
make test
```

### Step 3: View Results
```bash
make test-reports
```

---

## 📋 Common Commands

### Testing
```bash
make test              # Run all tests (verbose)
make test-quick        # Run tests (quiet)
make test-url URL=...  # Test custom URL
```

### Data Management
```bash
make populate-data     # Add test data
make populate-data-clear  # Remove test data
```

### Reports
```bash
make test-reports      # Show latest reports
make clean-test-reports # Delete all reports
```

### Shortcuts
```bash
make t                 # = make test
make tq                # = make test-quick
make pd                # = make populate-data
make pdc               # = make populate-data-clear
```

---

## 🔍 What Gets Tested

✅ **6 Main Pages** (home, about, resume, portfolio, blog, contact)
✅ **2 Modal Endpoints** (project detail, blog detail)
✅ **2 Form Endpoints** (contact submit, newsletter subscribe)
✅ **3 Error Cases** (invalid tab, invalid project, invalid blog)
✅ **8 Form Validations** (missing fields, empty inputs)

**Total: 30+ tests**

---

## 📊 Test Reports

Reports are saved in `test_reports/` with timestamps:

```
test_reports/
├── test_report_20240509_103045.json
├── test_report_20240509_110230.json
└── test_report_20240509_115612.json
```

Each report includes:
- ✅ Test results (passed/failed)
- ⏱️ Performance metrics
- 📈 Response times
- 📝 Detailed test info

---

## 🛠️ Python Commands

```bash
# Run tests
python -m tests.runner

# With options
python -m tests.runner --base-url http://custom-url:8000
python -m tests.runner --verbose

# Populate data
python -m tests.data_populator

# Clear data
python -m tests.data_populator --clear
```

---

## 📚 Documentation

- **Quick Reference**: `tests/README.md`
- **Comprehensive Guide**: `tests/GUIDE.md`
- **Migration Guide**: `tests/MIGRATION.md`
- **This File**: `tests/QUICKSTART.md`

---

## ⚡ Development Workflow

```bash
# 1. Start development server
make dev

# 2. In another terminal, run tests
make test

# 3. Make changes to code

# 4. Run tests again
make test-quick

# 5. View reports
make test-reports
```

---

## 🐛 Troubleshooting

### Server not running?
```bash
make dev
```

### Need fresh test data?
```bash
make populate-data-clear
make populate-data
```

### Check system status?
```bash
make check
make status
```

---

## 📈 Performance Benchmarks

Expected response times:
- Tab views: 100-300ms
- Modal endpoints: 50-150ms
- Form submissions: 200-500ms
- Error cases: 10-50ms

---

## 🎯 Next Steps

1. Run `make setup` to initialize
2. Run `make test` to verify tests work
3. Read `tests/README.md` for details
4. Check `test_reports/` for results

---

## 💡 Tips

- Use `make test-quick` for faster feedback
- Use `make test` for detailed output
- Use `make test-url URL=...` to test other servers
- Check `test_reports/` for performance analysis
- Run `make populate-data` before testing

---

## 🔗 Related Commands

```bash
make dev              # Start development server
make setup            # Full project setup
make check            # Run Django checks
make shell            # Open Django shell
make migrate          # Run migrations
make static           # Collect static files
```

---

**Version**: 1.0.0
**Last Updated**: May 9, 2024

For more details, see the comprehensive guides in the `tests/` directory.
