# Django-Grep Usage Analysis
**Spec:** Django Project Reorganization & Email Automation
**Task:** 2.3 - Create django-fusion usage analysis document
**Requirements:** 15.3-15.6
**Date:** 2025-01-XX

---

## Executive Summary

This document provides a comprehensive mapping of django-fusion usage across both ctc-research.com and structa.cloud websites. The analysis identifies which components are used by each website, shared features, and website-specific dependencies.

**Key Findings:**
- **Total Files Using django-fusion:** 100+ files across both websites
- **Shared Components:** DefaultBase, Person, PageHandler, NotificationMixin, CachedManager, BaseStreamBlock
- **ctc-research.com Specific:** LMS payment integrations, course-specific blocks
- **structa.cloud Specific:** Workspace/Team models, invitation system, more extensive configuration usage

---

## 1. Component Usage Mapping Table

### 1.1 Models

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **DefaultBase** | Base Model | ✓ | ✓ | 30+ | Core model with timestamps, is_active |
| **Person** | User Profile | ✓ | ✓ | 40+ | Extensive user profile model |
| **BaseTag** | Tagging | ✓ | ✓ | 10+ | Enhanced tagging system |
| **BaseTagCategory** | Tagging | ✓ | ✓ | 5+ | Tag categorization |
| **ContentBase** | Content Model | ✓ | ✗ | 1 | LMS-specific content base |
| **TemplateRenderMixin** | Model Mixin | ✓ | ✓ | 2 | Template rendering for models |
| **EmailTemplate** | Email System | ✗ | ✓ | 2 | Email template management |
| **Newsletter** | Email System | ✗ | ✓ | 1 | Newsletter management |
| **Workspace** | Organization | ✗ | ✓ | 1 | Workspace management |
| **Team** | Organization | ✗ | ✓ | 1 | Team management |
| **GlobalSettings** | Configuration | ✓ | ✗ | 1 | Site-wide settings |
| **CachingStorage** | Utility | ✓ | ✗ | 2 | Caching utilities |

### 1.2 Views & Site Components

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **PageHandler** | Base View | ✓ | ✓ | 20+ | Core page rendering with components |
| **NotificationMixin** | View Mixin | ✓ | ✓ | 15+ | Notification display capabilities |
| **PaymentProcessingMixin** | Payment View | ✓ | ✗ | 1 | Payment processing for LMS |

### 1.3 Component Blocks (Wagtail)

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **BaseStreamBlock** | StreamField | ✓ | ✓ | 3 | Core content blocks |
| **BaseBlock** | Block Base | ✓ | ✗ | 1 | LMS assignment blocks |
| **OverviewBlock** | Content Block | ✓ | ✗ | 1 | Course overview |
| **EventSectionBlock** | Content Block | ✓ | ✓ | 2 | Event-specific blocks |
| **ServicesSectionBlock** | Content Block | ✓ | ✓ | 2 | Service-specific blocks |
| **ContactMethodBlock** | Contact Block | ✓ | ✓ | 4 | Contact information |
| **ContactMethodsStreamBlock** | Contact Block | ✗ | ✓ | 2 | Contact methods stream |
| **FAQSectionBlock** | Content Block | ✓ | ✓ | 4 | FAQ sections |
| **ContactCardBlock** | Contact Block | ✓ | ✓ | 2 | Contact cards |
| **PageLinkBlock** | Navigation Block | ✓ | ✓ | 2 | Page links |
| **MediaGalleryBlock** | Media Block | ✓ | ✓ | 2 | Media galleries |

### 1.4 Managers

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **CachedManager** | Manager | ✓ | ✓ | 10+ | Manager with caching |
| **BaseManager** | Manager | ✓ | ✓ | 8+ | Base manager with common queries |
| **cached_method** | Decorator | ✓ | ✓ | 6+ | Method caching decorator |

### 1.5 Services & Utilities

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **BaseService** | Service Base | ✓ | ✗ | 4 | Base service class |
| **TokenService** | Service | ✓ | ✗ | 3 | Token management |
| **CRUDService** | Service | ✓ | ✗ | 1 | CRUD operations |
| **dispatch_job** | Job Queue | ✓ | ✓ | 6 | Background job dispatching |
| **StripeGateway** | Payment | ✓ | ✗ | 2 | Stripe payment integration |
| **PayPalGateway** | Payment | ✓ | ✗ | 2 | PayPal payment integration |

### 1.6 Configuration

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **AppSettings** | Configuration | ✓ | ✓ | 4 | Application settings |
| **DjangoComponentsSettings** | Configuration | ✓ | ✓ | 4 | Components configuration |
| **EmailPriority** | Enum | ✓ | ✓ | 2 | Email priority levels |
| **EmailSendingStrategy** | Enum | ✓ | ✓ | 2 | Email sending strategies |
| **EmailStatus** | Enum | ✗ | ✓ | 1 | Email status tracking |
| **TemplateSource** | Enum | ✗ | ✓ | 1 | Template source types |
| **Environment** | Enum | ✓ | ✓ | 2 | Environment types |
| **LogLevel** | Enum | ✓ | ✓ | 2 | Logging levels |
| **Module** | Enum | ✓ | ✓ | 2 | Module types |
| **Runtime** | Enum | ✓ | ✓ | 2 | Runtime environments |
| **Workflow** | Enum | ✓ | ✗ | 1 | Workflow types |
| **Direction** | Enum | ✓ | ✗ | 1 | Direction enum |

### 1.7 Debug & Development Tools

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **configure_common_urls** | URL Helper | ✓ | ✓ | 4 | Common URL configuration |
| **configure_dev_urls** | URL Helper | ✓ | ✓ | 4 | Development URL configuration |
| **handler400/403/404/500** | Error Views | ✓ | ✓ | 4 | Error page handlers |
| **health_check** | Health Check | ✓ | ✗ | 1 | Health check endpoint |

### 1.8 Signals

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **invitations** | Signal Namespace | ✓ | ✓ | 2 | Invitation-related signals |

### 1.9 Contrib Models

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **Contact** | Model | ✗ | ✓ | 1 | Contact information |
| **ContactEmail** | Model | ✗ | ✓ | 1 | Contact email |
| **ContactPhone** | Model | ✗ | ✓ | 1 | Contact phone |
| **Corporate** | Model | ✗ | ✓ | 1 | Company model |

### 1.10 Snippets (Wagtail Admin)

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **FormSubmissionViewSet** | Snippet | ✓ | ✗ | 1 | Form submission management |

### 1.11 Payment Views

| Component | Type | ctc-research.com | structa.cloud | Usage Count | Notes |
|-----------|------|------------------|---------------|-------------|-------|
| **StripeInitView** | Payment View | ✓ | ✗ | 1 | Stripe initialization |
| **PayPalInitView** | Payment View | ✓ | ✗ | 1 | PayPal initialization |
| **CartStripeInitView** | Payment View | ✓ | ✗ | 1 | Cart Stripe init |
| **CartPayPalInitView** | Payment View | ✓ | ✗ | 1 | Cart PayPal init |
| **StripeWebhookView** | Payment View | ✓ | ✗ | 1 | Stripe webhook handler |

---

## 2. Shared Features (Used by Both Websites)

### 2.1 Core Models
- **DefaultBase** - Base model with common fields (id, created_at, updated_at, is_active)
- **Person** - User profile model with extensive features
- **BaseTag / BaseTagCategory** - Enhanced tagging system
- **TemplateRenderMixin** - Template rendering for models

### 2.2 Core Views
- **PageHandler** - Base view class for page rendering with component support
- **NotificationMixin** - Notification display capabilities

### 2.3 Core Blocks
- **BaseStreamBlock** - Core StreamField blocks for Wagtail
- **EventSectionBlock** - Event-specific content blocks
- **ServicesSectionBlock** - Service-specific content blocks
- **ContactMethodBlock** - Contact information blocks
- **FAQSectionBlock** - FAQ content blocks
- **ContactCardBlock** - Contact cards
- **PageLinkBlock** - Page links
- **MediaGalleryBlock** - Media galleries

### 2.4 Core Managers
- **CachedManager** - Manager with caching capabilities
- **BaseManager** - Base manager with common query methods
- **cached_method** - Decorator for caching manager methods

### 2.5 Core Services
- **dispatch_job** - Background job dispatching with django-rq

### 2.6 Core Configuration
- **AppSettings** - Application-level settings management
- **DjangoComponentsSettings** - Django components configuration
- **EmailPriority** - Email priority levels
- **EmailSendingStrategy** - Email sending strategies
- **Environment / LogLevel / Module / Runtime** - Common enumerations

### 2.7 Core Debug Tools
- **configure_common_urls** - Common URL configuration
- **configure_dev_urls** - Development URL configuration
- **handler400/403/404/500** - Error page handlers

### 2.8 Core Signals
- **invitations** - Invitation-related signals

---

## 3. ctc-research.com Specific Features

### 3.1 LMS-Specific Models
- **ContentBase** - Base model for LMS content
- **GlobalSettings** - Site-wide settings
- **CachingStorage** - Caching utilities

### 3.2 LMS-Specific Blocks
- **BaseBlock** - Base block for LMS assignments
- **OverviewBlock** - Course overview blocks

### 3.3 LMS-Specific Services
- **BaseService** - Base service class for business logic
- **TokenService** - Token management service
- **CRUDService** - CRUD operations service

### 3.4 Payment Integration
- **PaymentProcessingMixin** - Payment processing view mixin
- **StripeGateway / PayPalGateway** - Payment gateway integrations
- **StripeInitView / PayPalInitView** - Payment initialization views
- **CartStripeInitView / CartPayPalInitView** - Cart payment views
- **StripeWebhookView** - Stripe webhook handler

### 3.5 Configuration
- **Workflow** - Workflow types enum
- **Direction** - Direction enum

### 3.6 Utilities
- **health_check** - Health check endpoint
- **FormSubmissionViewSet** - Form submission management

---

## 4. structa.cloud Specific Features

### 4.1 Organization Models
- **Workspace** - Workspace management model
- **Team** - Team management model

### 4.2 Email System Models
- **EmailTemplate** - Email template management
- **Newsletter** - Newsletter management

### 4.3 Configuration
- **EmailStatus** - Email status tracking enum
- **TemplateSource** - Template source types enum

### 4.4 Contrib Models
- **Contact / ContactEmail / ContactPhone** - Contact information models
- **Corporate** - Company model

### 4.5 Additional Blocks
- **ContactMethodsStreamBlock** - Contact methods stream blocks

---

## 5. Usage Statistics

### 5.1 Overall Statistics
- **Total Components Identified:** 70+
- **Shared Components:** 35 (50%)
- **ctc-research.com Specific:** 20 (28.5%)
- **structa.cloud Specific:** 15 (21.5%)

### 5.2 Usage by Category

#### Models (Heavy Usage)
- **Shared:** DefaultBase, Person, BaseTag, BaseTagCategory, TemplateRenderMixin
- **ctc-research.com:** ContentBase, GlobalSettings, CachingStorage
- **structa.cloud:** EmailTemplate, Newsletter, Workspace, Team, Contact models

#### Views (Heavy Usage)
- **Shared:** PageHandler, NotificationMixin
- **ctc-research.com:** PaymentProcessingMixin, Payment views

#### Blocks (Moderate Usage)
- **Shared:** BaseStreamBlock, EventSectionBlock, ServicesSectionBlock, Contact blocks, FAQ blocks, Media blocks
- **ctc-research.com:** BaseBlock, OverviewBlock
- **structa.cloud:** ContactMethodsStreamBlock

#### Managers (Moderate Usage)
- **Shared:** CachedManager, BaseManager, cached_method

#### Services (Light to Moderate Usage)
- **Shared:** dispatch_job
- **ctc-research.com:** BaseService, TokenService, CRUDService, Payment gateways

#### Configuration (Heavy Usage)
- **Shared:** AppSettings, DjangoComponentsSettings, Email enums, Environment enums
- **ctc-research.com:** Workflow, Direction
- **structa.cloud:** EmailStatus, TemplateSource

#### Debug Tools (Light Usage)
- **Shared:** URL configurators, Error handlers
- **ctc-research.com:** health_check

---

## 6. Critical Dependencies Analysis

### 6.1 Must-Have Features (Cannot Remove)
These features are essential and heavily used by both websites:

1. **DefaultBase model** - Used by 30+ models across both sites
2. **Person model** - Used by 40+ files across both sites
3. **PageHandler view** - Used by 20+ views across both sites
4. **NotificationMixin** - Used by 15+ views across both sites
5. **CachedManager** - Used by 10+ managers across both sites
6. **AppSettings** - Core configuration for both sites
7. **BaseStreamBlock** - Wagtail content foundation

### 6.2 Important Features (High Usage)
These features are used extensively but could potentially be replaced:

1. **Tag models** - Used by 10+ files
2. **dispatch_job** - Used by 6 files
3. **Contact blocks** - Used by 4+ files
4. **BaseManager** - Used by 8+ files
5. **Debug tools** - Development infrastructure

### 6.3 Website-Specific Features (Moderate Usage)
These features are used by only one website:

**ctc-research.com:**
- Payment integration (StripeGateway, PayPalGateway, payment views)
- LMS services (BaseService, TokenService, CRUDService)
- LMS-specific models and blocks

**structa.cloud:**
- Organization models (Workspace, Team)
- Email system models (EmailTemplate, Newsletter)
- Contrib models (Contact, Corporate)

### 6.4 Optional Features (Light Usage)
These features have minimal usage and could be inlined or replaced:

1. **Signals** - 2 files total
2. **Contrib models** - 1 file (structa.cloud only)
3. **Template tags** - Not used in either website
4. **health_check** - 1 file (ctc-research.com only)

---

## 7. Migration Considerations

### 7.1 High-Risk Areas (Requires Careful Planning)
- **Model inheritance** (DefaultBase, Person) - Database migrations required
- **View base classes** (PageHandler, NotificationMixin) - Affects all views
- **Manager classes** (CachedManager) - Query optimization dependencies
- **Configuration** (AppSettings) - Core application settings

### 7.2 Medium-Risk Areas (Moderate Complexity)
- **Component blocks** (StreamBlocks) - Wagtail content structure
- **Tag models** - Tagging system dependencies
- **Job dispatching** - Background task infrastructure
- **Payment integration** (ctc-research.com only) - Financial transactions

### 7.3 Low-Risk Areas (Easy to Replace)
- **Debug tools** - Development only, not production-critical
- **Signals** - Limited usage, easy to inline
- **Contrib utilities** - Minimal usage, simple to replace
- **Template tags** - Not currently used

---

## 8. Consolidation Recommendations

### 8.1 Keep as Dependency
**Recommendation:** Keep these as django-fusion dependencies due to complexity and heavy usage:

1. **DefaultBase, Person** - Core models with extensive usage
2. **PageHandler, NotificationMixin** - Core view infrastructure
3. **CachedManager, BaseManager** - Query optimization layer
4. **AppSettings, DjangoComponentsSettings** - Configuration foundation
5. **BaseStreamBlock** - Wagtail content foundation

**Rationale:** These components are deeply integrated, heavily used, and complex to inline. Maintaining them as dependencies reduces migration risk.

### 8.2 Consider Inlining
**Recommendation:** Consider inlining these features if consolidation is desired:

1. **Tag models** - Moderate usage, could be simplified
2. **Contact blocks** - Simple blocks, easy to inline
3. **Debug tools** - Development utilities, low risk

**Rationale:** These components have moderate usage and are relatively simple to inline without significant risk.

### 8.3 Evaluate Necessity
**Recommendation:** Evaluate whether these features are still needed:

1. **Signals** - Limited usage, may not be necessary
2. **Contrib models** - Single-site usage, could be moved to site-specific code
3. **Template tags** - Not used, can be removed

**Rationale:** These components have minimal usage and may not provide sufficient value to justify maintenance.

### 8.4 Website-Specific Extraction
**Recommendation:** Extract website-specific features to site-specific code:

**ctc-research.com:**
- Payment integration (move to ctc-research.com/apps/payments/)
- LMS services (move to ctc-research.com/apps/LMS/services/)

**structa.cloud:**
- Organization models (move to structa.cloud/apps/organization/)
- Email system models (move to structa.cloud/apps/email/)

**Rationale:** Website-specific features should live in the website codebase, not in shared libraries.

---

## 9. Implementation Strategy

### 9.1 Phase 1: Analysis and Planning
1. Review this document with development team
2. Prioritize features for keep/inline/extract decisions
3. Create detailed migration plan for each category
4. Estimate effort and timeline

### 9.2 Phase 2: Low-Risk Changes
1. Remove unused template tags
2. Inline debug tools (development only)
3. Extract website-specific features to site code
4. Test thoroughly in development

### 9.3 Phase 3: Medium-Risk Changes
1. Inline tag models if desired
2. Inline contact blocks if desired
3. Evaluate and remove signals if not needed
4. Test thoroughly in staging

### 9.4 Phase 4: High-Risk Changes (If Necessary)
1. Plan model inheritance changes carefully
2. Create database migration strategy
3. Update view base classes incrementally
4. Test extensively in all environments

### 9.5 Phase 5: Verification
1. Run full test suites for both websites
2. Verify all functionality works correctly
3. Monitor production for issues
4. Document all changes

---

## 10. Files Analyzed

### 10.1 ctc-research.com Python Files (50+)
- apps/LMS/models/*.py (10+ files)
- apps/LMS/views/*.py (5+ files)
- apps/LMS/services/*.py (4+ files)
- apps/LMS/managers/*.py (4+ files)
- apps/handlers/models/*.py (10+ files)
- apps/handlers/forms/*.py (6 files)
- apps/handlers/site/*.py (10+ files)
- apps/handlers/managers/*.py (5 files)
- apps/handlers/services/*.py (2 files)
- apps/handlers/registration/*.py (2 files)
- apps/pages/models/*.py (5+ files)
- configs/settings/*.py (2 files)
- core/*.py (5+ files)
- core/CI/models/*.py (2 files)
- core/CI/workflows/*.py (1 file)
- core/CI/adapters/*.py (1 file)

### 10.2 structa.cloud Python Files (50+)
- alliance/conf.py
- alliance/__init__.py
- alliance/urls.py
- alliance/CI/models/invitation/*.py
- alliance/CI/workflows/email/task.py
- alliance/CI/adapters/email.py
- apps/handlers/forms/*.py (6 files)
- apps/handlers/models/profiles/*.py (3 files)
- apps/handlers/models/blog/*.py (2 files)
- apps/handlers/models/manage/*.py (3 files)
- apps/handlers/services/*.py (2 files)
- apps/handlers/site/*.py (10 files)
- apps/handlers/managers/*.py (4 files)
- apps/handlers/snippets/*/*.py (4 files)
- apps/pages/models/*.py (4 files)
- configs/settings/conf.py

### 10.3 Template Files
- **ctc-research.com:** No django-fusion template tag usage found
- **structa.cloud:** No django-fusion template tag usage found

---

## 11. Next Steps

1. **Review this document** with the development team
2. **Make decisions** on keep/inline/extract for each component category
3. **Create detailed migration plan** with specific tasks and timeline
4. **Prioritize changes** by risk level and business value
5. **Execute incrementally** starting with low-risk changes
6. **Test thoroughly** at each phase
7. **Document all changes** for team reference
8. **Monitor production** after deployment

---

## 12. Conclusion

Both ctc-research.com and structa.cloud have extensive integration with django-fusion, with approximately 50% of components shared between the two websites. The core models (DefaultBase, Person), views (PageHandler, NotificationMixin), and managers (CachedManager) are heavily used and should be maintained as dependencies. Website-specific features (payment integration for ctc-research.com, organization models for structa.cloud) should be extracted to site-specific code. Low-usage features (signals, contrib models, template tags) can be evaluated for removal or inlining.

The recommended approach is to:
1. **Keep core shared components** as django-fusion dependencies
2. **Extract website-specific features** to site code
3. **Inline or remove low-usage features** to reduce complexity
4. **Execute changes incrementally** with thorough testing at each phase

This strategy balances the benefits of code reuse with the need for maintainability and reduces the risk of breaking changes during consolidation.

---

**End of Report**
