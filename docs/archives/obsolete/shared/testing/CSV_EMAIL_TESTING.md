# CSV-Based Email Testing System

## Overview
The CSV-based email testing system allows you to send test emails to addresses listed in a CSV file with role-based templates. This system integrates with the existing email infrastructure and provides delivery tracking.

## Features
- **CSV Parsing**: Reads email addresses and roles from CSV files
- **Role-Based Templates**: Different email templates for different user roles
- **Delivery Tracking**: Tracks email delivery status and performance
- **Bulk Operations**: Supports bulk email sending from CSV files
- **Results Export**: Exports test results to JSON format

## CSV Format
The CSV file should have the following columns:
- `email`: Recipient email address (required)
- `role`: User role (optional, defaults to 'default')

Example CSV (`test_email.csv`):
```csv
email,role
m.ezzat.mi0@gmail.com,admin
m.ezzat.mi1@gmail.com,admin/supervisor
test@example.com,supervisor
user@example.com,user
```

## Available Roles and Templates
- `admin`: Uses `admin_test.html` template
- `admin/supervisor`: Uses `admin_supervisor_test.html` template
- `supervisor`: Uses `supervisor_test.html` template
- `default`: Uses `test_email.html` template (fallback for all other roles)

## Usage

### Basic Usage
```bash
python manage.py test_email_csv --csv test_email.csv
```

### Dry Run (Test without sending)
```bash
python manage.py test_email_csv --csv test_email.csv --dry-run
```

### Custom Template Directory
```bash
python manage.py test_email_csv --csv test_email.csv --template-dir templates/emails
```

### Custom Sender Email
```bash
python manage.py test_email_csv --csv test_email.csv --from-email sender@example.com
```

### Save Results to Custom File
```bash
python manage.py test_email_csv --csv test_email.csv --output results.json
```

## Database Models
The system creates two database models for tracking:

### CSVEmailTest
Tracks individual email tests with:
- Recipient email and role
- Email subject and template used
- Delivery status (pending, sent, failed, skipped)
- Error messages (if any)
- Performance metrics (send duration)

### CSVEmailTestBatch
Tracks batch email tests with:
- Batch ID and CSV file path
- Total emails, sent count, failed count
- Success rate calculation
- Timestamps and results file path

## Email Templates
Templates are located in `apps/templates/emails/`:
- `test_email.html`: Default template for all roles
- `admin_test.html`: Template for admin role
- `admin_supervisor_test.html`: Template for admin/supervisor role
- `supervisor_test.html`: Template for supervisor role

## Template Variables
All templates have access to these variables:
- `email`: Recipient email address
- `role`: User role
- `site_name`: Site name from settings
- `site_url`: Site URL from settings
- `current_date`: Current date
- `support_email`: Support email from settings

## Results Output
Results are saved in JSON format with:
- Total emails processed
- Successfully sent count
- Failed count
- Skipped count
- Detailed information for each email
- Performance metrics

## Integration with Existing System
The CSV email testing system integrates with:
- Existing email infrastructure in `apps/handlers/registration/emails.py`
- Django's email sending system
- Role-based access control system
- Template rendering system

## Testing
To test the CSV email functionality:
1. Create a CSV file with test email addresses
2. Run the management command with `--dry-run` first
3. Check the results in the output JSON file
4. Run actual email tests when ready

## Example Workflow
```bash
# 1. Create test CSV
echo "email,role" > test.csv
echo "test1@example.com,admin" >> test.csv
echo "test2@example.com,supervisor" >> test.csv

# 2. Dry run test
python manage.py test_email_csv --csv test.csv --dry-run

# 3. Actual test
python manage.py test_email_csv --csv test.csv --output test_results.json

# 4. Check results
cat test_results.json
```

## Requirements
- Django 3.2+
- Python 3.8+
- Email backend configured in Django settings
- CSV file with proper format

## Notes
- The system uses Django's built-in email sending
- Templates support HTML and plain text fallback
- Delivery tracking is stored in the database
- Results can be exported for analysis
- Role-based templates allow for personalized emails
