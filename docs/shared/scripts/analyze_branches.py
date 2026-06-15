"""
Branch Analyzer — Task 11.4
Compares recent feature branches with main/default branch and identifies improvements to merge.
"""

import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class BranchInfo:
    name: str
    repo: str
    last_commit_date: str
    unique_commits: list[str] = field(default_factory=list)
    files_changed: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    merge_priority: str = "none"  # high, medium, low, none
    skip_reason: str = ""


@dataclass
class ComparisonResult:
    branch: BranchInfo
    base_branch: str
    commit_count: int
    summary: str


class BranchAnalyzer:
    """Analyzes git branches to identify improvements worth merging."""

    OLD_ARCH_PATTERNS = [
        "apps/handlers/",
        "apps/LMS/",
        "apps/pages/",
    ]

    BOUNDARY_VIOLATION_PATTERNS = [
        "from apps.handlers",
        "import apps.handlers",
        "from apps.LMS",
        "import apps.LMS",
    ]

    def __init__(self, repos: list[tuple[str, str]]):
        """
        repos: list of (repo_path, default_branch) tuples
        e.g. [("ctc-research.com", "main"), ("structa.cloud", "generic")]
        """
        self.repos = repos
        self.cutoff_date = datetime.now() - timedelta(days=90)

    def _run_git(self, args: list[str], cwd: str) -> str:
        """Run a git command and return stdout."""
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def list_recent_branches(self, repo_path: str) -> list[str]:
        """Find all branches with commits in the last 3 months."""
        output = self._run_git(
            ["branch", "-r", "--sort=-committerdate"],
            repo_path,
        )
        branches = []
        for line in output.splitlines():
            line = line.strip()
            if not line or "->" in line:
                continue
            # Strip "origin/" prefix
            branch_name = line.replace("origin/", "").strip()
            branches.append(branch_name)
        return branches

    def get_branch_date(self, repo_path: str, branch: str) -> datetime | None:
        """Get the date of the most recent commit on a branch."""
        output = self._run_git(
            ["log", "-1", "--format=%ci", f"origin/{branch}"],
            repo_path,
        )
        if not output:
            return None
        try:
            # Parse "2024-01-15 10:30:00 +0000"
            return datetime.strptime(output[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None

    def get_unique_commits(self, repo_path: str, branch: str, base: str) -> list[str]:
        """Get commits unique to branch vs base."""
        output = self._run_git(
            ["log", "--oneline", f"origin/{base}..origin/{branch}"],
            repo_path,
        )
        return [line.strip() for line in output.splitlines() if line.strip()]

    def get_changed_files(self, repo_path: str, branch: str, base: str) -> list[str]:
        """Get files changed in branch vs base."""
        output = self._run_git(
            ["diff", "--name-only", f"origin/{base}...origin/{branch}"],
            repo_path,
        )
        return [line.strip() for line in output.splitlines() if line.strip()]

    def contains_old_arch(self, files: list[str]) -> bool:
        """Check if any changed files use old architecture patterns."""
        for f in files:
            for pattern in self.OLD_ARCH_PATTERNS:
                if pattern in f:
                    return True
        return False

    def classify_branch(self, branch: str, commits: list[str], files: list[str]) -> tuple[str, str, list[str]]:
        """
        Returns (merge_priority, skip_reason, improvements).
        merge_priority: "high", "medium", "low", "none"
        """
        if not commits:
            return "none", "No unique commits vs base branch", []

        # Skip dependabot branches — they only bump lock files
        if branch.startswith("dependabot/"):
            # Check if it's a security bump (cryptography, pillow, etc.)
            commit_text = " ".join(commits).lower()
            if any(pkg in commit_text for pkg in ["cryptography", "pillow", "security"]):
                return "medium", "", [f"Security dependency bump: {commits[0]}"]
            return "low", "", [f"Dependency bump: {commits[0]}"]

        # Skip branches with old architecture patterns
        if self.contains_old_arch(files):
            return "none", f"Contains old architecture patterns (apps/handlers/, apps/LMS/, etc.)", []

        # Classify by content
        improvements = []
        for commit in commits:
            msg = commit.split(" ", 1)[1] if " " in commit else commit
            if any(skip in msg for skip in ["..", "...", "__"]):
                continue  # Skip placeholder commits
            improvements.append(msg)

        if not improvements:
            return "none", "Only placeholder/empty commits", []

        # Determine priority
        has_feat = any("feat" in c.lower() or "feature" in c.lower() for c in improvements)
        has_fix = any("fix" in c.lower() for c in improvements)
        has_security = any("security" in c.lower() or "cve" in c.lower() for c in improvements)
        has_refactor = any("refactor" in c.lower() for c in improvements)

        if has_security:
            return "high", "", improvements
        elif has_feat and len(improvements) >= 3:
            return "high", "", improvements
        elif has_feat or has_fix:
            return "medium", "", improvements
        elif has_refactor:
            return "low", "", improvements
        else:
            return "low", "", improvements

    def compare_with_main(self, repo_path: str, branch: str, base: str) -> ComparisonResult:
        """Compare a branch with the base branch and identify improvements."""
        commits = self.get_unique_commits(repo_path, branch, base)
        files = self.get_changed_files(repo_path, branch, base)
        priority, skip_reason, improvements = self.classify_branch(branch, commits, files)

        branch_info = BranchInfo(
            name=branch,
            repo=repo_path,
            last_commit_date=self._run_git(
                ["log", "-1", "--format=%ci", f"origin/{branch}"], repo_path
            )[:10],
            unique_commits=commits,
            files_changed=files,
            improvements=improvements,
            merge_priority=priority,
            skip_reason=skip_reason,
        )

        summary_parts = []
        if commits:
            summary_parts.append(f"{len(commits)} unique commit(s)")
        if files:
            summary_parts.append(f"{len(files)} file(s) changed")
        if skip_reason:
            summary_parts.append(f"SKIP: {skip_reason}")

        return ComparisonResult(
            branch=branch_info,
            base_branch=base,
            commit_count=len(commits),
            summary=", ".join(summary_parts) if summary_parts else "No differences",
        )

    def analyze_all(self) -> list[ComparisonResult]:
        """Run full analysis across all repos."""
        results = []
        for repo_path, default_branch in self.repos:
            print(f"\n{'='*60}")
            print(f"Analyzing repo: {repo_path} (base: {default_branch})")
            print(f"{'='*60}")

            branches = self.list_recent_branches(repo_path)
            print(f"Found {len(branches)} remote branch(es): {branches}")

            for branch in branches:
                if branch == default_branch:
                    continue  # Skip the base branch itself

                # Check if branch has recent activity
                branch_date = self.get_branch_date(repo_path, branch)
                if branch_date and branch_date < self.cutoff_date:
                    print(f"  SKIP {branch}: last commit {branch_date.date()} (older than 3 months)")
                    continue

                print(f"  Comparing {branch} vs {default_branch}...")
                result = self.compare_with_main(repo_path, branch, default_branch)
                results.append(result)
                print(f"    → {result.summary} | priority={result.branch.merge_priority}")

        return results


def write_merge_candidates(results: list[ComparisonResult], output_path: str = "MERGE_CANDIDATES.md") -> None:
    """Write MERGE_CANDIDATES.md with analysis results."""
    high = [r for r in results if r.branch.merge_priority == "high"]
    medium = [r for r in results if r.branch.merge_priority == "medium"]
    low = [r for r in results if r.branch.merge_priority == "low"]
    skipped = [r for r in results if r.branch.merge_priority == "none"]

    lines = [
        "# MERGE_CANDIDATES.md",
        "",
        "Branch analysis comparing recent feature branches with their default/main branch.",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Lookback window: 3 months (since {(datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')})",
        "",
        "## Summary",
        "",
        f"| Priority | Count |",
        f"|----------|-------|",
        f"| High     | {len(high)} |",
        f"| Medium   | {len(medium)} |",
        f"| Low      | {len(low)} |",
        f"| Skipped  | {len(skipped)} |",
        f"| **Total** | **{len(results)}** |",
        "",
    ]

    def write_section(title: str, items: list[ComparisonResult]) -> list[str]:
        section = [f"## {title}", ""]
        if not items:
            section.append("_None found._")
            section.append("")
            return section
        for r in items:
            b = r.branch
            section.append(f"### `{b.repo}` — branch `{b.name}`")
            section.append("")
            section.append(f"- **Repo:** `{b.repo}`")
            section.append(f"- **Branch:** `{b.name}`")
            section.append(f"- **Base branch:** `{r.base_branch}`")
            section.append(f"- **Last commit:** {b.last_commit_date}")
            section.append(f"- **Unique commits:** {r.commit_count}")
            section.append(f"- **Files changed:** {len(b.files_changed)}")
            section.append(f"- **Merge priority:** {b.merge_priority.upper()}")
            if b.skip_reason:
                section.append(f"- **Skip reason:** {b.skip_reason}")
            if b.improvements:
                section.append("")
                section.append("**Improvements:**")
                for imp in b.improvements[:10]:
                    section.append(f"- {imp}")
                if len(b.improvements) > 10:
                    section.append(f"- _(and {len(b.improvements) - 10} more)_")
            if b.files_changed:
                section.append("")
                section.append("**Changed files (sample):**")
                for f in b.files_changed[:10]:
                    section.append(f"- `{f}`")
                if len(b.files_changed) > 10:
                    section.append(f"- _(and {len(b.files_changed) - 10} more)_")
            section.append("")
        return section

    lines += write_section("High Priority — Merge Recommended", high)
    lines += write_section("Medium Priority — Review and Merge", medium)
    lines += write_section("Low Priority — Optional", low)
    lines += write_section("Skipped — Not Suitable for Merge", skipped)

    lines += [
        "## Architecture Constraints",
        "",
        "The following patterns were used to filter out branches incompatible with the new architecture:",
        "",
        "- Branches touching `apps/handlers/` → old architecture, skip",
        "- Branches touching `apps/LMS/` → old architecture, skip",
        "- Branches touching `apps/pages/` → old architecture, skip",
        "- Dependabot security bumps (cryptography, pillow) → medium priority",
        "- Dependabot non-security bumps → low priority",
        "",
        "## Merge Strategy",
        "",
        "For high/medium priority branches, use `scripts/intelligent_merge.py` to:",
        "1. Cherry-pick individual commits rather than merging entire branches",
        "2. Validate no boundary violations are introduced",
        "3. Run test suite after each cherry-pick",
        "4. Document results in MERGE_REPORT.md",
        "",
    ]

    Path(output_path).write_text("\n".join(lines))
    print(f"\nWrote {output_path}")


if __name__ == "__main__":
    # ctc-research.com: "dev" is the active working branch (HEAD).
    # "main" is an older branch. We compare feature branches against "dev".
    # structa.cloud: only has "generic" branch — no feature branches to compare.
    repos = [
        ("ctc-research.com", "dev"),
        ("structa.cloud", "generic"),
    ]

    analyzer = BranchAnalyzer(repos)
    results = analyzer.analyze_all()
    write_merge_candidates(results)

    print("\nDone. See MERGE_CANDIDATES.md for results.")
