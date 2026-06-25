"""Command-line interface for the orchestrator."""

import argparse
import json
import logging
import sys
from typing import Optional

from .config import ConfigLoader, OrchestratorConfig
from .models import TaskStatus
from .orchestrator import SpecTaskOrchestrator

logger = logging.getLogger(__name__)


class OrchestratorCLI:
    """Command-line interface for the orchestrator."""

    def __init__(self):
        """Initialize the CLI."""
        self.orchestrator: Optional[SpecTaskOrchestrator] = None
        self.config: Optional[OrchestratorConfig] = None

    def setup_logging(self, log_level: str) -> None:
        """Setup logging."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def load_config(self, config_file: Optional[str] = None) -> OrchestratorConfig:
        """Load configuration."""
        loader = ConfigLoader()

        if config_file:
            loader.load_from_file(config_file)

        loader.load_from_env()

        try:
            loader.validate_config()
        except ValueError as e:
            logger.error(f"Configuration validation failed: {e}")
            sys.exit(1)

        self.config = loader.get_config()
        return self.config

    def initialize_orchestrator(self) -> SpecTaskOrchestrator:
        """Initialize the orchestrator."""
        if not self.config:
            self.load_config()

        self.orchestrator = SpecTaskOrchestrator(self.config)
        return self.orchestrator

    def cmd_scan(self, args) -> int:
        """Scan specs."""
        self.initialize_orchestrator()

        result = self.orchestrator.scan_specs(args.base_path)

        if result["success"]:
            print(f"Found {result['specs_found']} specs in {result['categories']}")
            if result["warnings"]:
                print(f"Warnings: {result['warnings']}")
            return 0
        else:
            print(f"Error: {result['error']}")
            return 1

    def cmd_load(self, args) -> int:
        """Load specs."""
        self.initialize_orchestrator()

        result = self.orchestrator.load_specs(args.base_path)

        if result["success"]:
            print(f"Loaded {result['loaded']} specs ({result['failed']} failed)")
            return 0
        else:
            print(f"Error: {result['error']}")
            return 1

    def cmd_list(self, args) -> int:
        """List specs."""
        self.initialize_orchestrator()
        self.orchestrator.load_specs(args.base_path)

        if args.category:
            specs = self.orchestrator.get_specs_by_category(args.category)
            print(f"Specs in {args.category}:")
        else:
            specs = self.orchestrator.get_all_specs()
            print("All specs:")

        for spec in specs:
            print(f"  {spec.category}/{spec.spec_name}")

        return 0

    def cmd_tasks(self, args) -> int:
        """List tasks."""
        self.initialize_orchestrator()
        self.orchestrator.load_specs(args.base_path)

        if args.category:
            tasks = self.orchestrator.get_tasks_by_category(args.category)
            print(f"Tasks in {args.category}:")
        elif args.status:
            status = TaskStatus(args.status)
            tasks = self.orchestrator.get_tasks_by_status(status)
            print(f"Tasks with status {args.status}:")
        else:
            tasks = self.orchestrator.tasks
            print("All tasks:")

        for task in tasks:
            print(f"  {task.id}: {task.description} ({task.status.value})")

        return 0

    def cmd_progress(self, args) -> int:
        """Show progress."""
        self.initialize_orchestrator()
        self.orchestrator.load_specs(args.base_path)

        if args.category and args.spec:
            report = self.orchestrator.get_spec_progress(args.category, args.spec)
            print(json.dumps(report, indent=2, default=str))
        elif args.category:
            summary = self.orchestrator.get_category_summary(args.category)
            print(json.dumps(summary, indent=2, default=str))
        else:
            summary = self.orchestrator.get_overall_summary()
            print(json.dumps(summary, indent=2, default=str))

        return 0

    def cmd_execute(self, args) -> int:
        """Execute a task."""
        self.initialize_orchestrator()
        self.orchestrator.load_specs(args.base_path)

        result = self.orchestrator.execute_task(args.task_id)

        print(json.dumps(result, indent=2, default=str))

        return 0 if result.get("status") == "completed" else 1

    def cmd_export(self, args) -> int:
        """Export specs."""
        self.initialize_orchestrator()
        self.orchestrator.load_specs(args.base_path)

        result = self.orchestrator.export_to_json(args.output)

        if result:
            print(f"Exported to {args.output}")
            return 0
        else:
            print(f"Error exporting to {args.output}")
            return 1

    def main(self, argv: Optional[list] = None) -> int:
        """Main entry point."""
        parser = argparse.ArgumentParser(
            description="Spec Task Orchestrator",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  orchestrator scan
  orchestrator load
  orchestrator list --category auth
  orchestrator tasks --category auth
  orchestrator progress --category auth --spec spec-name
  orchestrator execute --task-id 1
  orchestrator export --output specs.json
            """,
        )

        parser.add_argument(
            "--config",
            help="Configuration file (.config.kiro)",
        )

        parser.add_argument(
            "--base-path",
            default=".kiro/specs-organized",
            help="Base path for specs (default: .kiro/specs-organized)",
        )

        parser.add_argument(
            "--log-level",
            default="INFO",
            help="Log level (default: INFO)",
        )

        subparsers = parser.add_subparsers(dest="command", help="Command to execute")

        # Scan command
        subparsers.add_parser("scan", help="Scan specs")

        # Load command
        subparsers.add_parser("load", help="Load specs")

        # List command
        list_parser = subparsers.add_parser("list", help="List specs")
        list_parser.add_argument("--category", help="Filter by category")

        # Tasks command
        tasks_parser = subparsers.add_parser("tasks", help="List tasks")
        tasks_parser.add_argument("--category", help="Filter by category")
        tasks_parser.add_argument("--status", help="Filter by status")

        # Progress command
        progress_parser = subparsers.add_parser("progress", help="Show progress")
        progress_parser.add_argument("--category", help="Category")
        progress_parser.add_argument("--spec", help="Spec name")

        # Execute command
        execute_parser = subparsers.add_parser("execute", help="Execute a task")
        execute_parser.add_argument("--task-id", required=True, help="Task ID")

        # Export command
        export_parser = subparsers.add_parser("export", help="Export specs")
        export_parser.add_argument("--output", required=True, help="Output file")

        args = parser.parse_args(argv)

        self.setup_logging(args.log_level)
        self.load_config(args.config)

        if not args.command:
            parser.print_help()
            return 0

        command_method = getattr(self, f"cmd_{args.command}", None)
        if not command_method:
            print(f"Unknown command: {args.command}")
            return 1

        return command_method(args)


def main():
    """Main entry point."""
    cli = OrchestratorCLI()
    sys.exit(cli.main())


if __name__ == "__main__":
    main()
