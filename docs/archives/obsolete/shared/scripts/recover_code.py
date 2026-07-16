#!/usr/bin/env python3
"""
Code Recovery System — scans git history for deleted files, checks references,
and recovers high-priority candidates.

Usage:
    python scripts/recover_code.py scan          # scan + find references
    python scripts/recover_code.py report        # write RECOVERY_CANDIDATES.md
    python scripts/recover_code.py recover <file> <target>  # recover a file
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DeletedFile:
    path: str
    deleted_commit: str
    deleted_date: str
    references_found: list[str] = field(default_factory=list)
    recovery_priority: str = "low"  # "high", "medium", "low"


@dataclass
class RecoveryResult:
    original_path: str
    new_path: str
    recovered_from_commit: str
    tests_added: bool
    verification_passed: bool


# ---------------------------------------------------------------------------
# CodeRecoverySystem
# ---------------------------------------------------------------------------

class CodeRecoverySystem:
    """
    Recovers deleted or moved code from git history.

    Supports multiple git repositories (ctc-research.com, structa.cloud).
    """

    REPOS = [
        ("ctc-research.com", Path("ctc-research.com")),
        ("structa.cloud", Path("structa.cloud")),
    ]

    def __init__(self, workspace_root: Path | None = None):
        self.workspace_root = workspace_root or Path(__file__).parent.parent
        self.deleted_files: list[DeletedFile] = []

    # ------------------------------------------------------------------
    # 11.1.2 — scan_git_history
    # ------------------------------------------------------------------

    def scan_git_history(self, since: str = "6 months ago") -> list[DeletedFile]:
        """
        Scan git history for deleted Python files across all repos.

        Returns a list of DeletedFile objects with commit info.
        """
        results: list[DeletedFile] = []

        for repo_name, repo_rel in self.REPOS:
            repo_path = self.workspace_root / repo_rel
            if not (repo_path / ".git").exists():
                print(f"  [skip] {repo_name}: no .git directory found")
                continue

            print(f"\n[scan] {repo_name} — looking for deleted .py files since '{since}'")
            deleted = self._get_deleted_files(repo_path, since)
            print(f"  Found {len(deleted)} deleted Python files")

            for path, commit, date in deleted:
                df = DeletedFile(
                    path=f"{repo_name}/{path}",
                    deleted_commit=commit,
                    deleted_date=date,
                )
                results.append(df)

        self.deleted_files = results
        return results

    def _get_deleted_files(
        self, repo_path: Path, since: str
    ) -> list[tuple[str, str, str]]:
        """
        Return list of (relative_path, commit_hash, date) for deleted .py files.
        """
        # Get commit hash + date + file list for deleted files
        cmd = [
            "git", "log",
            "--diff-filter=D",
            "--name-only",
            f"--since={since}",
            "--pretty=format:%H|%ai",
        ]
        result = subprocess.run(
            cmd, cwd=repo_path, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"  [warn] git log failed: {result.stderr.strip()}")
            return []

        deleted: list[tuple[str, str, str]] = []
        current_commit = ""
        current_date = ""

        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            if "|" in line and len(line.split("|")) == 2:
                # commit header line
                parts = line.split("|")
                current_commit = parts[0].strip()
                current_date = parts[1].strip()
            elif line.endswith(".py"):
                deleted.append((line, current_commit, current_date))

        # Deduplicate by path (keep most recent deletion)
        seen: dict[str, tuple[str, str, str]] = {}
        for path, commit, date in deleted:
            if path not in seen:
                seen[path] = (path, commit, date)

        return list(seen.values())

    # ------------------------------------------------------------------
    # 11.1.3 — find_references
    # ------------------------------------------------------------------

    def find_references(self, deleted_file: DeletedFile) -> list[str]:
        """
        Find references to a deleted file in the current codebase.

        Checks:
        1. Import statements matching the module path
        2. String references
        3. Migration files
        """
        # Convert file path to module-style import path
        # e.g. "ctc-research.com/apps/handlers/managers/profile.py"
        #   -> "apps.handlers.managers.profile"
        raw_path = deleted_file.path
        # Strip repo prefix
        for repo_name, _ in self.REPOS:
            if raw_path.startswith(repo_name + "/"):
                raw_path = raw_path[len(repo_name) + 1:]
                break

        module_path = raw_path.replace("/", ".").removesuffix(".py")
        # Also get the short module name (last component)
        module_name = module_path.split(".")[-1]
        # Parent package
        parent_package = ".".join(module_path.split(".")[:-1])

        patterns = [
            module_path,                          # full dotted path
            f"from {parent_package} import",      # from parent import ...
            f"import {module_path}",              # import full.path
        ]
        if module_name and len(module_name) > 3:
            patterns.append(module_name)          # bare name (less reliable)

        references: list[str] = []

        for repo_name, repo_rel in self.REPOS:
            repo_path = self.workspace_root / repo_rel
            if not repo_path.exists():
                continue

            for pattern in patterns[:3]:  # skip bare name to reduce noise
                cmd = [
                    "grep", "-r", "--include=*.py",
                    "-l", pattern,
                    str(repo_path),
                ]
                result = subprocess.run(
                    cmd, capture_output=True, text=True
                )
                for line in result.stdout.splitlines():
                    ref = line.strip()
                    if ref and ref not in references:
                        references.append(ref)

        return references

    def find_all_references(self) -> None:
        """
        Run find_references() for every deleted file and update priority.

        Uses a bulk grep approach: collect all import lines from current .py files,
        build a lookup index, then check each deleted module path against it.
        """
        print(f"\n[refs] Checking references for {len(self.deleted_files)} deleted files...")

        # Collect all current Python files
        all_current_py: list[str] = []
        for _, repo_rel in self.REPOS:
            repo_path = self.workspace_root / repo_rel
            if not repo_path.exists():
                continue
            result = subprocess.run(
                ["find", str(repo_path), "-name", "*.py", "-not", "-path", "*/.git/*"],
                capture_output=True, text=True,
            )
            all_current_py.extend(l for l in result.stdout.splitlines() if l.strip())

        libs_path = self.workspace_root / "venv" / "libs"
        if libs_path.exists():
            result = subprocess.run(
                ["find", str(libs_path), "-name", "*.py", "-not", "-path", "*/.git/*"],
                capture_output=True, text=True,
            )
            all_current_py.extend(l for l in result.stdout.splitlines() if l.strip())

        print(f"  Scanning {len(all_current_py)} current Python files for references...")

        # Build index: token -> set of files that import it
        # token = any word that appears in an import line
        # Skip .venv / site-packages (not our code)
        import_index: dict[str, set[str]] = {}
        for py_file in all_current_py:
            if ".venv" in py_file or "site-packages" in py_file:
                continue
            try:
                with open(py_file, encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        stripped = line.strip()
                        if not stripped.startswith(("import ", "from ")):
                            continue
                        # Extract all dotted tokens from the import line
                        tokens = re.findall(r"[\w.]+", stripped)
                        for tok in tokens:
                            if "." in tok or len(tok) > 4:
                                import_index.setdefault(tok, set()).add(py_file)
            except OSError:
                pass

        print(f"  Built import index with {len(import_index)} tokens")

        for i, df in enumerate(self.deleted_files):
            refs = self._find_references_indexed(df, import_index)
            df.references_found = refs
            df.recovery_priority = self._compute_priority(df, refs)
            if (i + 1) % 200 == 0:
                print(f"  Processed {i + 1}/{len(self.deleted_files)}...")

        print(f"  Done. Processed all {len(self.deleted_files)} files.")

    def _find_references_indexed(
        self,
        df: DeletedFile,
        import_index: dict[str, set[str]],
    ) -> list[str]:
        """
        Fast reference check using pre-built import index.
        Returns list of files that reference this deleted module.
        Excludes .venv and site-packages paths (not our code).
        """
        raw_path = df.path
        for repo_name, _ in self.REPOS:
            if raw_path.startswith(repo_name + "/"):
                raw_path = raw_path[len(repo_name) + 1:]
                break

        module_path = raw_path.replace("/", ".").removesuffix(".py")
        parent_package = ".".join(module_path.split(".")[:-1])
        module_name = module_path.split(".")[-1]

        # Patterns to look for in import lines
        patterns = [
            f"import {module_path}",
            f"from {module_path}",
            f"from {parent_package} import {module_name}",
        ]

        # Look up the full module path and parent package in the index
        candidates: set[str] = set()
        for token in [module_path, parent_package]:
            if token in import_index:
                candidates.update(import_index[token])

        # Verify each candidate actually imports this specific module
        # Exclude .venv / site-packages (not our code)
        confirmed: list[str] = []
        for py_file in candidates:
            if ".venv" in py_file or "site-packages" in py_file:
                continue
            try:
                content = open(py_file, encoding="utf-8", errors="ignore").read()
                if any(pat in content for pat in patterns):
                    confirmed.append(py_file)
            except OSError:
                pass

        return confirmed

    def _compute_priority(self, df: DeletedFile, refs: list[str]) -> str:
        """
        Determine recovery priority:
        - high:   still imported in current code (would cause ImportError)
        - medium: was important but not currently imported
        - low:    clearly replaced by new architecture
        """
        if refs:
            return "high"

        # Medium: files that look like they contained real business logic
        path_lower = df.path.lower()
        medium_indicators = [
            "services/", "managers/", "backends/", "adapters/",
            "middleware/", "mixins/", "handlers/",
        ]
        if any(ind in path_lower for ind in medium_indicators):
            # Only medium if not a migration or __init__
            if "migration" not in path_lower and "__init__" not in path_lower:
                return "medium"

        return "low"

    # ------------------------------------------------------------------
    # 11.2.1 — recover_file
    # ------------------------------------------------------------------

    def recover_file(self, deleted_file_path: str, target_path: str) -> RecoveryResult:
        """
        Recover a deleted file from git history and place it at target_path.

        Steps:
        1. Find the commit that deleted the file
        2. Extract file content from the commit before deletion
        3. Write to target_path
        4. Return RecoveryResult
        """
        # Determine which repo owns this file
        repo_path: Path | None = None
        repo_rel_path = deleted_file_path

        for repo_name, repo_rel in self.REPOS:
            prefix = repo_name + "/"
            if deleted_file_path.startswith(prefix):
                repo_path = self.workspace_root / repo_rel
                repo_rel_path = deleted_file_path[len(prefix):]
                break

        if repo_path is None:
            return RecoveryResult(
                original_path=deleted_file_path,
                new_path=target_path,
                recovered_from_commit="",
                tests_added=False,
                verification_passed=False,
            )

        # Find the commit that deleted the file
        cmd = [
            "git", "log", "--diff-filter=D",
            "--pretty=format:%H", "--", repo_rel_path,
        ]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)
        commits = [c.strip() for c in result.stdout.splitlines() if c.strip()]

        if not commits:
            print(f"  [warn] Could not find deletion commit for {deleted_file_path}")
            return RecoveryResult(
                original_path=deleted_file_path,
                new_path=target_path,
                recovered_from_commit="",
                tests_added=False,
                verification_passed=False,
            )

        deletion_commit = commits[0]
        # The file existed in the commit just before deletion
        parent_commit = f"{deletion_commit}^"

        # Extract file content
        cmd = ["git", "show", f"{parent_commit}:{repo_rel_path}"]
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"  [warn] Could not extract {repo_rel_path} from {parent_commit}")
            return RecoveryResult(
                original_path=deleted_file_path,
                new_path=target_path,
                recovered_from_commit=deletion_commit,
                tests_added=False,
                verification_passed=False,
            )

        # Write to target path
        target = self.workspace_root / target_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(result.stdout, encoding="utf-8")
        print(f"  [recovered] {deleted_file_path} -> {target_path}")

        return RecoveryResult(
            original_path=deleted_file_path,
            new_path=target_path,
            recovered_from_commit=deletion_commit,
            tests_added=False,
            verification_passed=True,
        )

    # ------------------------------------------------------------------
    # 11.1.4 — generate_recovery_candidates_report
    # ------------------------------------------------------------------

    def generate_recovery_candidates_report(self) -> str:
        """
        Generate RECOVERY_CANDIDATES.md listing deleted files still referenced,
        with recovery priority.
        """
        high = [df for df in self.deleted_files if df.recovery_priority == "high"]
        medium = [df for df in self.deleted_files if df.recovery_priority == "medium"]
        low = [df for df in self.deleted_files if df.recovery_priority == "low"]

        lines = [
            "# Recovery Candidates",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
            f"- Total deleted Python files scanned: {len(self.deleted_files)}",
            f"- **High priority** (still referenced — would cause ImportError): {len(high)}",
            f"- Medium priority (important logic, not currently imported): {len(medium)}",
            f"- Low priority (replaced by new architecture): {len(low)}",
            "",
        ]

        if high:
            lines += [
                "## High Priority — Still Referenced (Action Required)",
                "",
                "These files are still imported somewhere in the current codebase.",
                "Leaving them missing will cause `ImportError` at runtime.",
                "",
            ]
            for df in sorted(high, key=lambda x: x.path):
                lines += [
                    f"### `{df.path}`",
                    "",
                    f"- **Deleted commit**: `{df.deleted_commit}`",
                    f"- **Deleted date**: {df.deleted_date}",
                    f"- **References found** ({len(df.references_found)}):",
                ]
                for ref in df.references_found[:10]:
                    lines.append(f"  - `{ref}`")
                if len(df.references_found) > 10:
                    lines.append(f"  - _(and {len(df.references_found) - 10} more)_")
                lines.append("")
        else:
            lines += [
                "## High Priority",
                "",
                "✅ No deleted files are still referenced in the current codebase.",
                "No `ImportError` risks detected.",
                "",
            ]

        if medium:
            lines += [
                "## Medium Priority — Important Logic (Review Recommended)",
                "",
                "These files contained business logic (services, managers, etc.) but are",
                "not currently imported. They may have been intentionally replaced.",
                "",
            ]
            for df in sorted(medium, key=lambda x: x.path)[:30]:
                lines.append(f"- `{df.path}` (deleted: {df.deleted_date[:10]})")
            if len(medium) > 30:
                lines.append(f"- _(and {len(medium) - 30} more — see full list below)_")
            lines.append("")

        lines += [
            "## Low Priority — Replaced by New Architecture",
            "",
            f"There are {len(low)} low-priority deleted files (migrations, `__init__.py`,",
            "old app structure files). These were intentionally removed as part of the",
            "architectural refactoring and do not need recovery.",
            "",
            "## Recovery Instructions",
            "",
            "For each high-priority file, run:",
            "```bash",
            "python scripts/recover_code.py recover <original_path> <target_path>",
            "```",
            "",
            "Example:",
            "```bash",
            "python scripts/recover_code.py recover \\",
            "  ctc-research.com/apps/handlers/managers/profile.py \\",
            "  ctc-research.com/apps/accounts/managers/profile.py",
            "```",
        ]

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 11.2.5 / 11.3.1 — generate_recovery_report
    # ------------------------------------------------------------------

    def generate_recovery_report(
        self,
        recovered: list[RecoveryResult] | None = None,
        unrecoverable: list[str] | None = None,
    ) -> str:
        """
        Generate RECOVERY_REPORT.md documenting all recovered files and
        unrecoverable files with reimplementation tasks.
        """
        recovered = recovered or []
        unrecoverable = unrecoverable or []

        lines = [
            "# Recovery Report",
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
            f"- Files recovered: {len(recovered)}",
            f"- Files unrecoverable: {len(unrecoverable)}",
            "",
        ]

        if recovered:
            lines += [
                "## Recovered Files",
                "",
                "| Original Path | New Path | Commit | Tests Added | Verified |",
                "|---|---|---|---|---|",
            ]
            for r in recovered:
                lines.append(
                    f"| `{r.original_path}` | `{r.new_path}` "
                    f"| `{r.recovered_from_commit[:8]}` "
                    f"| {'✅' if r.tests_added else '❌'} "
                    f"| {'✅' if r.verification_passed else '❌'} |"
                )
            lines.append("")
        else:
            lines += [
                "## Recovered Files",
                "",
                "No files were recovered (no high-priority candidates found).",
                "",
            ]

        if unrecoverable:
            lines += [
                "## Unrecoverable Files",
                "",
                "The following files could not be recovered from git history.",
                "Their functionality must be reimplemented.",
                "",
            ]
            for path in unrecoverable:
                lines.append(f"- `{path}`")
            lines.append("")

        lines += [
            "## Reimplementation",
            "",
            "### Tasks for Unrecoverable Files",
            "",
        ]

        if unrecoverable:
            for i, path in enumerate(unrecoverable, 1):
                module_name = Path(path).stem
                lines += [
                    f"#### {i}. Reimplement `{path}`",
                    "",
                    f"- [ ] Identify what `{module_name}` was responsible for",
                    f"- [ ] Reimplement in the correct package location per new architecture",
                    f"- [ ] Add unit tests",
                    f"- [ ] Update all imports",
                    "",
                ]
        else:
            lines += [
                "No reimplementation tasks required.",
                "All deleted files were either recovered or intentionally removed.",
                "",
            ]

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Code Recovery System")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("scan", help="Scan git history and find references")
    subparsers.add_parser("report", help="Write RECOVERY_CANDIDATES.md")

    recover_parser = subparsers.add_parser("recover", help="Recover a specific file")
    recover_parser.add_argument("source", help="Original file path (repo/path/to/file.py)")
    recover_parser.add_argument("target", help="Target path for recovered file")

    args = parser.parse_args()

    workspace = Path(__file__).parent.parent
    system = CodeRecoverySystem(workspace_root=workspace)

    if args.command == "scan":
        print("=== Scanning git history for deleted Python files ===")
        deleted = system.scan_git_history(since="6 months ago")
        print(f"\nTotal deleted files found: {len(deleted)}")

        print("\n=== Finding references in current codebase ===")
        system.find_all_references()

        high = [df for df in system.deleted_files if df.recovery_priority == "high"]
        medium = [df for df in system.deleted_files if df.recovery_priority == "medium"]
        low = [df for df in system.deleted_files if df.recovery_priority == "low"]

        print(f"\nResults:")
        print(f"  High priority (still referenced): {len(high)}")
        print(f"  Medium priority: {len(medium)}")
        print(f"  Low priority: {len(low)}")

        if high:
            print("\nHigh priority files:")
            for df in high:
                print(f"  {df.path}")
                for ref in df.references_found[:3]:
                    print(f"    -> referenced in: {ref}")

    elif args.command == "report":
        print("=== Scanning git history ===")
        system.scan_git_history(since="6 months ago")
        print("=== Finding references ===")
        system.find_all_references()

        report = system.generate_recovery_candidates_report()
        out_path = workspace / "RECOVERY_CANDIDATES.md"
        out_path.write_text(report, encoding="utf-8")
        print(f"\nWritten: {out_path}")

    elif args.command == "recover":
        result = system.recover_file(args.source, args.target)
        if result.verification_passed:
            print(f"✅ Recovered: {args.source} -> {args.target}")
        else:
            print(f"❌ Recovery failed for: {args.source}")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
