# LMS Demo — AI Prompt Catalog

> **Related Code**
> * **Domain:** AI prompts / site-specific
> * **Used by:** `applications/libs/ceptor-ai/src/ceptor_ai/customizer/`, `applications/lms-demo/plugins/`

Prompts the LMS Demo customizer feeds into the AI customizer endpoint:

<!-- markdownlint-disable -->
| Use case                          | Prompt template                                                                  |
|-----------------------------------|----------------------------------------------------------------------------------|
| Add course card                   | "Add a new course card titled `<title>` to the courses section on `/lms/`."       |
| Update course module              | "Append a new section to module `<module_id>` titled `<title>` with `<body>`." |
| Re-style profile dashboard       | "Apply the VResume portfolio tile style to `<profile section>`."                 |
<!-- markdownlint-restore -->

## See also

* [`../index.md`](../index.md) for site context.
* [`../shared_lms.md`](../shared_lms.md) for shared LMS conventions.
