---
name: wagtail-field-customizer
description: Add new fields to Wagtail page models, generate migrations, and update the admin. Use this when the user asks to add a field, change a model, or update Wagtail panels.
---
# Wagtail Field Customizer Skill

You are an expert in Wagtail model customization. Follow these steps precisely:

## Step 1: Identify the Page Model
- Ask the user which page model to modify (e.g., `HomePage`, `ArticlePage`).
- Use `grep -r "class $MODEL_NAME" .` to locate the file.

## Step 2: Define the New Field
- Determine the field type: `CharField`, `TextField`, `RichTextField`, `ImageField`, `ForeignKey`, `StreamField`.
- Add the field to the model definition with appropriate attributes (e.g., `blank=True`, `null=True`).

## Step 3: Update Wagtail Panels
- Add the field to `content_panels` or `promote_panels`.
- For `StreamField`, define a new block in the `blocks.py` file.

## Step 4: Generate and Apply Migrations
- Run `python manage.py makemigrations` and capture the output.
- Run `python manage.py migrate` and confirm success.

## Step 5: Update the Admin Template (if needed)
- If the field appears in the admin list view, update `list_display` in the model admin.

## Step 6: Test
- Open the Wagtail admin and verify the new field appears.
- Create a new page instance and populate the field.

## Step 7: Report
- Output the migration number and a summary of changes.