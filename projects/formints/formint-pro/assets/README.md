# Pro asset boundary

Shared Formint assets are owned by [`../../assets/shared/`](../assets/shared/)
(the product-level registry). This directory is intentionally kept as the Pro
edition boundary for future Pro-only source assets; it is not a duplicate
asset store.

- Import shared frontend assets through `@formints-assets`.
- Django collects shared backend files through `FORMINT_SHARED_ASSETS` and
  keeps generated output in the Pro server `STATIC_ROOT`.
- Keep Pro-only assets here only when their content or runtime contract is not
  shared by another edition.
