# Design Document: Django Codebase Refactoring

## Implementation Sequence Design

### Phase 1: Template Restoration Design
**Objective:** Restore HTML templates from structa.cloud to ctc-research

**Design Approach:**
1. **Template Copy Strategy**: Copy templates while ignoring last changed templates
2. **Structure Preservation**: Maintain template inheritance and structure
3. **Validation**: Test all restored templates for functionality
4. **Testing**: Verify template rendering and responsiveness

**Technical Implementation:**
- Use rsync or similar tool for template copying
- Preserve template inheritance chains
- Test with Django template test suite
- Verify responsive design across devices

### Phase 2: Email and Wagtail Integration Design
**2.1 Email Command System**
**Objective:** Implement CSV-based email testing with `test_email.csv`

**Design Approach:**
1. **CSV Parsing**: Parse `test_email.csv` for email/role data
2. **Role-based Templates**: Email templates based on user roles
3. **Delivery Tracking**: Track email delivery status
4. **Bulk Operations**: Support bulk email sending

**Technical Implementation:**
- Extend django-seed email service
- Create management commands for email operations
- Implement delivery tracking with database storage
- Add bounce and failure handling

**2.2 Wagtail Integration**
**Objective:** Integrate Wagtail CMS with role-based content management

**Design Approach:**
1. **Group Synchronization**: Sync Wagtail groups with email roles
2. **Permission Inheritance**: Implement role-based permission inheritance
3. **Content Access**: Group-based content access control
4. **Role Hierarchy**: Manage role hierarchy and permissions

**Technical Implementation:**
- Extend Wagtail group management
- Implement permission inheritance system
- Create role-based content access controls
- Test Wagtail-CMS integration

### Phase 3: Django Group/Role Management Design
**Objective:** Implement Django group and role management system

**Design Approach:**
1. **Group Creation**: Create Django groups from CSV roles
2. **Permission Inheritance**: Implement permission inheritance system
3. **Role Hierarchy**: Configure role hierarchy and permissions
4. **Access Control**: Test group-based access control

**Technical Implementation:**
- Extend Django's built-in group system
- Implement permission inheritance logic
- Create role hierarchy management
- Test access control functionality

### Phase 4: Privacy Policy Modal Design
**Objective:** Create HTMX-based privacy policy modal

**Design Approach:**
1. **HTMX Modal**: Create modal with HTMX integration
2. **Auth Integration**: Integrate with authentication pages
3. **Display Logic**: Implement modal display/hide functionality
4. **Consent Tracking**: Track user consent and versioning

**Technical Implementation:**
- Create HTMX modal component
- Integrate with Django authentication system
- Implement modal state management
- Add consent tracking and versioning

### Phase 5: Notes Profile Section Design
**Objective:** Enhance user profile with notes system

**Design Approach:**
1. **Database Persistence**: Store notes in database
2. **Modal Interface**: Create modal for note editing
3. **Real-time Updates**: Implement real-time updates
4. **User-specific Storage**: User-specific note storage

**Technical Implementation:**
- Create notes model with database persistence
- Implement modal-based note interface
- Add real-time update functionality
- Test note creation and editing

### Phase 6: Data Tags System Design
**Objective:** Implement tagging system for content organization

**Design Approach:**
1. **Tagging System**: Add tags to models
2. **Management Interface**: Create tag management interface
3. **Tag-based Filtering**: Implement tag-based filtering
4. **Search Functionality**: Add tag-based search

**Technical Implementation:**
- Extend models with tagging capability
- Create tag management interface
- Implement tag-based filtering logic
- Add search functionality with tags

### Phase 7: Import Fixes and Basic Checks Design
**Objective:** Fix import issues and run system checks

**Design Approach:**
1. **Import Fixes**: Fix all import statements
2. **Circular Imports**: Resolve circular import issues
3. **System Checks**: Run Django system checks
4. **Database Verification**: Verify database connections

**Technical Implementation:**
- Use automated import fixing tools
- Resolve circular import dependencies
- Run Django's built-in system checks
- Test database connectivity

### Phase 8: Dumped Data Fixes Design
**Objective:** Fix dumped data inconsistencies

**Design Approach:**
1. **Data Review**: Review dumped data for inconsistencies
2. **Relationship Verification**: Verify data relationships
3. **Integrity Fixes**: Fix data integrity issues
4. **Loading Testing**: Test data loading and validation

**Technical Implementation:**
- Use data validation tools
- Fix data relationship issues
- Implement data integrity checks
- Test data loading processes

### Phase 9: JSON Data Merging Design
**Objective:** Merge multiple JSON data files

**Design Approach:**
1. **File Merging**: Merge multiple JSON files
2. **Conflict Resolution**: Resolve data conflicts
3. **Dataset Creation**: Create comprehensive dataset
4. **Integrity Testing**: Test data loading and integrity

**Technical Implementation:**
- Implement JSON file merging logic
- Create conflict resolution strategies
- Build comprehensive dataset
- Test data integrity and loading

### Phase 10: Language Testing Design
**Objective:** Test language switching functionality

**Design Approach:**
1. **Language Switching**: Test language change functionality
2. **Content Verification**: Verify language-specific content
3. **URL Testing**: Test language URLs with curl
4. **Translation Accuracy**: Verify translation accuracy

**Technical Implementation:**
- Test Django's i18n functionality
- Verify language-specific content
- Use curl for URL testing
- Check translation accuracy

### Phase 11: Package Reorganization Design
**Objective:** Reorganize package structure

**Design Approach:**
1. **Structure Review**: Review current package structure
2. **Reorganization**: Reorganize packages logically
3. **Dependency Updates**: Update package dependencies
4. **Functionality Testing**: Test package functionality

**Technical Implementation:**
- Analyze current package structure
- Reorganize packages for better organization
- Update dependency management
- Test package functionality

### Phase 12: Import and Namespace Updates Design
**Objective:** Update import statements and namespaces

**Design Approach:**
1. **Import Updates**: Update all import statements
2. **Namespace Fixes**: Fix namespace conflicts
3. **Accuracy Verification**: Verify import accuracy
4. **Functionality Testing**: Test import functionality

**Technical Implementation:**
- Use automated import fixing
- Resolve namespace conflicts
- Verify import paths
- Test import functionality

### Phase 13: Comprehensive Testing Design
**Objective:** Run comprehensive test suite

**Design Approach:**
1. **Unit Tests**: Execute unit tests
2. **Integration Tests**: Run integration tests
3. **System Tests**: Perform system tests
4. **Failure Fixes**: Fix test failures

**Technical Implementation:**
- Run Django test suite
- Execute integration tests
- Perform system-level testing
- Fix any test failures

### Phase 14: Error and Log Management Design
**Objective:** Fix errors and manage system logs

**Design Approach:**
1. **Error Review**: Review and fix error logs
2. **Warning Resolution**: Resolve system warnings
3. **Logging Implementation**: Implement proper logging
4. **Log Cleanup**: Clean up log files

**Technical Implementation:**
- Analyze error logs
- Fix system warnings
- Implement structured logging
- Clean up log files

## Technical Architecture

### System Architecture
- **Frontend**: HTMX for dynamic updates
- **Backend**: Django with django-seed package
- **Database**: PostgreSQL with data integrity
- **Caching**: Redis for performance optimization

### Security Architecture
- **Authentication**: Django's built-in auth system
- **Authorization**: Role-based access control
- **Data Protection**: GDPR compliance
- **Logging**: Structured logging for audit trails

### Performance Architecture
- **Caching**: Multi-level caching strategy
- **Database Optimization**: Query optimization and indexing
- **Asset Optimization**: Static asset optimization
- **CDN Integration**: Content delivery network for static assets

## Success Metrics

### Performance Metrics
- Page load time: < 2 seconds
- Email delivery: < 5 seconds
- Database queries: < 100ms
- System response: < 200ms

### Quality Metrics
- 100% template functionality
- 99.9% email delivery rate
- 100% permission accuracy
- 0 errors in production logs

## Risk Mitigation

### Technical Risks
1. **Template Compatibility**: Test on staging environment first
2. **Email Delivery**: Use multiple email service providers
3. **Data Integrity**: Implement comprehensive backup strategy
4. **Performance**: Conduct load testing before deployment

### Project Risks
1. **Timeline**: Regular progress reviews and adjustments
2. **Integration**: Incremental integration with thorough testing
3. **Quality**: Automated testing at each implementation phase

## Implementation Timeline

### Week 1: Foundation
- Template restoration
- Email system setup
- Wagtail integration

### Week 2: Core Features
- Group/role management
- Privacy policy modal
- Notes system
- Data tagging

### Week 3: Data Management
- Import fixes
- Data merging
- Language testing

### Week 4: Optimization
- Package reorganization
- Import/namespace fixes
- Testing and debugging
- Error resolution

This design document follows the exact implementation sequence specified, providing detailed technical approaches for each phase.

## Optional Design Considerations

### Blog Maintenance Design (Optional)
**Objective:** Enhance blog functionality with Wagtail bakerydemo integration

**Design Approach:**
1. **Blog Post Management**: Add blog post creation/editing to user profiles
2. **Template Integration**: Use Wagtail bakerydemo templates for blog pages
3. **Tag System**: Implement comprehensive blog tagging and categorization
4. **Search Functionality**: Add blog search and filtering capabilities
5. **Social Features**: Implement comments, interactions, and social sharing

**Technical Implementation:**
- Extend user profiles with blog management interface
- Integrate Wagtail bakerydemo template resources
- Implement tag-based blog organization
- Add search functionality with Django Haystack or similar
- Create social sharing and comment systems

### Profile Section Fixes Design (Optional)
**Objective:** Improve user profile experience and functionality

**Design Approach:**
1. **Layout Enhancement**: Fix profile section layouts and responsiveness
2. **Completion Tracking**: Track profile completion progress
3. **Customization**: Add profile customization options
4. **Privacy Settings**: Implement granular privacy controls
5. **Analytics**: Add profile analytics and insights

**Technical Implementation:**
- Update profile template layouts
- Implement profile completion tracking system
- Add customization options with user preferences
- Create privacy settings management
- Build analytics dashboard for user profiles

### Wagtail Bakery Demo Integration Design (Optional)
**Objective:** Integrate Wagtail bakerydemo features for enhanced content management

**Design Approach:**
1. **Template Integration**: Use bakerydemo templates for content pages
2. **Page Models**: Create Wagtail page models for different content types
3. **Streamfields**: Implement streamfields for flexible content editing
4. **Tag System**: Add comprehensive tagging system
5. **SEO Features**: Implement SEO optimization features

**Technical Implementation:**
- Integrate bakerydemo template resources
- Create custom Wagtail page models
- Implement streamfield blocks for content
- Add tag management system
- Implement SEO features and sitemaps

### Services Template Enhancement Design (Optional)
**Objective:** Enhance services pages with advanced features

**Design Approach:**
1. **Wagtail Integration**: Update services template with Wagtail sections
2. **Categorization**: Add service categories and tags
3. **Filtering**: Implement service filtering and search
4. **Booking System**: Add service booking functionality
5. **Reviews**: Implement service reviews and ratings

**Technical Implementation:**
- Update services template with Wagtail streamfields
- Create service categorization system
- Implement filtering and search functionality
- Build booking system with calendar integration
- Add review and rating system

### Wagtail Page Model Implementation Design (Optional)
**Objective:** Implement advanced Wagtail page models for content management

**Design Approach:**
1. **Service Pages**: Create Wagtail page models for services
2. **Section Management**: Implement sections as streamfields
3. **Tagging System**: Add page tagging and categorization
4. **Versioning**: Implement page versioning system
5. **Workflow**: Add publishing workflow and approvals

**Technical Implementation:**
- Create Wagtail page models for different content types
- Implement streamfield sections for flexible layouts
- Add comprehensive tagging system
- Create versioning system for content changes
- Implement publishing workflow with approvals

## Integration Strategy

### Optional Features Integration
1. **Modular Approach**: Each optional feature as separate module
2. **Feature Flags**: Use feature flags to enable/disable optional features
3. **Progressive Enhancement**: Add features incrementally
4. **Testing Strategy**: Separate testing for optional features

### Resource Integration
1. **Wagtail Bakerydemo**: Use as template and model reference
2. **Template Resources**: Leverage existing template structures
3. **Code Patterns**: Follow established Wagtail patterns
4. **Best Practices**: Implement industry best practices

## Success Metrics for Optional Features

### Blog Maintenance Metrics
- Blog post creation time: < 5 minutes
- Blog search accuracy: > 95%
- User engagement: > 30% increase
- Social shares: > 20% increase

### Profile Enhancement Metrics
- Profile completion rate: > 80%
- User satisfaction: > 4.5/5 rating
- Customization usage: > 60% of users
- Privacy settings usage: > 70% of users

### Wagtail Integration Metrics
- Content creation time: 50% reduction
- Page load time: < 2 seconds
- SEO performance: > 90/100 score
- User satisfaction: > 4.5/5 rating

## Implementation Priority

### High Priority (Required)
- Phase 1-14: Core implementation sequence
- Email system and testing
- Permission and role management
- Basic template restoration

### Medium Priority (Recommended)
- Blog maintenance features
- Profile section fixes
- Basic Wagtail integration

### Low Priority (Optional)
- Advanced Wagtail bakerydemo features
- Services template enhancements
- Advanced page model implementations

This design document provides comprehensive coverage of both required and optional features, allowing for flexible implementation based on project priorities and resources.
