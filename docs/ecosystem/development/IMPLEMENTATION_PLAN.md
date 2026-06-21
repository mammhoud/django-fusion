# Implementation Plan: Ecosystem-Wide Architectural Refactoring

Generated: 2026-04-14 21:41:57

## Executive Summary

- **Total Phases**: 16
- **Total Tasks**: 122
- **Total Estimated Effort**: 581.0 hours
- **Estimated Duration**: 14.5 weeks (at 40 hrs/week)

## Dependency Graph

```
Phase 1: Analysis and Planning
  ↓
Phase 2: django_osoul (Pure Django Foundation)
  ↓
Phase 3: crafts_ai (Wagtail + Automation)
  ↓
Phase 4: django_osoul (Testing Infrastructure)
  ↓
Phase 5: nawaai (Pure Python Boundary)
  ↓
Phase 6: Domain Restructuring (App Renames)
  ↓
Phase 7: Project Simplification (Thin Layers)
  ↓
Phase 8: Naming Conventions
  ↓
Phase 9: Templates and Static Files
  ↓
Phase 10: Dependency Alignment
  ↓
Phase 11: Code Recovery and Merging
  ↓
Phase 12: Parsers and Serializers
  ↓
Phase 13: CI and Automation
  ↓
Phase 14: Documentation
  ↓
Phase 15: Migration Safety
  ↓
Phase 16: Final Validation
```

## Validation Checkpoints

After each phase, the following validations MUST pass:

1. **Boundary Check**: `import-linter --config .importlinter` returns zero violations
2. **Duplication Check**: `scripts/analyze_duplication.py --threshold 0.70` finds no new duplication
3. **Test Suite**: All tests pass in all packages and projects
4. **Import Check**: No ImportError or ModuleNotFoundError
5. **Git Status**: All changes committed with descriptive messages

## Rollback Strategy

Before each phase, a git tag is created for recovery:

- `rollback-phase-1-start`: Before Phase 1
- `rollback-phase-2-start`: Before Phase 2
- `rollback-phase-3-start`: Before Phase 3
- `rollback-phase-4-start`: Before Phase 4
- `rollback-phase-5-start`: Before Phase 5
- `rollback-phase-6-start`: Before Phase 6
- `rollback-phase-7-start`: Before Phase 7
- `rollback-phase-8-start`: Before Phase 8
- `rollback-phase-9-start`: Before Phase 9
- `rollback-phase-10-start`: Before Phase 10
- `rollback-phase-11-start`: Before Phase 11
- `rollback-phase-12-start`: Before Phase 12
- `rollback-phase-13-start`: Before Phase 13
- `rollback-phase-14-start`: Before Phase 14
- `rollback-phase-15-start`: Before Phase 15
- `rollback-phase-16-start`: Before Phase 16

To rollback to a previous phase:
```bash
git checkout <rollback-tag>
git reset --hard <rollback-tag>
```

## Detailed Phase Plans

### Phase 1: Analysis and Planning

**Rollback Point**: `rollback-phase-1-start`

**Estimated Effort**: 50.0 hours

**Tasks**: 14

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 1.1.1 | Task 1.1.1 | 8.0 | None |
| 1.1.2 | Task 1.1.2 | 4.0 | None |
| 1.1.3 | Task 1.1.3 | 3.0 | None |
| 1.1.4 | Task 1.1.4 | 2.0 | None |
| 1.2.1 | Task 1.2.1 | 6.0 | None |
| 1.2.2 | Task 1.2.2 | 3.0 | None |
| 1.2.3 | Task 1.2.3 | 4.0 | None |
| 1.2.4 | Task 1.2.4 | 2.0 | None |
| 1.3.1 | Task 1.3.1 | 4.0 | None |
| 1.3.2 | Task 1.3.2 | 2.0 | None |
| 1.4.1 | Task 1.4.1 | 6.0 | None |
| 1.4.2 | Task 1.4.2 | 3.0 | None |
| 1.4.3 | Task 1.4.3 | 1.0 | None |
| 1.4.4 | Task 1.4.4 | 2.0 | None |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 2: django_osoul — Extract Pure Django/Python Foundation

**Rollback Point**: `rollback-phase-2-start`

**Estimated Effort**: 72.0 hours

**Tasks**: 14

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 2.1 | Task 2.1 | 12.0 | 1.4 |
| 2.2 | Task 2.2 | 6.0 | 2.1 |
| 2.3 | Task 2.3 | 4.0 | 2.2 |
| 2.4 | Task 2.4 | 8.0 | 2.3 |
| 2.5 | Task 2.5 | 6.0 | 2.4 |
| 2.6 | Task 2.6 | 4.0 | 2.5 |
| 2.7 | Task 2.7 | 4.0 | 2.6 |
| 2.8 | Task 2.8 | 4.0 | 2.7 |
| 2.9 | Task 2.9 | 3.0 | 2.8 |
| 2.10 | Task 2.10 | 3.0 | 2.9 |
| 2.11 | Task 2.11 | 4.0 | 2.10 |
| 2.12 | Task 2.12 | 4.0 | 2.11 |
| 2.13 | Task 2.13 | 6.0 | 2.12 |
| 2.14 | Task 2.14 | 4.0 | 2.13 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 3: crafts_ai — Extract Wagtail + Automation Logic

**Rollback Point**: `rollback-phase-3-start`

**Estimated Effort**: 76.0 hours

**Tasks**: 17

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 3.1 | Task 3.1 | 8.0 | 2.14 |
| 3.2 | Task 3.2 | 8.0 | 3.1 |
| 3.3 | Task 3.3 | 6.0 | 3.2 |
| 3.4 | Task 3.4 | 6.0 | 3.3 |
| 3.5 | Task 3.5 | 4.0 | 3.4 |
| 3.6 | Task 3.6 | 4.0 | 3.5 |
| 3.7 | Task 3.7 | 6.0 | 3.6 |
| 3.8 | Task 3.8 | 4.0 | 3.7 |
| 3.9 | Task 3.9 | 3.0 | 3.8 |
| 3.10 | Task 3.10 | 4.0 | 3.9 |
| 3.11 | Task 3.11 | 3.0 | 3.10 |
| 3.12 | Task 3.12 | 3.0 | 3.11 |
| 3.13 | Task 3.13 | 3.0 | 3.12 |
| 3.14 | Task 3.14 | 3.0 | 3.13 |
| 3.15 | Task 3.15 | 3.0 | 3.14 |
| 3.16 | Task 3.16 | 4.0 | 3.15 |
| 3.17 | Task 3.17 | 4.0 | 3.16 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 4: django_osoul — Extract Testing Infrastructure and Health Checks

**Rollback Point**: `rollback-phase-4-start`

**Estimated Effort**: 50.0 hours

**Tasks**: 10

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 4.1 | Task 4.1 | 4.0 | 3.17 |
| 4.2 | Task 4.2 | 6.0 | 4.1 |
| 4.3 | Task 4.3 | 4.0 | 4.2 |
| 4.4 | Task 4.4 | 3.0 | 4.3 |
| 4.5 | Task 4.5 | 3.0 | 4.4 |
| 4.6 | Task 4.6 | 2.0 | 4.5 |
| 4.7 | Task 4.7 | 6.0 | 4.6 |
| 4.8 | Task 4.8 | 12.0 | 4.7 |
| 4.9 | Task 4.9 | 6.0 | 4.8 |
| 4.10 | Task 4.10 | 4.0 | 4.9 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 5: nawaai — Verify Pure Python Boundary

**Rollback Point**: `rollback-phase-5-start`

**Estimated Effort**: 8.0 hours

**Tasks**: 1

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 5.1 | Task 5.1 | 8.0 | 4.10 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 6: Domain Restructuring — App Renames and Module Reorganization

**Rollback Point**: `rollback-phase-6-start`

**Estimated Effort**: 68.0 hours

**Tasks**: 9

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 6.1 | Task 6.1 | 8.0 | 5.1 |
| 6.2 | Task 6.2 | 8.0 | 6.1 |
| 6.3 | Task 6.3 | 6.0 | 6.2 |
| 6.4 | Task 6.4 | 6.0 | 6.3 |
| 6.5 | Task 6.5 | 8.0 | 6.4 |
| 6.6 | Task 6.6 | 12.0 | 6.5 |
| 6.7 | Task 6.7 | 8.0 | 6.6 |
| 6.8 | Task 6.8 | 8.0 | 6.7 |
| 6.9 | Task 6.9 | 4.0 | 6.8 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 7: Project Simplification — Thin Layer Pattern

**Rollback Point**: `rollback-phase-7-start`

**Estimated Effort**: 40.0 hours

**Tasks**: 9

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 7.1 | Task 7.1 | 6.0 | 6.9 |
| 7.2 | Task 7.2 | 8.0 | 7.1 |
| 7.3 | Task 7.3 | 4.0 | 7.2 |
| 7.4 | Task 7.4 | 4.0 | 7.3 |
| 7.5 | Task 7.5 | 3.0 | 7.4 |
| 7.6 | Task 7.6 | 3.0 | 7.5 |
| 7.7 | Task 7.7 | 4.0 | 7.6 |
| 7.8 | Task 7.8 | 4.0 | 7.7 |
| 7.9 | Task 7.9 | 4.0 | 7.8 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 8: Cross-Project Consistency and Naming Conventions

**Rollback Point**: `rollback-phase-8-start`

**Estimated Effort**: 30.0 hours

**Tasks**: 5

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 8.1 | Task 8.1 | 6.0 | 7.9 |
| 8.2 | Task 8.2 | 6.0 | 8.1 |
| 8.3 | Task 8.3 | 6.0 | 8.2 |
| 8.4 | Task 8.4 | 4.0 | 8.3 |
| 8.5 | Task 8.5 | 8.0 | 8.4 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 9: Template Strategy and Static Files

**Rollback Point**: `rollback-phase-9-start`

**Estimated Effort**: 14.0 hours

**Tasks**: 3

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 9.1 | Task 9.1 | 6.0 | 8.5 |
| 9.2 | Task 9.2 | 4.0 | 9.1 |
| 9.3 | Task 9.3 | 4.0 | 9.2 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 10: Dependency Alignment and Version Unification

**Rollback Point**: `rollback-phase-10-start`

**Estimated Effort**: 20.0 hours

**Tasks**: 5

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 10.1 | Task 10.1 | 4.0 | 9.3 |
| 10.2 | Task 10.2 | 6.0 | 10.1 |
| 10.3 | Task 10.3 | 4.0 | 10.2 |
| 10.4 | Task 10.4 | 3.0 | 10.3 |
| 10.5 | Task 10.5 | 3.0 | 10.4 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 11: Code Recovery and Branch Merging

**Rollback Point**: `rollback-phase-11-start`

**Estimated Effort**: 40.0 hours

**Tasks**: 5

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 11.1 | Task 11.1 | 6.0 | 10.5 |
| 11.2 | Task 11.2 | 12.0 | 11.1 |
| 11.3 | Task 11.3 | 4.0 | 11.2 |
| 11.4 | Task 11.4 | 6.0 | 11.3 |
| 11.5 | Task 11.5 | 12.0 | 11.4 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 12: Parser and Serializer Requirements

**Rollback Point**: `rollback-phase-12-start`

**Estimated Effort**: 18.0 hours

**Tasks**: 3

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 12.1 | Task 12.1 | 4.0 | 11.5 |
| 12.2 | Task 12.2 | 6.0 | 12.1 |
| 12.3 | Task 12.3 | 8.0 | 12.2 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 13: Continuous Integration and Automated Validation

**Rollback Point**: `rollback-phase-13-start`

**Estimated Effort**: 12.0 hours

**Tasks**: 3

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 13.1 | Task 13.1 | 4.0 | 12.3 |
| 13.2 | Task 13.2 | 6.0 | 13.1 |
| 13.3 | Task 13.3 | 2.0 | 13.2 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 14: Documentation Organization and Spec Completion

**Rollback Point**: `rollback-phase-14-start`

**Estimated Effort**: 39.0 hours

**Tasks**: 10

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 14.1 | Task 14.1 | 6.0 | 13.3 |
| 14.2 | Task 14.2 | 4.0 | 14.1 |
| 14.3 | Task 14.3 | 4.0 | 14.2 |
| 14.4 | Task 14.4 | 4.0 | 14.3 |
| 14.5 | Task 14.5 | 4.0 | 14.4 |
| 14.6 | Task 14.6 | 3.0 | 14.5 |
| 14.7 | Task 14.7 | 4.0 | 14.6 |
| 14.8 | Task 14.8 | 4.0 | 14.7 |
| 14.9 | Task 14.9 | 4.0 | 14.8 |
| 14.10 | Task 14.10 | 2.0 | 14.9 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 15: Migration Safety and Reversibility

**Rollback Point**: `rollback-phase-15-start`

**Estimated Effort**: 16.0 hours

**Tasks**: 3

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 15.1 | Task 15.1 | 4.0 | 14.10 |
| 15.2 | Task 15.2 | 8.0 | 15.1 |
| 15.3 | Task 15.3 | 4.0 | 15.2 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed

### Phase 16: Final Validation and Deliverables

**Rollback Point**: `rollback-phase-16-start`

**Estimated Effort**: 28.0 hours

**Tasks**: 11

| Task ID | Title | Effort (hrs) | Dependencies |
|---------|-------|-------------|--------------|
| 16.1 | Task 16.1 | 2.0 | 15.3 |
| 16.2 | Task 16.2 | 2.0 | 16.1 |
| 16.3 | Task 16.3 | 4.0 | 16.2 |
| 16.4 | Task 16.4 | 4.0 | 16.3 |
| 16.5 | Task 16.5 | 2.0 | 16.4 |
| 16.6 | Task 16.6 | 2.0 | 16.5 |
| 16.7 | Task 16.7 | 2.0 | 16.6 |
| 16.8 | Task 16.8 | 2.0 | 16.7 |
| 16.9 | Task 16.9 | 2.0 | 16.8 |
| 16.10 | Task 16.10 | 4.0 | 16.9 |
| 16.11 | Task 16.11 | 2.0 | 16.10 |

**Validation Checkpoints**:

- [ ] All tasks completed
- [ ] Boundary check passes
- [ ] All tests pass
- [ ] No import errors
- [ ] Changes committed
