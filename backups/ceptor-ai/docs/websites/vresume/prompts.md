# VResume — AI Prompt Catalog

> **Related Code**
> * **Domain:** AI prompts / site-specific
> * **Used by:** `applications/libs/ceptor-ai/src/ceptor_ai/customizer/`, `applications/VResume/plugins/`

Prompts the VResume customizer feeds into the AI customizer endpoint:

<!-- markdownlint-disable -->
| Use case                  | Prompt template                                                                  |
|---------------------------|----------------------------------------------------------------------------------|
| Add portfolio item        | "Add a new portfolio project titled `<title>` to the VResume portfolio list, with tags `<tagset>`." |
| Tag project               | "Tag `<project>` with `<tagset>`. Use existing tags where possible." |
| Update bio                | "Update the author bio on `<page>` to mention `<new_fact>`." |
| Add blog section          | "Insert a `Newsletter Signup` section into the blog landing template using the canonical `{% comp %}` form." |
<!-- markdownlint-restore -->

## See also

* [`../index.md`](../index.md) for site context.
* [`../../../docs/ai/prompt_tasks.md`](../../../docs/ai/prompt_tasks.md) for shared AI prompt conventions.
