---
Object type: Note
Tags: notes, journal, origin, startup, learning
Status: Draft
Author: people/me.md
---

# Start-Up Journal — Working Notes

> **Description:** Raw, working notes from the start of the project. These are unfiltered capture notes; the polished narrative lives in the story, and the outcomes live on the achievement board.

---

## How it started

- Started with **Django** and quickly implemented a few **small sites** to learn by doing.
- Explored complementary frontend stacks — **htmx** and **Alpine.js** — to keep the frontend lightweight and server-driven.
- Moved into **small WebSocket apps** and completed several of them, learning real-time communication.

## Scalability notes

- Studied what actually makes an app scalable — especially at the **database** layer.
- Added **multi-tenancy** at the database level so one deployment can serve many customers.
- Handled **user registration and OAuth** with the **django-allauth** package.

## Backend and AI notes

- Django became the integrated **backend**, exposing data through **API packages**.
- Adopted an **AI stack** and **agentic development**, including **agents** and **MCP workflows**.

## Product building sequence

1. **Small LMS** first.
2. **Website pages** for marketing and company presence.
3. **CRM** — started with an admin-panel-backed version, then a full CRM with a complete frontend and custom themes.
4. **Complete LMS** with full registration.
5. **Agents and MCP workflows** layered on top.

## django-fusion

- Built the **django-fusion** package to make component requests easier and uniform.
- A component can contain **data**, a **table**, an **htmx request**, or **server-sent events (SSE)**.
- Components can be added to a project **separated as backend and frontend**.
- Used it to build the **POS**, the **LMS**, and the **company website pages**.

## CMS and AI notes

- Integrated **Wagtail as a CMS** into each website; every page has manageable content.
- **Flexible AI** can change a component, its fields, data flow, and design — making the development cycle fast.

## Platform notes

- The **POS** gained a **desktop app** built with **Tauri** and **cloud** integration.
- A dedicated **frontend project** with a related, familiar tech stack.
- Wrote full **documentation** for the projects.
- Set up **workspace development on the server** as a coding workspace using **Coder**.

---

## Related

- → `../starting-the-project.md` — Polished narrative
- → `../../goals/achievement-board.md` — Outcomes
- → `../../plans/startup-planner.md` — Strategy
- → `../../objects/story.md` — Story object type
