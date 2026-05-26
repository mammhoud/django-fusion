# Tasks: {{SPEC_NAME}}

## Phase 1: [Phase Name]

- [ ] 1.1 [Task description]
  - [ ] 1.1.1 [Sub-task description]
  - [ ] 1.1.2 [Sub-task description]
  - [ ] 1.1.3 [Sub-task description]

- [ ] 1.2 [Task description]
  - [ ] 1.2.1 [Sub-task description]
  - [ ] 1.2.2 [Sub-task description]

- [ ] 1.3 [Task description]
  - [ ] 1.3.1 [Sub-task description]

## Phase 2: [Phase Name]

- [ ] 2.1 [Task description]
  - [ ] 2.1.1 [Sub-task description]
  - [ ] 2.1.2 [Sub-task description]

- [ ] 2.2 [Task description]
  - [ ] 2.2.1 [Sub-task description]
  - [ ] 2.2.2 [Sub-task description]
  - [ ] 2.2.3 [Sub-task description]

## Phase 3: [Phase Name]

- [ ] 3.1 [Task description]
  - [ ] 3.1.1 [Sub-task description]

- [ ] 3.2 [Task description]
  - [ ] 3.2.1 [Sub-task description]
  - [ ] 3.2.2 [Sub-task description]

## Phase 4: [Phase Name]

- [ ] 4.1 [Task description]
  - [ ] 4.1.1 [Sub-task description]

- [ ] 4.2 [Task description]
  - [ ] 4.2.1 [Sub-task description]
  - [ ] 4.2.2 [Sub-task description]

## Phase 5: Validation & Documentation

- [ ] 5.1 [Task description]
  - [ ] 5.1.1 [Sub-task description]
  - [ ] 5.1.2 [Sub-task description]

- [ ] 5.2 [Task description]
  - [ ] 5.2.1 [Sub-task description]

## Task Status Legend

| Marker | Meaning | When to Use |
|--------|---------|-------------|
| `[x]` | Completed | Task is fully complete and verified |
| `[ ]` | Not started | Task has not been started |
| `[-]` | In progress | Task is actively being worked on |
| `[~]` | Partially complete | Some sub-tasks are done, but not all |

## Task Dependencies

### Dependency Graph
```
1.1 → 1.2 → 1.3
     ↓
2.1 → 2.2 → 2.3
```

### Critical Path
- 1.1 → 1.2 → 2.1 → 2.2 → 3.1

## Task Verification

### Completion Criteria
Each task must meet these criteria before being marked `[x]`:
- [ ] Code is written and tested
- [ ] Tests pass (unit, integration, etc.)
- [ ] Documentation is updated
- [ ] Code review is completed (if applicable)
- [ ] Deployment is verified (if applicable)

### Quality Gates
- All tests must pass before moving to next phase
- Code coverage must meet minimum requirements
- Security scans must pass
- Performance benchmarks must be met

## Task Tracking

### Progress Metrics
- **Total Tasks**: {{TOTAL_TASKS}}
- **Completed Tasks**: {{COMPLETED_TASKS}}
- **Completion Percentage**: {{COMPLETION_PERCENTAGE}}

### Time Estimates
| Phase | Estimated Hours | Actual Hours | Variance |
|-------|----------------|--------------|----------|
| Phase 1 | [estimate] | [actual] | [variance] |
| Phase 2 | [estimate] | [actual] | [variance] |
| Phase 3 | [estimate] | [actual] | [variance] |
| Phase 4 | [estimate] | [actual] | [variance] |
| Phase 5 | [estimate] | [actual] | [variance] |

## Notes
- Add any additional notes about task execution
- Document any deviations from the plan
- Record lessons learned

---

**Created**: {{CREATION_DATE}}
**Last Updated**: {{LAST_UPDATED}}
**Total Tasks**: {{TOTAL_TASKS}}
**Completed**: {{COMPLETED_TASKS}}/{{TOTAL_TASKS}}
**Status**: {{COMPLETION_PERCENTAGE}} complete
