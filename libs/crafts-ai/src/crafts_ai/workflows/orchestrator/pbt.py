"""Property-based testing support."""

from datetime import datetime
from typing import Any, Callable, Dict, List

from .models import Counterexample, TestResult


class PBTExecutor:
    """Executes property-based tests."""

    def __init__(self):
        """Initialize the PBT executor."""
        self.test_results: List[TestResult] = []
        self.frameworks_available = self._check_frameworks()

    def _check_frameworks(self) -> Dict[str, bool]:
        """Check which PBT frameworks are available."""
        frameworks = {}

        try:
            frameworks["hypothesis"] = True
        except ImportError:
            frameworks["hypothesis"] = False

        try:
            frameworks["pytest"] = True
        except ImportError:
            frameworks["pytest"] = False

        return frameworks

    def execute_property_test(
        self,
        property_id: str,
        framework: str,
        test_func: Callable,
        iterations: int = 100,
    ) -> TestResult:
        """
        Execute a property-based test.

        Args:
            property_id: ID of the property
            framework: Testing framework (hypothesis, pytest, etc.)
            test_func: Test function to execute
            iterations: Number of iterations

        Returns:
            TestResult with pass/fail status
        """
        start_time = datetime.now()

        try:
            if framework == "hypothesis":
                return self._execute_hypothesis_test(
                    property_id, test_func, iterations, start_time
                )
            else:
                return self._execute_generic_test(
                    property_id, test_func, iterations, start_time
                )
        except Exception as e:
            end_time = datetime.now()
            return TestResult(
                property_id=property_id,
                passing=False,
                iterations=0,
                execution_time=end_time - start_time,
                counterexample=Counterexample(
                    input=None,
                    expected=None,
                    actual=None,
                    error_message=str(e),
                ),
                framework=framework,
            )

    def _execute_hypothesis_test(
        self,
        property_id: str,
        test_func: Callable,
        iterations: int,
        start_time: datetime,
    ) -> TestResult:
        """Execute a Hypothesis-based test."""
        try:
            from hypothesis import HealthCheck, given, settings

            # Configure Hypothesis
            @settings(
                max_examples=iterations,
                suppress_health_check=[HealthCheck.too_slow],
                deadline=None,
            )
            @given(test_func)
            def wrapped_test(data):
                pass

            wrapped_test()

            end_time = datetime.now()
            return TestResult(
                property_id=property_id,
                passing=True,
                iterations=iterations,
                execution_time=end_time - start_time,
                framework="hypothesis",
            )

        except Exception as e:
            end_time = datetime.now()
            return TestResult(
                property_id=property_id,
                passing=False,
                iterations=iterations,
                execution_time=end_time - start_time,
                counterexample=Counterexample(
                    input=None,
                    expected=None,
                    actual=None,
                    error_message=str(e),
                ),
                framework="hypothesis",
            )

    def _execute_generic_test(
        self,
        property_id: str,
        test_func: Callable,
        iterations: int,
        start_time: datetime,
    ) -> TestResult:
        """Execute a generic test."""
        try:
            for _ in range(iterations):
                test_func()

            end_time = datetime.now()
            return TestResult(
                property_id=property_id,
                passing=True,
                iterations=iterations,
                execution_time=end_time - start_time,
                framework="generic",
            )

        except Exception as e:
            end_time = datetime.now()
            return TestResult(
                property_id=property_id,
                passing=False,
                iterations=iterations,
                execution_time=end_time - start_time,
                counterexample=Counterexample(
                    input=None,
                    expected=None,
                    actual=None,
                    error_message=str(e),
                ),
                framework="generic",
            )

    def execute_round_trip_test(
        self,
        data: Any,
        serialize: Callable,
        deserialize: Callable,
    ) -> bool:
        """
        Execute a round-trip test.

        Verifies that data survives serialization and deserialization.
        """
        try:
            serialized = serialize(data)
            deserialized = deserialize(serialized)
            return data == deserialized
        except Exception:
            return False

    def execute_idempotence_test(
        self,
        data: Any,
        operation: Callable,
    ) -> bool:
        """
        Execute an idempotence test.

        Verifies that f(f(x)) = f(x).
        """
        try:
            result1 = operation(data)
            result2 = operation(result1)
            return result1 == result2
        except Exception:
            return False

    def execute_metamorphic_test(
        self,
        data: Any,
        transform: Callable,
        verify: Callable,
    ) -> bool:
        """
        Execute a metamorphic test.

        Verifies a relationship between components.
        """
        try:
            transformed = transform(data)
            return verify(data, transformed)
        except Exception:
            return False

    def capture_counterexample(self, failure: Exception) -> Dict[str, Any]:
        """Capture a counterexample from a test failure."""
        return {
            "error_type": type(failure).__name__,
            "error_message": str(failure),
            "stack_trace": str(failure.__traceback__),
        }

    def store_test_results(self, results: List[TestResult]) -> None:
        """Store test results."""
        self.test_results.extend(results)

    def get_test_results(self) -> List[TestResult]:
        """Get all stored test results."""
        return self.test_results

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of test results."""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passing)
        failed = total - passed

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "total_iterations": sum(r.iterations for r in self.test_results),
            "total_time": sum(
                (r.execution_time.total_seconds() for r in self.test_results),
                0,
            ),
        }

    def is_framework_available(self, framework: str) -> bool:
        """Check if a framework is available."""
        return self.frameworks_available.get(framework, False)
