# Migration Safety Guide

## Overview

This guide provides comprehensive procedures for ensuring migration safety during architectural refactoring, app renames, import path changes, and boundary enforcement. It covers verification procedures, rollback strategies, and quality assurance checks to prevent data loss and maintain system integrity.

## Core Safety Principles

### 1. Zero Data Loss Principle
- **Rule**: All migrations must preserve existing data
- **Implementation**: Use `AlterModelTable` to preserve physical table names
- **Verification**: Compare row counts before and after migration

### 2. Reversibility Principle
- **Rule**: All migrations must be reversible
- **Implementation**: Create reversible migration operations
- **Verification**: Test migration reversal with `migrate zero`

### 3. Atomicity Principle
- **Rule**: Migration operations must be atomic
- **Implementation**: Use database transactions
- **Verification**: Test migration failure scenarios

### 4. Dependency Ordering Principle
- **Rule**: Migrations must respect dependency ordering
- **Implementation**: Define explicit migration dependencies
- **Verification**: Run migration dependency checker

## Migration Safety Procedures

### 1. Pre-Migration Safety Checks

#### 1.1 Database Backup Procedure
```bash
# Create timestamped backup
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_pre_migration_${BACKUP_TIMESTAMP}.sql"

# PostgreSQL backup
pg_dump -U postgres -d your_database -F c -f ${BACKUP_FILE}

# SQLite backup
cp db.sqlite3 db.sqlite3.backup.${BACKUP_TIMESTAMP}

# Verify backup integrity
pg_restore --list ${BACKUP_FILE} | head -20
```

#### 1.2 Data Integrity Verification
```python
# data_integrity_check.py
from django.db import connection
from django.apps import apps

def verify_data_integrity():
    """Verify all foreign key relationships before migration."""
    with connection.cursor() as cursor:
        # Check foreign key constraints
        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY';
        """)
        foreign_keys = cursor.fetchall()
        print(f"Found {len(foreign_keys)} foreign key constraints")

    # Verify ContentType consistency
    from django.contrib.contenttypes.models import ContentType
    content_types = ContentType.objects.all()
    print(f"Found {content_types.count()} ContentType records")

    return True
```

#### 1.3 Migration Readiness Checklist
- [ ] Database backup completed and verified
- [ ] Foreign key constraints documented
- [ ] ContentType records documented
- [ ] Row counts recorded for all tables
- [ ] Test environment migration tested
- [ ] Rollback procedure documented
- [ ] Team notified of maintenance window
- [ ] Monitoring alerts configured

### 2. Migration Execution Safety

#### 2.1 App Rename Safety Procedure
```python
# accounts/migrations/0001_rename_app_label.py
from django.db import migrations

class Migration(migrations.Migration):
    """
    SAFETY FEATURES:
    1. Preserves table names with AlterModelTable
    2. Atomic operation within transaction
    3. Explicit dependency on original app's final migration
    4. Reversible operation
    """

    # SAFETY: Explicit dependency ensures proper ordering
    dependencies = [
        ('handlers', '0001_initial'),  # Last migration of original app
    ]

    operations = [
        # SAFETY: Preserves physical table names
        migrations.AlterModelTable(
            name='person',
            table='handlers_person',  # Original table name preserved
        ),
        migrations.AlterModelTable(
            name='certificate',
            table='handlers_certificate',
        ),
        # ... repeat for all models
    ]
```

#### 2.2 ContentType Update Safety Procedure
```python
# accounts/migrations/0002_update_contenttypes.py
from django.db import migrations

def update_contenttypes(apps, schema_editor):
    """
    SAFETY FEATURES:
    1. Uses historical models (apps.get_model)
    2. Atomic update within transaction
    3. Reversible with reverse function
    4. No data loss - only metadata update
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # SAFETY: Batch update within transaction
    updated = ContentType.objects.filter(app_label='handlers').update(app_label='accounts')

    print(f"Updated {updated} ContentType records")

def reverse_update_contenttypes(apps, schema_editor):
    """Reversible operation for rollback."""
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='accounts').update(app_label='handlers')

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_rename_app_label'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(
            update_contenttypes,
            reverse_update_contenttypes,
            # SAFETY: Atomic operation
            atomic=True
        ),
    ]
```

#### 2.3 Migration Execution with Safety Wrappers
```bash
#!/bin/bash
# safe_migration.sh

set -e  # Exit on error

echo "Starting safe migration procedure..."

# Step 1: Enter maintenance mode
python manage.py maintenance_mode on

# Step 2: Run migrations with transaction wrapper
echo "Running migrations..."
python manage.py migrate --plan  # Show migration plan first
python manage.py migrate --dry-run  # Dry run without changes

# Step 3: Execute migrations with error handling
if python manage.py migrate; then
    echo "Migrations completed successfully"

    # Step 4: Verify migration results
    python manage.py check --deploy
    python manage.py showmigrations

    # Step 5: Exit maintenance mode
    python manage.py maintenance_mode off

    echo "Migration completed successfully"
else
    echo "Migration failed. Initiating rollback..."

    # Step 6: Rollback on failure
    python manage.py migrate --plan  # Show current state
    python manage.py maintenance_mode off

    exit 1
fi
```

### 3. Post-Migration Verification

#### 3.1 Data Integrity Verification
```python
# post_migration_verification.py
from django.db import connection

def verify_post_migration_integrity():
    """Verify data integrity after migration."""

    # 1. Verify table names preserved
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name LIKE 'handlers_%';
        """)
        preserved_tables = cursor.fetchall()
        print(f"Preserved {len(preserved_tables)} handler tables")

        # Should still find handlers_* tables after rename
        assert len(preserved_tables) > 0, "Table names not preserved!"

    # 2. Verify ContentType updates
    from django.contrib.contenttypes.models import ContentType
    old_content_types = ContentType.objects.filter(app_label='handlers').count()
    new_content_types = ContentType.objects.filter(app_label='accounts').count()

    print(f"Old ContentTypes (handlers): {old_content_types}")
    print(f"New ContentTypes (accounts): {new_content_types}")

    assert old_content_types == 0, "Old ContentTypes still exist!"
    assert new_content_types > 0, "New ContentTypes not created!"

    # 3. Verify foreign key relationships
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND ccu.table_name LIKE 'handlers_%';
        """)
        foreign_keys = cursor.fetchall()

        # Foreign keys should still reference handlers_* tables
        assert len(foreign_keys) > 0, "Foreign keys broken!"

    return True
```

#### 3.2 Application Functionality Verification
```python
# functionality_verification.py
from django.test import TestCase
from django.apps import apps

class PostMigrationFunctionalityTest(TestCase):
    """Test application functionality after migration."""

    def test_model_instantiation(self):
        """Verify models can be instantiated with new app label."""
        try:
            # Try to get model with new app label
            Person = apps.get_model('accounts', 'Person')
            person = Person.objects.first()
            self.assertIsNotNone(person)
        except LookupError as e:
            self.fail(f"Model lookup failed: {e}")

    def test_foreign_key_relationships(self):
        """Verify foreign key relationships work."""
        from apps.accounts.models import Person
        from apps.lms.models import Enrollment

        # Create test data
        person = Person.objects.create(name="Test Person")
        enrollment = Enrollment.objects.create(
            person=person,
            course_id=1
        )

        # Verify relationship
        self.assertEqual(enrollment.person, person)
        self.assertIn(enrollment, person.enrollment_set.all())

    def test_admin_registration(self):
        """Verify admin site still works."""
        from django.contrib import admin
        from apps.accounts.models import Person

        # Check if model is registered with admin
        self.assertTrue(admin.site.is_registered(Person))

    def test_url_resolution(self):
        """Verify URLs still resolve correctly."""
        from django.urls import reverse

        # Test URL reversal
        try:
            url = reverse('admin:accounts_person_changelist')
            self.assertTrue(url.startswith('/admin/accounts/person/'))
        except Exception as e:
            self.fail(f"URL resolution failed: {e}")
```

#### 3.3 Performance Verification
```python
# performance_verification.py
import time
from django.db import connection
from django.core.management import call_command

def verify_performance():
    """Verify performance after migration."""

    # 1. Query performance
    start_time = time.time()

    from apps.accounts.models import Person
    persons = Person.objects.all()[:100]
    list(persons)  # Force evaluation

    query_time = time.time() - start_time
    print(f"Query time for 100 persons: {query_time:.3f}s")

    assert query_time < 1.0, f"Query performance degraded: {query_time:.3f}s"

    # 2. Migration rollback performance
    start_time = time.time()
    call_command('migrate', 'accounts', 'zero')
    rollback_time = time.time() - start_time

    print(f"Rollback time: {rollback_time:.3f}s")

    # 3. Re-migration performance
    start_time = time.time()
    call_command('migrate', 'accounts')
    remigration_time = time.time() - start_time

    print(f"Re-migration time: {remigration_time:.3f}s")

    return True
```

### 4. Rollback Procedures

#### 4.1 Emergency Rollback Procedure
```bash
#!/bin/bash
# emergency_rollback.sh

set -e

echo "Initiating emergency rollback..."

# Step 1: Stop application traffic
python manage.py maintenance_mode on

# Step 2: Rollback migrations in reverse dependency order
echo "Rolling back migrations..."
python manage.py migrate content zero
python manage.py migrate lms zero
python manage.py migrate accounts zero

# Step 3: Restore INSTALLED_APPS to old values
echo "Restoring old INSTALLED_APPS..."
# Manual step: Update settings.py to use old app names

# Step 4: Verify rollback
python manage.py check --deploy
python manage.py showmigrations

# Step 5: Restore from backup if needed
if [ -f "backup_pre_migration.sql" ]; then
    echo "Restoring from backup..."
    pg_restore -U postgres -d your_database -c backup_pre_migration.sql
fi

# Step 6: Restart application
python manage.py maintenance_mode off

echo "Emergency rollback completed"
```

#### 4.2 Gradual Rollback Procedure
```python
# gradual_rollback.py
from django.db import migrations

class Migration(migrations.Migration):
    """
    Gradual rollback migration.
    Reverses app rename in controlled manner.
    """

    dependencies = [
        ('accounts', '0002_update_contenttypes'),
    ]

    operations = [
        # Reverse ContentType update
        migrations.RunPython(
            lambda apps, schema_editor: apps.get_model(
                'contenttypes', 'ContentType'
            ).objects.filter(
                app_label='accounts'
            ).update(app_label='handlers'),
            lambda apps, schema_editor: apps.get_model(
                'contenttypes', 'ContentType'
            ).objects.filter(
                app_label='handlers'
            ).update(app_label='accounts'),
        ),

        # Reverse table rename
        migrations.AlterModelTable(
            name='person',
            table=None,  # Django will use default naming
        ),
        # ... repeat for all models
    ]
```

### 5. Quality Assurance Checklists

#### 5.1 Pre-Migration QA Checklist
- [ ] Database backup completed and verified
- [ ] Migration plan documented and reviewed
- [ ] Rollback procedure tested in staging
- [ ] Team notified of maintenance window
- [ ] Monitoring configured for migration events
- [ ] Performance baseline recorded
- [ ] Data integrity verified
- [ ] Test suite passes with migration applied

#### 5.2 Migration Execution QA Checklist
- [ ] Migration run in transaction
- [ ] Each step logged with timestamp
- [ ] Error handling configured
- [ ] Progress monitoring active
- [ ] Resource usage within limits
- [ ] No blocking operations detected
- [ ] Foreign key constraints preserved
- [ ] ContentType updates verified

#### 5.3 Post-Migration QA Checklist
- [ ] Data integrity verified
- [ ] Application functionality tested
- [ ] Performance compared to baseline
- [ ] All tests pass
- [ ] Admin interface functional
- [ ] URLs resolve correctly
- [ ] Search functionality works
- [ ] Reports generate correctly
- [ ] Monitoring alerts cleared

#### 5.4 Rollback QA Checklist
- [ ] Rollback procedure documented
- [ ] Rollback tested in staging
- [ ] Data preservation verified
- [ ] Application functional after rollback
- [ ] Performance acceptable after rollback
- [ ] All tests pass after rollback

### 6. Common Migration Issues and Solutions

#### 6.1 Issue: Foreign Key Constraint Violation
**Symptoms**: `django.db.utils.IntegrityError: update or delete on table violates foreign key constraint`
**Cause**: Migration tries to modify table referenced by foreign key
**Solution**:
```python
# Add dependency on referencing migration
dependencies = [
    ('referencing_app', 'migration_that_adds_fk'),
]

# Or temporarily drop constraint
operations = [
    migrations.RunSQL(
        "ALTER TABLE child_table DROP CONSTRAINT fk_constraint;",
        "ALTER TABLE child_table ADD CONSTRAINT fk_constraint "
        "FOREIGN KEY (parent_id) REFERENCES parent_table(id);"
    ),
]
```

#### 6.2 Issue: ContentType Inconsistency
**Symptoms**: `django.contrib.contenttypes.models.DoesNotExist: ContentType matching query does not exist`
**Cause**: ContentType records not updated during app rename
**Solution**:
```python
# Ensure ContentType migration runs
operations = [
    migrations.RunPython(
        update_contenttypes,
        reverse_update_contenttypes,
    ),
]

# Update ContentType in post_migration signal
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def update_contenttypes_post_migration(sender, **kwargs):
    if sender.name == 'accounts':
        ContentType = kwargs['apps'].get_model('contenttypes', 'ContentType')
        ContentType.objects.filter(app_label='handlers').update(app_label='accounts')
```

#### 6.3 Issue: Circular Migration Dependency
**Symptoms**: `django.db.migrations.exceptions.CircularDependencyError`
**Cause**: Two migrations depend on each other
**Solution**:
```python
# Break circular dependency with swappable dependency
dependencies = [
    ('other_app', '0001_initial'),
    # Instead of ('other_app', '0002_migration'),
    # Use:
    ('other_app', '__first__'),
]

# Or create third migration that both depend on
```

#### 6.4 Issue: Table Already Exists
**Symptoms**: `django.db.utils.ProgrammingError: relation "table_name" already exists`
**Cause**: Migration tries to create table that already exists
**Solution**:
```python
# Use AlterModelTable instead of CreateModel
operations = [
    migrations.AlterModelTable(
        name='model_name',
        table='existing_table_name',
    ),
]

# Or check if table exists first
from django.db import connection

def forward(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_name=%s)", ['table_name'])
        exists = cursor.fetchone()[0]

    if not exists:
        # Create table
        pass
```

### 7. Automated Safety Tools

#### 7.1 Migration Safety Validator
```python
# migration_safety_validator.py
import os
import re
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Validate migration safety'

    def handle(self, *args, **options):
        migrations_dir = 'apps/accounts/migrations/'

        for filename in os.listdir(migrations_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                path = os.path.join(migrations_dir, filename)
                with open(path, 'r') as f:
                    content = f.read()

                # Check for safety patterns
                safety_checks = [
                    ('AlterModelTable', 'Table names preserved'),
                    ('RunPython atomic=True', 'Atomic Python operations'),
                    ('dependencies', 'Explicit dependencies'),
                    ('reverse_code', 'Reversible operations'),
                ]

                for pattern, description in safety_checks:
                    if re.search(pattern, content):
                        self.stdout.write(f"✓ {filename}: {description}")
                    else:
                        self.stdout.write(f"✗ {filename}: Missing {description}")
```

#### 7.2 Boundary Checker
```bash
#!/bin/bash
# boundary_checker.sh

echo "Checking boundary violations..."

# Run import-linter
import-linter --config .importlinter

# Check for grep-test-only violations
echo "Checking grep-test-only violations..."
grep -r "from django_fusion\|import django_fusion" --include="*.py" . \
    | grep -v "test" \
    | grep -v ".pyc" \
    | wc -l

# Check for project-specific imports in crafts_ai
echo "Checking rseal-no-projects violations..."
grep -r "from apps\|import apps" venv/libs/crafts-ai/src/crafts_ai/ \
    | grep -v ".pyc" \
    | wc -l
```

#### 7.3 Performance Monitor
```python
# performance_monitor.py
import time
import psutil
from django.db import connection

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}

    def measure_migration(self, migration_name):
        """Measure migration performance."""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        # Execute migration
        # ... migration code ...

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        self.metrics[migration_name] = {
            'duration': end_time - start_time,
            'memory_delta': end_memory - start_memory,
            'queries': len(connection.queries),
        }

        return self.metrics[migration_name]
```

### 8. Best Practices Summary

#### 8.1 Migration Design Best Practices
1. **Always preserve table names** with `AlterModelTable`
2. **Always update ContentType records** during app renames
3. **Always make migrations reversible**
4. **Always use transactions** for data migrations
5. **Always define explicit dependencies**
6. **Always test migrations in staging first**
7. **Always backup before migration**
8. **Always monitor during migration**

#### 8.2 Safety Verification Best Practices
1. **Verify data integrity** before and after
2. **Verify foreign key constraints**
3. **Verify ContentType consistency**
4. **Verify application functionality**
5. **Verify performance characteristics**
6. **Verify rollback procedure**
7. **Verify monitoring alerts**
8. **Verify team communication**

#### 8.3 Rollback Best Practices
1. **Always have rollback procedure documented**
2. **Always test rollback in staging**
3. **Always preserve backup points**
4. **Always monitor during rollback**
5. **Always verify after rollback**
6. **Always communicate rollback status**
7. **Always analyze rollback causes**
8. **Always update procedures based on learnings**

### 9. Appendices

#### 9.1 Migration Safety Command Reference
```bash
# Safety verification commands
python manage.py check --deploy
python manage.py showmigrations
python manage.py migrate --plan
python manage.py migrate --dry-run
python manage.py makemigrations --check
python manage.py sqlmigrate app_label migration_name

# Backup commands
pg_dump -U postgres -d database -F c -f backup.sql
pg_restore -U postgres -d database -c backup.sql

# Monitoring commands
tail -f migration.log
watch -n 1 'ps aux | grep migration'
```

#### 9.2 Emergency Contact Procedures
1. **Database Administrator**: [DBA Contact]
2. **Application Lead**: [App Lead Contact]
3. **Infrastructure Team**: [Infra Contact]
4. **On-call Engineer**: [On-call Contact]
5. **Project Manager**: [PM Contact]

#### 9.3 Glossary
- **AlterModelTable**: Django migration operation that changes table metadata without moving data
- **ContentType**: Django's content types framework for generic relationships
- **Foreign Key Constraint**: Database constraint enforcing referential integrity
- **Migration Atomicity**: Property where migration either fully succeeds or fully fails
- **Migration Reversibility**: Property where migration can be undone without data loss
- **Table Preservation**: Technique of keeping physical table names unchanged during app rename

---

## Related Documentation

- [MIGRATION_GUIDE.md](../deployment/MIGRATION_GUIDE.md) - Import path changes and app renames
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture and boundaries
- [BOUNDARY_ENFORCEMENT_GUIDE.md](./BOUNDARY_ENFORCEMENT_GUIDE.md) - Boundary rule enforcement
- [.importlinter](../../.importlinter) - Import boundary configuration

## Version History

- **v1.0.0**: Initial migration safety guide
- **v1.1.0**: Added emergency procedures and monitoring
- **v1.2.0**: Added automated safety tools and best practices

## Feedback and Improvements

Please report issues, suggestions, or improvements to the architecture team. This guide should be continuously updated based on migration experiences and lessons learned.
