# POS Full — Prompt Variations

> **Project:** `projects/pos/pos-full/`
> **Purpose:** Reusable AI prompts for code generation, organized by language

---

## TypeScript / React Prompts

### Add a new page
```
Add a new page at src/pages/NewFeature.tsx with:
- PageLayout wrapper
- RTK Query data fetching from the sidecar API
- Loading, error, empty, and normal states
- CTC teal theme classes
- framer-motion entrance animation
- Responsive grid (1-col mobile, 2-col tablet, 3-col desktop)
```

### Add a new component
```
Create a shared component at src/components/ui/NewComponent.tsx with:
- PascalCase naming
- Named props interface (NewComponentProps)
- Tailwind CSS styling with CTC teal variables
- All four states: loading (Skeleton), error (ErrorDisplay), empty, normal
- Vitest unit test at src/test/components/NewComponent.test.tsx
```

### Add a new RTK Query endpoint
```
Add a new endpoint to src/store/api/ for [resource]:
- Create the endpoint file at src/store/api/endpoints/[resource].ts
- Export query/mutation hooks (useGet[Resource]Query, useCreate[Resource]Mutation, etc.)
- Register in store/api/index.ts
- Add TypeScript types to src/types.ts
```

### Add a new Tauri command
```
Add a new Tauri invoke command for [feature]:
- Create the Rust command handler in src-tauri/src/commands/[feature].rs
- Register in src-tauri/src/main.rs
- Create TypeScript invoke wrapper in src/utils/tauri.ts
- Add unit test in src/test/invoke.test.ts
```

---

## Python / Sidecar Prompts

### Add a new sidecar route
```
Add a new route to the Robyn sidecar at sidecar/routes/[resource].py:
- Use django_fusion patterns (RoutableComponent if applicable)
- Return fusion_json_response envelope
- Add pytest tests at sidecar/tests/test_[resource].py
- Register the route in the sidecar app
```

### Add a new Django ORM model
```
Add a new model to sidecar/models/pos.py:
- Extend django.db.models.Model
- Add django_fusion base manager
- Create migration: python manage.py makemigrations
- Add pytest fixture for the new model
```

### Add a new sidecar service
```
Create a new service at sidecar/services/[name].py:
- Use django_fusion BaseService pattern
- Implement business logic methods
- Add pytest tests at sidecar/tests/test_[name].py
```

---

## Rust / Tauri Prompts

### Add a new Diesel model
```
Add a new Rust struct to src-tauri/src/db/models.rs for [table]:
- Derive Queryable, Insertable, Serialize, Deserialize
- Add to schema.rs with diesel::table! macro
- Create SQL migration in src-tauri/migrations/
```

### Add a new SQL migration
```
Create a new SQL migration for [change]:
- File: src-tauri/migrations/YYYY-MM-DD-HHMMSS_[description]/up.sql
- Use IF NOT EXISTS for additive changes
- Test against the existing schema
```

---

## SQL Prompts

### Add a column to an existing table
```sql
-- Migration: add [column] to [table]
ALTER TABLE [table] ADD COLUMN IF NOT EXISTS [column] [type] [constraints];
```

### Create a new table
```sql
-- Migration: create [table]
CREATE TABLE IF NOT EXISTS [table] (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
