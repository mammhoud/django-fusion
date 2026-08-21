# Merge the Projects page into the Products catalog

Status: accepted

The site had two overlapping pages — Products (the commercial catalog) and Projects
(the monorepo inventory) — with duplicated content on both render roads. We merged
them into a single catalog: `/products/` now renders the data-driven product cards
**and** the repo project grid, `/projects/` permanently 301-redirects to `/products/`,
and the `ProjectsPage` model was deleted via migration 0012 (mirroring the earlier
`/company/` → `/about/` merge).

Why: the backend road already carried the project grid on `/products/`, so the frontend
road simply caught up; one document for the full inventory is easier to navigate, and
one fewer nav item keeps the header at the 80px single-line standard. Considered and
rejected: keeping both pages cross-linked (duplication returns), and dropping Products
in favor of Projects (the catalog is the commercial front door — it must win).

Consequences: editors create `ProductPage` children for the catalog and edit the project
inventory as blocks on the Products page; any legacy link to `/projects/` now lands on
the catalog via the redirect.
