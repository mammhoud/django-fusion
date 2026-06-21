"""Data models for the orchestrator."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Task status enumeration."""
    NOT_STARTED = "not_started"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class SpecStatus(Enum):
    """Spec status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class TestType(Enum):
    """Test type enumeration."""
    UNIT = "unit"
    PROPERTY = "property"
    INTEGRATION = "integration"


@dataclass
class SpecMetadata:
    """Metadata for a discovered spec."""
    category: str
    spec_name: str
    path: str
    requirements_path: Optional[str] = None
    design_path: Optional[str] = None
    tasks_path: Optional[str] = None
    bugfix_path: Optional[str] = None
    config_path: Optional[str] = None
    files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AcceptanceCriterion:
    """An acceptance criterion for a requirement."""
    id: str
    description: str
    testable: bool
    test_type: Optional[TestType] = None
    test_strategy: Optional[str] = None


@dataclass
class Requirement:
    """A requirement with user story and acceptance criteria."""
    id: str
    user_story: str
    acceptance_criteria: List[AcceptanceCriterion]
    traceability: List[str] = field(default_factory=list)


@dataclass
class PBTSpecification:
    """Property-based test specification."""
    framework: str
    iterations: int = 100
    patterns: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)


@dataclass
class ExecutionMetadata:
    """Metadata for task execution."""
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None
    success: bool = False
    error_message: Optional[str] = None
    user: Optional[str] = None
    environment: Optional[str] = None


@dataclass
class Task:
    """A task to be executed."""
    id: str
    description: str
    status: TaskStatus
    category: str
    spec_name: str
    spec_category: str
    requirements_traceability: List[str]
    dependencies: List[str] = field(default_factory=list)
    pbt_specification: Optional[PBTSpecification] = None
    execution_metadata: Optional[ExecutionMetadata] = None


@dataclass
class Counterexample:
    """A counterexample from a failed property test."""
    input: Any
    expected: Any
    actual: Any
    error_message: str
    stack_trace: Optional[str] = None


@dataclass
class TestResult:
    """Result of a test execution."""
    property_id: str
    passing: bool
    iterations: int
    execution_time: timedelta
    counterexample: Optional[Counterexample] = None
    framework: str = "hypothesis"


@dataclass
class CorrectnessProperty:
    """A correctness property to be verified."""
    id: str
    title: str
    statement: str
    validates: List[str]
    test_type: str
    framework: Optional[str] = None


@dataclass
class Design:
    """Design information for a spec."""
    overview: str
    key_principles: List[str]
    architecture: str
    components: List[str] = field(default_factory=list)
    data_models: List[str] = field(default_factory=list)
    correctness_properties: List[CorrectnessProperty] = field(default_factory=list)


@dataclass
class Spec:
    """A complete spec with all its data."""
    category: str
    spec_name: str
    introduction: str
    glossary: Dict[str, str]
    requirements: List[Requirement]
    design: Optional[Design] = None
    tasks: List[Task] = field(default_factory=list)
    status: SpecStatus = SpecStatus.NOT_STARTED
    progress: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    owner: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert spec to dictionary."""
        return {
            "category": self.category,
            "spec_name": self.spec_name,
            "introduction": self.introduction,
            "glossary": self.glossary,
            "requirements": [
                {
                    "id": r.id,
                    "user_story": r.user_story,
                    "acceptance_criteria": [
                        {
                            "id": ac.id,
                            "description": ac.description,
                            "testable": ac.testable,
                            "test_type": ac.test_type.value if ac.test_type else None,
                            "test_strategy": ac.test_strategy,
                        }
                        for ac in r.acceptance_criteria
                    ],
                    "traceability": r.traceability,
                }
                for r in self.requirements
            ],
            "design": {
                "overview": self.design.overview,
                "key_principles": self.design.key_principles,
                "architecture": self.design.architecture,
                "components": self.design.components,
                "data_models": self.design.data_models,
                "correctness_properties": [
                    {
                        "id": p.id,
                        "title": p.title,
                        "statement": p.statement,
                        "validates": p.validates,
                        "test_type": p.test_type,
                        "framework": p.framework,
                    }
                    for p in self.design.correctness_properties
                ],
            } if self.design else None,
            "tasks": [
                {
                    "id": t.id,
                    "description": t.description,
                    "status": t.status.value,
                    "category": t.category,
                    "spec_name": t.spec_name,
                    "spec_category": t.spec_category,
                    "requirements_traceability": t.requirements_traceability,
                    "dependencies": t.dependencies,
                    "pbt_specification": {
                        "framework": t.pbt_specification.framework,
                        "iterations": t.pbt_specification.iterations,
                        "patterns": t.pbt_specification.patterns,
                        "properties": t.pbt_specification.properties,
                    } if t.pbt_specification else None,
                }
                for t in self.tasks
            ],
            "status": self.status.value,
            "progress": self.progress,
            "last_updated": self.last_updated.isoformat(),
            "owner": self.owner,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Spec":
        """Create spec from dictionary."""
        requirements = [
            Requirement(
                id=r["id"],
                user_story=r["user_story"],
                acceptance_criteria=[
                    AcceptanceCriterion(
                        id=ac["id"],
                        description=ac["description"],
                        testable=ac["testable"],
                        test_type=TestType(ac["test_type"]) if ac.get("test_type") else None,
                        test_strategy=ac.get("test_strategy"),
                    )
                    for ac in r["acceptance_criteria"]
                ],
                traceability=r.get("traceability", []),
            )
            for r in data.get("requirements", [])
        ]

        design = None
        if data.get("design"):
            d = data["design"]
            design = Design(
                overview=d["overview"],
                key_principles=d["key_principles"],
                architecture=d["architecture"],
                components=d.get("components", []),
                data_models=d.get("data_models", []),
                correctness_properties=[
                    CorrectnessProperty(
                        id=p["id"],
                        title=p["title"],
                        statement=p["statement"],
                        validates=p["validates"],
                        test_type=p["test_type"],
                        framework=p.get("framework"),
                    )
                    for p in d.get("correctness_properties", [])
                ],
            )

        tasks = [
            Task(
                id=t["id"],
                description=t["description"],
                status=TaskStatus(t["status"]),
                category=t["category"],
                spec_name=t["spec_name"],
                spec_category=t["spec_category"],
                requirements_traceability=t["requirements_traceability"],
                dependencies=t.get("dependencies", []),
                pbt_specification=PBTSpecification(
                    framework=t["pbt_specification"]["framework"],
                    iterations=t["pbt_specification"].get("iterations", 100),
                    patterns=t["pbt_specification"].get("patterns", []),
                    properties=t["pbt_specification"].get("properties", []),
                ) if t.get("pbt_specification") else None,
            )
            for t in data.get("tasks", [])
        ]

        return cls(
            category=data["category"],
            spec_name=data["spec_name"],
            introduction=data["introduction"],
            glossary=data.get("glossary", {}),
            requirements=requirements,
            design=design,
            tasks=tasks,
            status=SpecStatus(data.get("status", "not_started")),
            progress=data.get("progress", 0.0),
            last_updated=datetime.fromisoformat(data["last_updated"]) if "last_updated" in data else datetime.now(),
            owner=data.get("owner"),
        )
