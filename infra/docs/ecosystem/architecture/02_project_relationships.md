# Project Relationships

How projects interact and depend on each other.

## Project Dependencies

```
ctc-research
├── Depends on: None (standalone)
├── Used by: structa (data source)
└── Integrates with: blinko (knowledge base)

structa
├── Depends on: ctc-research (data API)
├── Used by: None
└── Integrates with: blinko (visualization)

blinko
├── Depends on: ctc-research (research data)
├── Used by: None
└── Integrates with: structa (data visualization)
```

## Data Flow Between Projects

### ctc-research → structa

**Purpose**: Provide research data for visualization

**Data Types**:
- Research datasets
- Analysis results
- Metadata

**API Endpoints**:
- `/api/datasets/` - List available datasets
- `/api/datasets/{id}/` - Get dataset details
- `/api/analysis/` - Get analysis results

### ctc-research → blinko

**Purpose**: Store and retrieve research notes

**Data Types**:
- Notes and annotations
- References and citations
- Tags and categories

**API Endpoints**:
- `/api/notes/` - Manage notes
- `/api/tags/` - Manage tags
- `/api/references/` - Manage references

### structa → blinko

**Purpose**: Embed visualizations in notes

**Data Types**:
- Visualization configurations
- Chart data
- Interactive elements

**Integration Points**:
- Embed API
- Widget system
- Data export

## Shared Infrastructure

### Database
- PostgreSQL instance shared across projects
- Separate schemas for each project
- Cross-project queries where needed

### Cache Layer
- Redis for session management
- Shared cache for common data
- Cache invalidation strategies

### Authentication
- Centralized authentication service
- JWT token validation
- Single sign-on (SSO)

### File Storage
- Shared file storage system
- Upload/download endpoints
- File versioning

## Communication Patterns

### Synchronous Communication
- REST API calls
- Direct database queries
- Real-time updates

### Asynchronous Communication
- Message queues (Celery)
- Event streaming
- Webhooks

### Event-Driven Architecture
- Project events published to message bus
- Other projects subscribe to relevant events
- Decoupled communication

## Integration Points

### API Gateway
- Single entry point for all APIs
- Request routing
- Rate limiting
- Authentication

### Service Discovery
- Dynamic service registration
- Load balancing
- Health checks

### Configuration Management
- Centralized configuration
- Environment-specific settings
- Feature flags

## Deployment Coordination

### Dependency Order
1. Database setup
2. ctc-research backend
3. structa backend (if applicable)
4. blinko backend
5. Frontend services

### Version Compatibility
- API versioning strategy
- Backward compatibility
- Migration procedures

### Rollback Procedures
- Coordinated rollbacks
- Data consistency checks
- Fallback mechanisms

## Next Steps

- Review [Technology Stack](03-technology-stack.md)
- Check [Entry Points](04-entry-points.md)
- See [System Overview](01-system-overview.md)
