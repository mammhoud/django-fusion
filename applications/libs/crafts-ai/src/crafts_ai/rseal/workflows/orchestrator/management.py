"""Integration with management scripts."""

import json
import subprocess
from typing import Any, Dict, List, Optional, Tuple


class ManagementScriptRunner:
    """Runs and integrates with management scripts."""

    def __init__(self, script_paths: Optional[Dict[str, str]] = None):
        """
        Initialize the runner.

        Args:
            script_paths: Dictionary mapping script names to their paths
        """
        self.script_paths = script_paths or {}
        self.execution_log: List[Dict[str, Any]] = []

    def run_script(self, script_name: str, args: List[str]) -> Dict[str, Any]:
        """
        Run a management script.

        Args:
            script_name: Name of the script (e.g., 'manage-specs.sh')
            args: Arguments to pass to the script

        Returns:
            Dictionary with script output and status
        """
        script_path = self.script_paths.get(script_name)

        if not script_path:
            return {
                "success": False,
                "error": f"Script path not configured: {script_name}",
            }

        try:
            cmd = [script_path] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            output = {
                "script": script_name,
                "args": args,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

            self.execution_log.append(output)
            return output

        except subprocess.TimeoutExpired:
            return {
                "script": script_name,
                "success": False,
                "error": "Script execution timed out",
            }
        except Exception as e:
            return {
                "script": script_name,
                "success": False,
                "error": str(e),
            }

    def list_specs(self, category: Optional[str] = None) -> List[str]:
        """List specs in a category or all categories."""
        args = ["list"]
        if category:
            args.append(category)

        result = self.run_script("manage-specs.sh", args)

        if result.get("success"):
            # Parse output
            specs = []
            for line in result.get("stdout", "").split("\n"):
                if line.strip():
                    specs.append(line.strip())
            return specs

        return []

    def check_duplicates(self) -> Dict[str, List[Tuple[str, str]]]:
        """Check for duplicate specs."""
        result = self.run_script("check-duplicates.py", [])

        if result.get("success"):
            try:
                return json.loads(result.get("stdout", "{}"))
            except json.JSONDecodeError:
                return {}

        return {}

    def find_similar_specs(self, spec_name: str) -> List[Tuple[str, str]]:
        """Find similar specs by name."""
        result = self.run_script("check-duplicates.py", ["--find-similar", spec_name])

        if result.get("success"):
            try:
                data = json.loads(result.get("stdout", "[]"))
                return [(item[0], item[1]) for item in data]
            except (json.JSONDecodeError, TypeError):
                return []

        return []

    def suggest_category(self, spec_name: str) -> List[str]:
        """Suggest category for a new spec."""
        result = self.run_script("check-duplicates.py", ["--suggest-category", spec_name])

        if result.get("success"):
            try:
                return json.loads(result.get("stdout", "[]"))
            except json.JSONDecodeError:
                return []

        return []

    def add_category_context(self, category: str, spec_name: str) -> bool:
        """Add category context to a spec."""
        result = self.run_script(
            "add-category-context.py",
            ["--category", category, "--spec", spec_name],
        )

        return result.get("success", False)

    def get_stats(self) -> Dict[str, Any]:
        """Get spec statistics."""
        result = self.run_script("manage-specs.sh", ["stats"])

        if result.get("success"):
            try:
                return json.loads(result.get("stdout", "{}"))
            except json.JSONDecodeError:
                return {}

        return {}

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get execution log of all script calls."""
        return self.execution_log

    def clear_execution_log(self) -> None:
        """Clear execution log."""
        self.execution_log = []
