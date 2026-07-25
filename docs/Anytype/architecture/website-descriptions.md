---
# yaml-language-server: $schema=schemas/milestone.schema.json
Object type:
    - Milestone
Backlinks:
    - product-development.md
    - startup-planner.md
    - project-guide.md
Creation date: "2024-07-12T10:00:00Z"
Created by:
    - mammhoud
Emoji: "\U0001F310"
id: bafyreifjdks34ejxqgfliw55kkixgyai6ci7tzy3rgyjmjmcy3qbtdldky
---
# Website & Application Descriptions   
   
# Website & Application Descriptions + Domain & Use Cases   
## Structa Cloud Platform – Complete Reference   
 --- 
## Table of Contents   
1. [Overview](.md)   
2. [Core Domain](.md)   
3. [Primary Websites & Applications](.md)   
    - 3.1 [CTC Research](.md)   
    - 3.2 [LMS Demo](.md)   
    - 3.3 [VResume](.md)   
    - 3.4 [Tinker (Template Customiser)](.md)   
4. [Shared Libraries](.md)   
    - 4.1 [django-fusion](.md)   
    - 4.2 [ceptor-ai](.md)   
5. [Infrastructure Components](.md)   
    - 5.1 [Proxy (Traefik + Nginx)](.md)   
    - 5.2 [Databases](.md)   
6. [Use Cases](.md)   
    - 6.1 [Research Publication & Management](.md)   
    - 6.2 [Course Management & Learning Delivery](.md)   
    - 6.3 [Professional Portfolio Creation](.md)   
    - 6.4 [Template Customisation Without Code](.md)   
    - 6.5 [AI-Assisted Content Generation](.md)   
    - 6.6 [Multi-Site Administration](.md)   
    - 6.7 [Integration & API Usage](.md)   
7. [Cross-Cutting Concerns](.md)   
8. [Business Value & Market Positioning](.md)   
9. [Development Workflow Integration](.md)   
10. [References & Related Documentation](.md)   
 --- 
   
## Overview   
The Structa Cloud monorepo contains **five primary websites/applications** and **multiple supporting libraries and infrastructure components**, all built on Django and Wagtail with shared templates and components. This document provides a comprehensive description of each component, its purpose, technical stack, future roadmap, and how they integrate to deliver business value.   
**Key Differentiators:**   
- **Component-Based Architecture** – Reusable UI components via `django-fusion`   
- **AI-Integrated** – Ceptor AI powers content generation and customisation   
- **Multi-Site Consistency** – Shared templates and assets across all sites   
- **Developer-Friendly** – Django/Wagtail stack with modern tooling   
- **Self-Hosted** – Complete control with Docker-based deployment   
 --- 
   
## Core Domain   
### Domain Description   
The platform operates at the intersection of:   
- **Content Management Systems (CMS)** – Wagtail-powered content administration   
- **Learning Management Systems (LMS)** – Course delivery and progress tracking   
- **Portfolio Management** – Professional portfolio and resume building   
- **AI-Assisted Content Creation** – Smart content generation and customisation   
   
### Key Domain Entities   
|           Entity   <br> |                                            Description   <br> |                              Implementation   <br> |
|:------------------------|:--------------------------------------------------------------|:---------------------------------------------------|
|         **Site**   <br> | A discrete web presence (e.g., CTC Research, LMS Demo)   <br> | Django application with Wagtail integration   <br> |
|     **Template**   <br> |                   Shared layout and styling components   <br> |                    `core/assets/templates/`   <br> |
|    **Component**   <br> |                                    Reusable UI element   <br> |                     `django-fusion` library   <br> |
|      **Content**   <br> |                      Pages, courses, research articles   <br> |                         Wagtail Page models   <br> |
|         **User**   <br> |                     System user with roles/permissions   <br> |                           Django auth model   <br> |
| **AI Assistant**   <br> |                   AI‑powered content and customisation   <br> |                         `ceptor-ai` library   <br> |

### Domain Boundaries   
```
┌──────────────────────────────────────────────────────────────────┐
│                      Structa Cloud Platform                     │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ CTC Research │  │  LMS Demo   │  │  VResume    │            │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤            │
│  │  Research    │  │  Courses    │  │ Portfolios  │            │
│  │  Training    │  │  Enrollment │  │ Resumes     │            │
│  │  Courses     │  │  Progress   │  │ AI Assistance│           │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                 │                    │
│  ┌──────┴────────────────┴─────────────────┴──────────────┐    │
│  │              Shared Assets & Templates                  │    │
│  │           core/assets/templates/static/                 │    │
│  └──────────────────────────────────────────────────────────┘    │
│         │                │                 │                    │
│  ┌──────┴────────────────┴─────────────────┴──────────────┐    │
│  │         Shared Libraries (django-fusion, ceptor-ai)     │    │
│  └──────────────────────────────────────────────────────────┘    │
│         │                │                 │                    │
│  ┌──────┴────────────────┴─────────────────┴──────────────┐    │
│  │             Infrastructure (Proxy, Databases)            │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘

```
 --- 
## Primary Websites & Applications   
### 1. CTC Research   
**Purpose:** Research and Training Platform   
**Repo Path:** `core/ctc-research/`   
### Description   
CTC Research serves as a comprehensive platform for publishing research content, delivering courses, and providing training materials. It leverages Wagtail's powerful content management capabilities to create a flexible educational ecosystem.   
### Key Features   
- **Research Publication** – academic paper management, publication workflows, DOI integration.   
- **Course Management** – course creation, module organisation, syllabus delivery.   
- **Training Materials** – interactive content, downloadable resources, multimedia integration.   
- **Wagtail Integration** – full CMS capabilities for content editors.   
- **Shared Components** – reuses templates and components from `core/assets/`.   
- **User Authentication** – role‑based access (authors, editors, students).   
   
### Technical Implementation   
- **Framework:** Django 4.2+ with Wagtail 5.x+.   
- **Content Modelling:** Wagtail Page models for research articles, courses, training modules.   
- **Templates:** Extends `core/assets/templates/base.html` and shared components.   
- **URL Structure:** `/research/`, `/courses/`, `/training/`.   
   
### Use Cases   
1. **Academic Research Groups** – publish and manage research outputs.   
2. **Corporate Training Departments** – deliver internal training programs.   
3. **Educational Institutions** – offer courses and training materials online.   
4. **Individual Researchers** – build academic profiles and publications.   
   
### Future Enhancements   
- Integration with Ceptor AI for automated research summarisation.   
- Citation management and tracking.   
- Peer review workflows.   
- Research metrics and analytics.   
 --- 
   
### 2. LMS Demo (Structa Cloud)   
**Purpose:** Learning Management System Demo   
**Repo Path:** `core/lms-demo/`   
### Description   
LMS Demo is a fully functional learning management system demonstration that showcases the Structa Cloud platform's educational capabilities. It implements core LMS features including course enrolment, progress tracking, and student dashboards.   
### Key Features   
- **Course Catalog** – browse available courses with details and prerequisites.   
- **Enrolment System** – student enrolment with progress tracking.   
- **Progress Tracking** – student progress visualisation, completion tracking.   
- **Student Dashboard** – personalised dashboard showing active courses and progress.   
- **Instructor Tools** – course management and student monitoring.   
- **Shared Stack** – same Django/Wagtail stack as CTC Research with shared components.   
   
### Technical Implementation   
- **Framework:** Django 4.2+ with Wagtail 5.x+.   
- **Course Models:** Course, Module, Lesson, Enrolment, Progress.   
- **Templates:** Extends shared base templates with LMS‑specific components.   
- **API:** REST API endpoints for course data and progress tracking.   
- **Integration:** Connects to CTC Research for content sharing.   
   
### Use Cases   
1. **EdTech Demonstrations** – showcase LMS capabilities to potential customers.   
2. **Corporate Training Evaluation** – evaluate LMS features for enterprise training.   
3. **Educational Pilots** – pilot LMS implementation for educational institutions.   
4. **Sales Demonstrations** – product demo for sales presentations.   
   
### Future Enhancements   
- Gamification features.   
- Assessment and quiz engines.   
- Certification and credentialing.   
- SSO integration (SAML, OAuth).   
 --- 
   
### 3. VResume   
**Purpose:** Portfolio and Resume Builder   
**Repo Path:** `core/VResume/`   
### Description   
VResume is a professional portfolio and resume builder that enables users to create, customise, and publish professional portfolios. The directory uses a capitalised name (VResume) while Makefile aliases use `vresume`.   
### Key Features   
- **Portfolio Creation** – drag‑and‑drop portfolio builder with Wagtail pages.   
- **Resume Builder** – professional resume creation with multiple templates.   
- **Customisation** – theme selection, color customisation, layout options.   
- **Wagtail Integration** – content management for portfolio sections.   
- **AI Assistance** – AI‑powered content suggestions via Ceptor AI.   
   
### Technical Implementation   
- **Framework:** Django 4.2+ with Wagtail 5.x+.   
- **Portfolio Models:** Project, Experience, Education, Skill, Achievement.   
- **Templates:** Shared base templates with portfolio‑specific styling.   
- **Export:** PDF export for resumes, portfolio export.   
   
### Use Cases   
1. **Creative Professionals** – showcase work in design, art, and media.   
2. **Software Developers** – portfolio of projects and contributions.   
3. **Academics** – research portfolio with publications and teaching.   
4. **Freelancers** – client‑facing portfolio and resume.   
5. **Job Seekers** – professional resume and portfolio for applications.   
   
### Future Enhancements   
- Advanced portfolio analytics (view tracking, engagement).   
- Social media integration.   
- Personal branding features.   
- Multi‑language support.   
 --- 
   
### 4. Tinker (Template Customiser)   
**Purpose:** Template Customisation Tool   
**Repo Path:** `core/tinker/`   
### Description   
Tinker is a visual template customisation tool that provides a user‑friendly interface for customising shared templates across all Structa Cloud sites. It enables non‑developers to adjust themes and components without touching code.   
### Key Features   
- **Visual Template Customisation** – theme selection, color palette, font choices.   
- **Component Styling** – customise individual components (buttons, cards, navigation).   
- **Preview Mode** – live preview of changes.   
- **CSS Variables** – dynamic styling without touching CSS.   
- **User‑Friendly Interface** – non‑developer accessible UI.   
   
### Technical Implementation   
- **Framework:** Django 4.2+ with React/Vue.js (frontend).   
- **Styling Engine:** CSS variables mapped to django-fusion components.   
- **State Management:** Redux/Vuex for user preferences.   
- **Storage:** User preferences stored in the database.   
- **Integration:** Works with all structa‑cloud sites.   
   
### Use Cases   
1. **Marketing Teams** – customise site appearance for campaigns.   
2. **Content Creators** – adjust branding without developer help.   
3. **Enterprise Customers** – maintain brand consistency across sites.   
4. **Agency Clients** – self‑service customisation.   
   
### Future Enhancements   
- Template marketplace.   
- Advanced component builder.   
- Versioning for themes.   
- Export/import of custom templates.   
 --- 
   
## Shared Libraries   
### 5.1 django-fusion   
**Repo Path:** `core/libs/django-fusion/`   
### Description   
django-fusion is a component‑based Django framework used by all Structa Cloud sites. It provides routing, generic class‑based views (CBVs), routable components, and fragment rendering.   
### Key Features   
- **Component‑Based Architecture** – React‑like components in Django.   
- **Routable Components** – URL routing at component level.   
- **Fragment Rendering** – partial page updates.   
- **Generic CBVs** – extended base views for rapid development.   
- **Template Integration** – seamless template component integration.   
   
### Technical Implementation   
- **Framework:** Django 4.2+.   
- **Components:** Python classes with template rendering.   
- **Fragment System:** server‑side fragment updates.   
- **Performance:** caching and optimised rendering.   
- **Compatibility:** works with Wagtail and standard Django.   
   
### Use Cases   
1. **Accelerated development** – rapid component creation.   
2. **Consistent UI** – shared components across all sites.   
3. **Maintainability** – single source of truth for UI components.   
4. **Developer Experience** – consistent component patterns.   
   
### Future Enhancements   
- Server components (similar to React Server Components).   
- LiveView‑style real‑time updates.   
- Component library with Storybook integration.   
 --- 
   
### 5.2 ceptor-ai   
**Repo Path:** `core/libs/ceptor-ai/`   
### Description   
ceptor-ai provides AI integration helpers powering AI‑assisted content generation and customisation across all Structa Cloud applications.   
### Key Features   
- **Content Generation** – AI‑powered content creation (research, courses, portfolios).   
- **Smart Customisation** – AI‑assisted template customisation.   
- **Text Analysis** – NLP for content optimisation.   
- **Personalisation** – user‑specific content recommendations.   
   
### Technical Implementation   
- **Framework:** Python with Django integration.   
- **AI Models:** integration with OpenAI API, Hugging Face.   
- **Caching:** smart caching for AI responses.   
- **Security:** API key management, content filtering.   
   
### Use Cases   
1. **Content Generation** – research summaries, course descriptions, portfolio text.   
2. **Customisation Assistance** – AI suggests template customisations.   
3. **Content Enhancement** – grammar checking, tone adjustment.   
4. **Personalised Learning** – AI‑curated educational content.   
 --- 
   
## Infrastructure Components   
### 6.1 Proxy (Traefik + Nginx)   
**Repo Path:** `applications/proxy/`   
### Description   
The proxy layer handles SSL termination and routing via Traefik while Nginx serves static and media files for all sites.   
### Technical Implementation   
- **Traefik:** Edge router with Let's Encrypt SSL termination.   
- **Nginx:** Static and media file serving.   
- **Docker Compose:** Containerised deployment.   
- **Health Checks:** Automated service health monitoring.   
   
### Configuration Snippets   
```
# Traefik
http:
  routers:
    web:
      rule: "Host(`structa.example.com`)"
      service: "app-service"
      tls:
        certResolver: "letsencrypt"

```
```
# Nginx
server {
    listen 80;
    server_name structa.example.com;
    root /static;
    location /static/ { alias /static/; }
    location /media/ { alias /media/; }
}

```
 --- 
### 6.2 Databases   
**Repo Path:** `applications/databases/`   
### Description   
PostgreSQL and Redis services shared across all Structa Cloud sites for data persistence and caching.   
### Technical Implementation   
- **PostgreSQL:** Primary data store (version 15+).   
- **Redis:** Cache, session storage, task queue.   
- **Replication:** Master‑slave for high availability.   
- **Backup:** Automated backups to S3‑compatible storage.   
   
### Use Cases   
1. **Data Persistence** – all application data.   
2. **Session Management** – user sessions across sites.   
3. **Caching** – performance optimisation.   
4. **Task Queues** – Celery or Redis queues for background tasks.   
 --- 
   
## Primary Use Cases   
### Use Case 1: Research Publication and Management   
**Actor:** Researcher, Academic Institution, Corporate Training Department   
| Step   <br> |                     Action   <br> |         System Response   <br> |            Data Flow   <br> |
|:------------|:----------------------------------|:-------------------------------|:----------------------------|
|    1   <br> | Researcher creates account   <br> |   User account creation   <br> |           Auth model   <br> |
|    2   <br> |      Accesses CTC Research   <br> | Wagtail admin interface   <br> |         Site routing   <br> |
|    3   <br> |   Creates research article   <br> |      Wagtail Page model   <br> |        Content model   <br> |
|    4   <br> |   Adds AI‑assisted content   <br> |    Ceptor AI suggestion   <br> |       AI integration   <br> |
|    5   <br> |         Publishes research   <br> |      Public‑facing page   <br> |     Content delivery   <br> |
|    6   <br> |    Shares through LMS Demo   <br> |      Cross‑site linking   <br> |   Multi‑site sharing   <br> |

**Success Criteria:** Research article published with AI‑assisted content, available across sites.   
**Related Repo:** `core/ctc-research/`   
 --- 
### Use Case 2: Course Management and Learning Delivery   
**Actor:** Course Creator, Student, Administrator   
| Step   <br> |                            Action   <br> |           System Response   <br> |              Data Flow   <br> |
|:------------|:-----------------------------------------|:---------------------------------|:------------------------------|
|    1   <br> |  Course creator uses CTC Research   <br> | Course creation interface   <br> |       Content modeling   <br> |
|    2   <br> |          Builds course curriculum   <br> |    Module/Lesson creation   <br> |           Wagtail Page   <br> |
|    3   <br> |                  Enables LMS Demo   <br> |       Course availability   <br> |        Cross‑site sync   <br> |
|    4   <br> |      Student enrolls via LMS Demo   <br> |         Enrollment record   <br> |       Enrollment model   <br> |
|    5   <br> | Student progresses through course   <br> |         Progress tracking   <br> |         Progress model   <br> |
|    6   <br> |          Student completes course   <br> |    Completion certificate   <br> | Certificate generation   <br> |

**Success Criteria:** Course created, students enrolled, progress tracked, certificates generated.   
**Related Repos:** `core/ctc-research/`, `core/lms-demo/`   
 --- 
### Use Case 3: Professional Portfolio Creation   
**Actor:** Professional, Freelancer, Job Seeker   
| Step   <br> |                           Action   <br> |              System Response   <br> |        Data Flow   <br> |
|:------------|:----------------------------------------|:------------------------------------|:------------------------|
|    1   <br> |    Professional accesses VResume   <br> |            Portfolio builder   <br> |    Wagtail admin   <br> |
|    2   <br> |       Creates portfolio sections   <br> | Project/Experience/Education   <br> | Portfolio models   <br> |
|    3   <br> | Customises appearance via Tinker   <br> |         Visual customisation   <br> |    CSS variables   <br> |
|    4   <br> |         Adds AI‑assisted content   <br> |            AI‑generated text   <br> |        Ceptor AI   <br> |
|    5   <br> |              Publishes portfolio   <br> |                   Public URL   <br> |  Site deployment   <br> |
|    6   <br> |             Generates PDF resume   <br> |                Resume export   <br> |   PDF generation   <br> |

**Success Criteria:** Professional portfolio created, customised, and published.   
**Related Repos:** `core/VResume/`, `core/tinker/`   
 --- 
### Use Case 4: Template Customisation Without Code   
**Actor:** Content Manager, Marketing Team, Non‑Technical User   
| Step   <br> |                    Action   <br> |        System Response   <br> |        Data Flow   <br> |
|:------------|:---------------------------------|:------------------------------|:------------------------|
|    1   <br> |      User accesses Tinker   <br> | Template customiser UI   <br> |     UI rendering   <br> |
|    2   <br> | Selects site to customise   <br> |           Site listing   <br> |    Site registry   <br> |
|    3   <br> |    Chooses template theme   <br> |          Theme options   <br> |    CSS variables   <br> |
|    4   <br> |   Customises colors/fonts   <br> |      Real‑time preview   <br> |    Live updating   <br> |
|    5   <br> |    Applies customisations   <br> |       Site‑wide update   <br> | Database storage   <br> |
|    6   <br> |     Verifies on live site   <br> |           Confirmation   <br> |       Deployment   <br> |

**Success Criteria:** Template customisation applied without code changes.   
**Related Repo:** `core/tinker/`   
 --- 
### Use Case 5: AI‑Assisted Content Generation   
**Actor:** Content Creator, Researcher, Course Creator   
| Step   <br> |                       Action   <br> |             System Response   <br> |          Data Flow   <br> |
|:------------|:------------------------------------|:-----------------------------------|:--------------------------|
|    1   <br> | User accesses content editor   <br> |            Editor interface   <br> |      Wagtail admin   <br> |
|    2   <br> |       Requests AI assistance   <br> |        Ceptor AI activation   <br> |     AI integration   <br> |
|    3   <br> |       Provides topic/context   <br> |        AI prompt generation   <br> | Prompt engineering   <br> |
|    4   <br> |         AI generates content   <br> | AI response with formatting   <br> |      Content model   <br> |
|    5   <br> |       User reviews and edits   <br> |          Content refinement   <br> |     Manual editing   <br> |
|    6   <br> |            Publishes content   <br> |               Final content   <br> |    Site deployment   <br> |

**Success Criteria:** AI‑generated content refined and published.   
**Related Repo:** `core/libs/ceptor-ai/`   
 --- 
### Use Case 6: Multi‑Site Administration   
**Actor:** System Administrator, DevOps Engineer   
| Step   <br> |                    Action   <br> |     System Response   <br> |              Data Flow   <br> |
|:------------|:---------------------------------|:---------------------------|:------------------------------|
|    1   <br> | Admin accesses management   <br> |     Admin dashboard   <br> |           Django admin   <br> |
|    2   <br> |         Views site health   <br> |       System status   <br> |       Monitoring tools   <br> |
|    3   <br> |       Manages users/roles   <br> | User administration   <br> |            Auth models   <br> |
|    4   <br> |          Performs updates   <br> |      System updates   <br> |              Git/CI/CD   <br> |
|    5   <br> |          Deploys new site   <br> |       Site creation   <br> | Application deployment   <br> |
|    6   <br> |      Monitors performance   <br> | Performance metrics   <br> |     Prometheus/Grafana   <br> |

**Success Criteria:** Multi‑site administration with monitoring and updates.   
**Related Files:** `Makefile`, `docker-compose.yml`, `applications/`   
 --- 
### Use Case 7: Integration and API Usage   
**Actor:** Developer, Systems Integrator, Third‑Party Application   
| Step   <br> |                           Action   <br> |      System Response   <br> |         Data Flow   <br> |
|:------------|:----------------------------------------|:----------------------------|:-------------------------|
|    1   <br> |      Developer accesses API docs   <br> |    API documentation   <br> |   Swagger/OpenAPI   <br> |
|    2   <br> |        Authenticates API request   <br> | Token/SSO validation   <br> |       Auth system   <br> |
|    3   <br> |        Retrieves content via API   <br> |        JSON response   <br> |     API endpoints   <br> |
|    4   <br> |          Creates/updates content   <br> | API write operations   <br> |    Content models   <br> |
|    5   <br> |          Retrieves user progress   <br> |        Progress data   <br> | Progress tracking   <br> |
|    6   <br> | Integrates with external systems   <br> |   External API calls   <br> | Integration layer   <br> |

**Success Criteria:** API‑based integration with external systems.   
**Related:** `core/\*/api.py`, `core/configs/`   
 --- 
## Cross-Cutting Concerns   
### Shared Components and Templates   
```
core/assets/
├── templates/
│   ├── base.html              # Base template for all sites
│   ├── components/            # Reusable component templates
│   │   ├── navigation.html
│   │   ├── cards.html
│   │   ├── forms.html
│   │   └── footer.html
│   └── wagtail/
│       └── snippets.html
├── static/
│   ├── css/
│   │   ├── base.css           # Shared CSS foundation
│   │   └── themes/           # Theme‑specific CSS
│   ├── js/
│   │   ├── components/       # Shared JavaScript components
│   │   └── tinker/          # Tinker customisation script
│   └── images/
└── webpack.config.js          # Asset compilation configuration

```
### Data Sharing Across Sites   
- **Shared Database:** PostgreSQL with schema isolation by site.   
- **Shared Cache:** Redis for session management and caching.   
- **Shared Media:** Centralised S3/cloud storage.   
- **Shared Authentication:** Django auth with site‑specific roles.   
   
### Security Considerations   
- **HTTPS Everywhere:** Traefik handles SSL termination.   
- **API Security:** Token-based authentication with JWT.   
- **Data Privacy:** GDPR-compliant architecture.   
- **Role-Based Access Control:** Wagtail permissions system.   
 --- 
   
## Business Value and Market Positioning   
### Value Proposition   
|                         Need   <br> |                        Solution   <br> |                    Implementation   <br> |
|:------------------------------------|:---------------------------------------|:-----------------------------------------|
|   **Multi‑site consistency**   <br> | Shared templates and components   <br> | `core/assets/` with django-fusion   <br> |
|       **Content management**   <br> |                     Wagtail CMS   <br> |        All sites use Wagtail 5.x+   <br> |
|        **Learning delivery**   <br> |                  Integrated LMS   <br> |           CTC Research + LMS Demo   <br> |
|       **Portfolio building**   <br> |                 VResume builder   <br> |           Wagtail‑based portfolio   <br> |
|   **Template customisation**   <br> |               Visual customiser   <br> |         Tinker with CSS variables   <br> |
|           **AI enhancement**   <br> |        Integrated AI assistance   <br> |                 ceptor-ai library   <br> |
|           **Infrastructure**   <br> |         Docker‑based deployment   <br> |      `applications/` with Traefik   <br> |

### Target Market Segments   
|                      Segment   <br> |            Primary Need   <br> |                   Usage   <br> |
|:------------------------------------|:-------------------------------|:-------------------------------|
|         **EdTech companies**   <br> |      Combined CMS + LMS   <br> | CTC Research + LMS Demo   <br> |
|    **Professional services**   <br> |    Research + portfolio   <br> |  CTC Research + VResume   <br> |
|       **Corporate training**   <br> | Content + customisation   <br> |       LMS Demo + Tinker   <br> |
|         **Digital agencies**   <br> |   Multi‑site management   <br> |       Complete platform   <br> |
| **Individual professionals**   <br> |        Portfolio/resume   <br> |        VResume + Tinker   <br> |

### Competitive Advantages   
|                    Feature   <br> | Structa Cloud   <br> |   WordPress   <br> | Contentful   <br> |     Moodle   <br> |
|:----------------------------------|:---------------------|:-------------------|:------------------|:------------------|
|  **AI Content Generation**   <br> |    ✅ Built-in   <br> |    ❌ Add-on   <br> |   ❌ Add-on   <br> |       ❌ No   <br> |
|  **Multi-Site Management**   <br> |      ✅ Native   <br> |   ❌ Limited   <br> |       ❌ No   <br> |       ❌ No   <br> |
| **Template Customisation**   <br> |      ✅ Visual   <br> |    ❌ Coding   <br> |   ❌ Coding   <br> |   ❌ Coding   <br> |
|        **LMS Integration**   <br> |    ✅ Complete   <br> |    ❌ Plugin   <br> |       ❌ No   <br> |   ✅ Native   <br> |
|            **Open Source**   <br> |         ✅ Yes   <br> |       ✅ Yes   <br> |       ❌ No   <br> |      ✅ Yes   <br> |

 --- 
## Development Workflow Integration   
The project domain is tightly integrated with the Anytype workspace for planning and tracking:   
### Anytype Workspace Usage   
- **Tasks** – link to specific repo paths and sites.   
- **Vision** – high‑level direction and goals.   
- **Product Development** – detailed planning and milestones.   
- **Architecture** – technical design and patterns.   
   
### Development Process Flow   
```
Anytype Capture → Repo Path Mapping → Implementation → Validation → Review → Deployment

```
### Roadmap and Future Development   
|       Phase   <br> |     Timeline   <br> |               Focus   <br> |                                    Features   <br> |
|:-------------------|:--------------------|:---------------------------|:---------------------------------------------------|
| **Phase 1**   <br> |   Q1‑Q2 2026   <br> | Platform foundation   <br> |    Core sites, shared assets, django-fusion   <br> |
| **Phase 2**   <br> |   Q3‑Q4 2026   <br> |      AI integration   <br> |            ceptor-ai, AI content generation   <br> |
| **Phase 3**   <br> |   Q1‑Q2 2027   <br> | Enterprise features   <br> |                SSO, advanced LMS, analytics   <br> |
| **Phase 4**   <br> |   Q3‑Q4 2027   <br> |         Marketplace   <br> |            Template marketplace, extensions   <br> |
| **Phase 5**   <br> |        2028+   <br> |  Platform expansion   <br> | Mobile apps, headless, internationalisation   <br> |

 --- 
## References & Related Documentation   
### Primary Documents   
- **[Market Research & Analysis](market-research-analysis.md)** – Industry trends, competitors, target audiences, and USP.   
- **[Operational Plan](operational-plan.md)** – Development, production, deployment, customer service, and disaster recovery.   
- **[Risk Management](risk-management.md)** – Financial, operational, reputational, and strategic risks with mitigation strategies.   
- **[Website & Application Descriptions (Standalone)](website-applications.md)** – Detailed descriptions of every site, shared library, and infrastructure component.   
- **[Project Domain & Use Cases (Standalone)](project-domain-use-cases.md)** – Core domain model, primary/secondary use cases, and business value mapping.   
   
### Recommended New Files   
- **[Architecture Overview](architecture-overview.md)** – High-level technical architecture diagram and explanation.   
- **[Development Workflow](development-workflow.md)** – Step-by-step developer guide and contribution workflow.   
- **[API Reference](api-reference.md)** – REST API documentation for third-party integrations.   
- **[Contributing Guide](contributing-guide.md)** – Open source contribution guidelines.   
- **[Changelog](changelog.md)** – Version history and release notes.   
- **[Deployment Guide](deployment-guide.md)** – Production deployment handbook.   
- **[Glossary](glossary.md)** – Domain-specific terminology reference.   
 --- 
   
## Quick Reference   
### Key Repo Paths   
- **CTC Research:** `core/ctc-research/`   
- **LMS Demo:** `core/lms-demo/`   
- **VResume:** `core/VResume/`   
- **Tinker:** `core/tinker/`   
- **django-fusion:** `core/libs/django-fusion/`   
- **ceptor-ai:** `core/libs/ceptor-ai/`   
- **Proxy:** `applications/proxy/`   
- **Databases:** `applications/databases/`   
- **Shared Assets:** `core/assets/`   
- **Configuration:** `core/configs/`   
- **Tests:** `tests/`   
- **Documentation:** `docs/`   
   
### Core Technologies   
- **Backend:** Django 4.2+, Python 3.11+   
- **CMS:** Wagtail 5.x+   
- **Frontend:** React/Vue.js (Tinker), Bootstrap/Tailwind CSS   
- **Database:** PostgreSQL 15+, Redis 7+   
- **Proxy:** Traefik, Nginx   
- **Container:** Docker, Docker Compose   
- **AI:** OpenAI API, Hugging Face   
- **Monitoring:** Prometheus, Grafana, ELK Stack   
   
### Make Commands (Quick Reference)   
```
# Development
make -C core run-dev WEBSITE=<site>
make -C core build-assets WEBSITE=<site>
make -C core migrate WEBSITE=<site>
make -C core check WEBSITE=<site>

# Testing
make -C core test-local
make deploy-preflight

# Deployment
make deploy
make deploy-databases
make deploy-apps
make deploy-proxy

```
 --- 
**Document Version:** 2.0   
**Last Updated:** 2026-07-18   
**Maintained By:** Structa Cloud Development Team   
 --- 
**See also:**   
- [Market Research](market-research-analysis.md) – for market alignment and competitive analysis.   
- [Operational Plan](operational-plan.md) – for deployment and maintenance procedures.   
- [Risk Management](risk-management.md) – for identifying and mitigating project risks.   
- [Project Domain & Use Cases](project-domain-use-cases.md) – for standalone domain reference.   
- [Website Applications](http://website-applications.md) – for standalone application descriptions.   
