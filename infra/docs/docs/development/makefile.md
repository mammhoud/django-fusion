# Makefile Commands

VResume uses a comprehensive `Makefile` to automate development tasks. This ensures consistency across environments and simplifies the workflow for developers.

## 🚀 Getting Started

If you are setting up the project for the first time:

```bash
make setup
```
This command handles dependency installation, database migrations, static file collection, and initial data population.

## 🛠️ Common Commands

| Command | Description |
|---------|-------------|
| `make dev` | Starts the Django development server (Uvicorn). |
| `make r` | **Shortcut**: Alias for `make dev`. |
| `make build` | **All-in-one**: Clean migrations, setup, and populate data. |
| `make menu` | **Interactive Menu**: A guided CLI interface for all major tasks. |
| `make migrate` | Synchronizes the database with current models. |
| `make superuser` | Creates an administrative user for the Wagtail CMS. |
| `make static` | Collects all static files into the `static_root`. |

## 🎨 Frontend Commands

VResume's frontend is powered by Node.js and Tailwind CSS.

- `make frontend-install`: Install npm dependencies.
- `make frontend-watch`: Start development server with hot-reloading for styles and scripts.
- `make frontend-production`: Build optimized production assets.
- `make css-purge`: Manually trigger PurgeCSS to remove unused styles.

## 🧪 Testing & Quality

- `make test`: Run the full suite of automated tests.
- `make lint`: Check code for style and import issues.
- `make fix`: Automatically fix common linting errors.
- `make check`: Run Django's system check framework.

## 🗃️ Database Management

> [!CAUTION]
> These commands are destructive. Use with care.

- `make reset-db`: Deletes the database and all migrations, then restarts from scratch.
- `make populate-data`: Populates the database with fresh sample content.
- `make populate-data-clear`: Wipes all sample content from the database.

## 📖 Documentation

- `make docs`: Build the documentation site.
- `make docs-serve`: Serve documentation locally at [http://localhost:8000](http://localhost:8000).

---

## ⌨️ Shortcuts

For faster typing, many commands have short aliases:
- `make s` → setup
- `make d` → dev
- `make r` → run/dev
- `make build` → clean + setup + populate
- `make m` → migrate
- `make t` → test
- `make su` → superuser
- `make pd` → populate-data
