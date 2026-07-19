# Development Workflow

## Overview

This document describes the development workflow for the Xellent Website platform.

## Git Workflow

### Branch Strategy

We use a modified Git Flow strategy:

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: Feature branches
- **bugfix/**: Bug fix branches
- **hotfix/**: Production hotfixes

### Creating a Feature Branch

```bash
# Update develop branch
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feature/feature-name

# Make changes and commit
git add .
git commit -m "feat: add feature description"

# Push to remote
git push origin feature/feature-name
```

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Build/dependency changes

**Example**:
```
feat(auth): add JWT token refresh endpoint

- Add refresh token endpoint
- Implement token rotation
- Add tests for token refresh

Closes #123
```

## Development Process

### 1. Create Feature Branch

```bash
git checkout -b feature/user-authentication
```

### 2. Implement Feature

```bash
# Make changes
# Run tests
make test

# Format code
make format

# Run linting
make lint
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat(auth): implement user authentication"
```

### 4. Push to Remote

```bash
git push origin feature/user-authentication
```

### 5. Create Pull Request

- Go to GitHub
- Create pull request from feature branch to develop
- Add description and link related issues
- Request reviewers

### 6. Code Review

- Address review comments
- Make requested changes
- Push updates

### 7. Merge to Develop

- Squash commits if needed
- Merge to develop branch
- Delete feature branch

### 8. Deploy to Staging

```bash
git checkout develop
git pull origin develop
make deploy-staging
```

### 9. Merge to Main

After testing on staging:

```bash
git checkout main
git pull origin main
git merge develop
git push origin main
```

## Development Cycle

### Daily Development

```bash
# Start day
git checkout develop
git pull origin develop

# Create/switch to feature branch
git checkout feature/my-feature

# Make changes
# ... edit files ...

# Test changes
make test

# Format and lint
make format
make lint

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push changes
git push origin feature/my-feature
```

### Code Review Checklist

Before submitting a pull request:

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No console errors or warnings
- [ ] Performance impact assessed
- [ ] Security implications reviewed

### Reviewer Checklist

When reviewing code:

- [ ] Code is clear and maintainable
- [ ] Tests are comprehensive
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Documentation is complete
- [ ] Follows project conventions

## Testing Workflow

### Before Committing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov
```

### Continuous Integration

- Tests run automatically on pull requests
- Must pass before merging
- Coverage must not decrease

## Deployment Workflow

### Staging Deployment

```bash
# Deploy to staging
make deploy-staging

# Run smoke tests
make test-smoke

# Verify on staging
# https://staging.structa.cloud
```

### Production Deployment

```bash
# Deploy to production
make deploy-production

# Monitor logs
docker-compose logs -f

# Verify deployment
# https://site.structa.cloud
```

### Rollback

```bash
# Rollback to previous version
make rollback

# Or manually
git revert <commit-hash>
git push origin main
```

## Collaboration

### Communication

- Use GitHub issues for discussions
- Use pull request comments for code review
- Use Slack for urgent matters
- Document decisions in ADRs (Architecture Decision Records)

### Pair Programming

```bash
# Share screen or use VS Code Live Share
# Work together on complex features
# Improves code quality and knowledge sharing
```

### Code Ownership

- Each module has a primary owner
- Owners review changes to their modules
- Owners are responsible for maintenance

## Performance Optimization

### Profiling

```bash
# Profile management command
python -m cProfile -s cumulative manage.py migrate

# Profile with line_profiler
kernprof -l -v manage.py migrate
```

### Database Optimization

```bash
# Check slow queries
# Enable query logging in settings
# Use Django Debug Toolbar
# Analyze query plans
```

### Frontend Optimization

```bash
# Analyze bundle size
make css-analyze

# Purge unused CSS
make css-purge

# Minify assets
npm run build:production
```

## Documentation

### Code Documentation

```python
def calculate_score(answers: List[str], correct_answers: List[str]) -> float:
    """
    Calculate quiz score based on answers.

    Args:
        answers: List of user answers
        correct_answers: List of correct answers

    Returns:
        Score as percentage (0-100)

    Raises:
        ValueError: If answer lists have different lengths
    """
    if len(answers) != len(correct_answers):
        raise ValueError("Answer lists must have same length")

    correct = sum(1 for a, c in zip(answers, correct_answers) if a == c)
    return (correct / len(answers)) * 100
```

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When value is invalid
        TypeError: When type is wrong
    """
```

## Related Documentation

- [Testing Strategy](02-testing-strategy.md)
- [Code Standards and Conventions](03-code-standards-and-conventions.md)
- [Local Development Setup](../getting-started/02-local-development-setup.md)
