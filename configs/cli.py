"""
🎯 Django CLI Commands with Fire Integration
============================================
Command-line interface for Django management and sync operations.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import fire

from configs.settings import cli_command
from configs.settings import settings as env_settings
from configs.settings import settings as tracker


# ====================================
# 🔧 Django Command Runner
# ====================================
class DjangoCLI:
    """Django management commands."""

    def __init__(self):
        self.project_dir = Path(__file__).resolve().parent.parent
        self.manage_py = self.project_dir / "com"

    def _django_cmd(self, *args):
        """Run Django management command."""
        cmd = [sys.executable, str(self.manage_py), *args]
        subprocess.run(cmd, check=True)

    @cli_command("Run Django development server")
    def dev(self, host: str = None, port: str = None, noreload: bool = False):
        """
        Run Django development server.

        Args:
            host: Host to bind to (default: from env)
            port: Port to bind to (default: from env)
            noreload: Disable auto-reload
        """
        host = host or env_settings.HOST
        port = port or env_settings.PORT
        args = ["runserver", f"{host}:{port}"]
        if noreload:
            args.append("--noreload")
        self._django_cmd(*args)

    @cli_command("Run initial setup")
    def setup(self, noinput: bool = False):
        """Run initial setup (migrations, superuser, etc.)."""
        from django.core.management.base import CommandError

        print("⚡ Running setup...")

        # Migrations
        migrate_args = ["migrate"]
        if noinput:
            migrate_args.append("--noinput")
        self._django_cmd(*migrate_args)

        try:
            self._django_cmd("setup_periodic_tasks")
        except CommandError:
            print("⚠️  Periodic tasks setup not available")

        # Create superuser
        try:
            superuser_args = ["createsuperuser"]
            if noinput:
                superuser_args.extend(["--noinput", "--traceback"])
            self._django_cmd(*superuser_args)
            print("✅ Superuser created")
        except CommandError:
            print("⚠️  Superuser might already exist")

        print("✅ Setup completed!")

    @cli_command("Run any Django management command")
    def manage(self, *args):
        """
        Run any Django management command.

        Example:
            python -m configs.cli_commands manage migrate
            python -m configs.cli_commands manage createsuperuser
        """
        self._django_cmd(*args)

    @cli_command("Run database migrations")
    def migrate(self, *args):
        """Run database migrations."""
        self._django_cmd("migrate", *args)

    @cli_command("Create new migrations")
    def makemigrations(self, *args):
        """Create new migrations."""
        self._django_cmd("makemigrations", *args)

    @cli_command("Open Django shell")
    def shell(self, *args):
        """Open Django shell."""
        self._django_cmd("shell", *args)

    @cli_command("Run Django tests")
    def test(self, *args):
        """Run Django tests."""
        self._django_cmd("test", *args)

    @cli_command("Run Django system checks")
    def check(self, *args):
        """Run Django system checks."""
        self._django_cmd("check", *args)

    @cli_command("Collect static files")
    def collectstatic(self, *args):
        """Collect static files."""
        self._django_cmd("collectstatic", *args)

    @cli_command("Create superuser")
    def createsuperuser(self, *args):
        """Create superuser."""
        self._django_cmd("createsuperuser", *args)


# ====================================
# 🔄 Sync CLI Commands
# ====================================
class SyncCLI:
    """Sync operations between local, GitHub, and Docker."""

    def __init__(self):
        self.key_mapping = {
            "git.username": "git_username",
            "git.email": "git_email",
            "git.repo": "git_repo",
            "git.token": "git_token",
            "demo.container": "demo_container",
            "main.container": "main_container",
            "demo.branch": "demo_branch",
            "main.branch": "main_branch",
            "sync.restart_container": "restart_container",
            "sync.run_tests": "run_tests",
            "sync.auto_commit": "auto_commit",
            "server.host": "host",
            "server.port": "port",
        }

    @cli_command("Run sync operation")
    def sync(self, env: str = None, direction: str = None,
             workflow: str = None, container: str = None,
             branch: str = None, no_interactive: bool = False):
        """
        Run sync operation.

        Args:
            env: Environment (demo, main, development, staging, production)
            direction: Direction (push, pull, sync)
            workflow: Workflow (quick, standard, full)
            container: Container name (overrides env default)
            branch: Branch name (overrides env default)
            no_interactive: Non-interactive mode
        """
        try:
            config = tracker.get_sync_config(env, direction, workflow)

            if container:
                config.container = container
            if branch:
                config.branch = branch

            self._run_sync(config, interactive=not no_interactive)

        except ValueError as e:
            print(f"❌ Invalid parameter: {e}")
            return False

    @cli_command("Manage tokens")
    def token(self, action: str = "list", token: str = None, scope: str = "global"):
        """
        Token management operations.

        Args:
            action: Action to perform (list, save, test)
            token: Token to save (for save action)
            scope: Config scope (global or local)
        """
        actions = {
            "list": self._list_tokens,
            "save": lambda: self._save_token(token, scope),
            "test": self._test_token
        }

        if action in actions:
            actions[action]()
        else:
            print(f"❌ Unknown action: {action}")

    @cli_command("Configuration management")
    def config(self, action: str = "show", key: str = None, value: str = None):
        """
        Configuration management.

        Args:
            action: Action to perform (show, set, reset, validate, template)
            key: Configuration key to set (for set action)
            value: Value to set (for set action)
        """
        actions = {
            "show": self._show_config,
            "set": lambda: self._set_config(key, value) if key and value else print("❌ Key and value required for set"),
            "reset": self._reset_config,
            "validate": self._validate_config,
            "template": self._create_template
        }

        if action in actions:
            actions[action]()
        else:
            print(f"❌ Invalid action: {action}")
            print("Valid actions: show, set, reset, validate, template")

    @cli_command("Show environment")
    def env(self, show_all: bool = False):
        """Show environment settings."""
        print("🌍 Environment Settings:")
        print(f"  SERVER_ENV: {env_settings.SERVER_ENV.value}")
        print(f"  RUNNING_ENV: {env_settings.RUNNING_ENV.value}")
        print(f"  MODULE: {env_settings.MODULE.value}")
        print(f"  DEBUG: {env_settings.DEBUG}")
        print(f"  HOST: {env_settings.HOST}")
        print(f"  PORT: {env_settings.PORT}")

        if show_all:
            print("\nFull Environment:")
            for key, value in env_settings.to_dict(include_secrets=False).items():
                if not key.startswith('_'):
                    print(f"  {key}: {value}")

        # Show warnings
        warnings = env_settings.validate()
        config_warnings = tracker.validate_config()
        all_warnings = warnings + config_warnings

        if all_warnings:
            print("\n⚠️  Warnings:")
            for warning in all_warnings:
                print(f"  {warning}")

    # Internal methods
    def _run_sync(self, config, interactive: bool = True):
        """Run sync pipeline."""
        print(f"\n🚀 Starting {config.environment.value} Pipeline")
        print(f"Direction:    {config.direction.value}")
        print(f"Workflow:     {config.workflow.value}")
        print(f"Container:    {config.container}")
        print(f"Branch:       {config.branch}")

        if interactive:
            confirm = input("\nContinue? (y/n): ")
            if confirm.lower() != 'y':
                print("Cancelled.")
                return

        # TODO: Implement actual sync logic
        print(f"\n📤 Syncing {config.direction.value} to {config.environment.value}...")
        print("✅ Sync completed!")

    def _list_tokens(self):
        """List available tokens."""
        print("🔐 Available Tokens:")

        # Git config
        git_token = tracker.get_token()
        if git_token:
            masked = f"{git_token[:4]}...{git_token[-4:]}" if len(git_token) > 8 else "***"
            print(f"  Git Config: {masked}")
        else:
            print("  Git Config: NOT SET")

        # Environment variable
        env_token = env_settings.GIT_TOKEN
        if env_token:
            masked = f"{env_token[:4]}...{env_token[-4:]}" if len(env_token) > 8 else "***"
            print(f"  Environment: {masked}")

    def _save_token(self, token: str = None, scope: str = "global"):
        """Save token to git config."""
        if not token:
            token = input("Enter GitHub token: ").strip()

        if token:
            repo_path = Path.cwd() if scope == "local" else None

            # Ask if user wants to save to .env file too
            save_to_env = False
            if scope == "global":
                response = input("Also save to .env file? (y/n) [n]: ").strip().lower()
                save_to_env = response == "y"

            if tracker.save_token(token, repo_path, scope, save_to_env):
                print("✅ Token saved")
            else:
                print("❌ Failed to save token")

    def _test_token(self):
        """Test token validity."""
        token = tracker.get_token()
        if token:
            print(f"✅ Token found (masked: {token[:4]}...{token[-4:]})")

            # Test with GitHub API
            try:
                import requests
                response = requests.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"token {token}"},
                    timeout=5
                )
                if response.status_code == 200:
                    print("✅ Token is valid")
                else:
                    print("❌ Token is invalid")
            except Exception:
                print("⚠️  Could not verify token (network error)")
        else:
            print("❌ No token found")

    def _show_config(self):
        """Show current configuration."""
        config = tracker.show_config()

        print("⚙️ Current Configuration:")
        for category, values in config.items():
            print(f"\n{category.upper()}:")
            for key, value in values.items():
                print(f"  {key}: {value}")

    def _set_config(self, key: str, value: str):
        """Set configuration value."""
        if key in self.key_mapping:
            param_name = self.key_mapping[key]
            if tracker.update_config(**{param_name: value}):
                print(f"✅ Set {key} = {value}")
            else:
                print(f"❌ Failed to set {key}")
        else:
            print(f"❌ Unknown config key: {key}")
            print(f"Available keys: {', '.join(self.key_mapping.keys())}")

    def _reset_config(self):
        """Reset configuration to defaults."""
        confirm = input("Reset configuration to defaults? (y/n): ").strip().lower()
        if confirm == 'y':
            if tracker.reset_config(confirm=True):
                print("✅ Configuration reset to defaults")
            else:
                print("❌ Failed to reset configuration")
        else:
            print("❌ Cancelled")

    def _validate_config(self):
        """Validate configuration."""
        warnings = tracker.validate_config()
        if warnings:
            print("⚠️  Configuration Warnings:")
            for warning in warnings:
                print(f"  {warning}")
        else:
            print("✅ Configuration is valid")

    def _create_template(self):
        """Create .env.template file."""
        if tracker.create_env_template():
            print("✅ Created .env.template")
            print("📝 Rename to .env and fill in your values")
        else:
            print("❌ Failed to create template")


# ====================================
# 🎯 Interactive Menu
# ====================================
def show_interactive_menu():
    """Show interactive menu."""
    print("\n" + "="*50)
    print("🔧 Development Menu")
    print("="*50)
    print("\nWhat would you like to do?\n")

    menu_options = [
        "1. 🚀 Start Django server",
        "2. 📦 Install/Update Python dependencies",
        "3. 🔄 Run sync operation",
        "4. 🗃️  Run database migrations",
        "5. 🧹 Collect static files",
        "6. 👑 Create superuser",
        "7. 🔍 Run Django checks",
        "8. 🧪 Run tests",
        "9. 🐚 Open Django shell",
        "10. 🔐 Manage tokens",
        "11. ⚙️  Show configuration",
        "12. 🌍 Show environment",
        "13. 📖 Show help",
        "0. 🚪 Exit"
    ]

    for option in menu_options:
        print(option)

    try:
        choice = input("\nChoose an option (0-13): ").strip()

        cli = MainCLI()

        actions = {
            "1": lambda: cli.django.dev(),
            "2": lambda: subprocess.run(["uv", "sync"]),
            "3": lambda: cli.sync.sync(),
            "4": lambda: cli.django.migrate(),
            "5": lambda: cli.django.collectstatic(),
            "6": lambda: cli.django.createsuperuser(),
            "7": lambda: cli.django.check(),
            "8": lambda: cli.django.test(),
            "9": lambda: cli.django.shell(),
            "10": lambda: cli.sync.token(),
            "11": lambda: cli.sync.config(),
            "12": lambda: cli.sync.env(),
            "13": lambda: cli.help(),
            "0": lambda: None
        }

        if choice in actions:
            if choice == "0":
                print("\n👋 Goodbye!")
                return
            actions[choice]()
        else:
            print("❌ Invalid option")

        # Ask to continue
        input("\nPress Enter to continue...")
        show_interactive_menu()

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return
    except EOFError:
        print("\n\n👋 Goodbye!")
        return


# ====================================
# 🏗️ Variant Management CLI
# ====================================
class VariantCLI:
    """Project variant management (Basic, Blogger, LMS)."""

    def __init__(self):
        self.project_dir = Path(__file__).resolve().parent.parent
        self.variants = {
            "core": {
                "name": "Core",
                "remove": ["apps/LMS", "apps/blog", "apps/newsletter"],
                "use_case": "Essential framework and infrastructure (No LMS, No Blog).",
                "repo_key": "CORE_REPO",
            },
            "blog": {
                "name": "Blog",
                "remove": ["apps/LMS"],
                "use_case": "Content-focused variant with Blog and Newsletter features.",
                "repo_key": "BLOG_REPO",
            },
            "lms": {
                "name": "LMS",
                "remove": ["apps/blog", "apps/newsletter"],
                "use_case": "Dedicated LMS variant (No Blog or Newsletter).",
                "repo_key": "LMS_REPO",
            },
            "all": {
                "name": "Full",
                "remove": [],
                "use_case": "Complete platform with LMS, Blog, and Newsletter.",
                "repo_key": "ALL_REPO",
            },
        }

    @cli_command("Setup project variant")
    def setup(self, variant: str):
        """
        Setup a specific project variant.

        Args:
            variant: Variant name (basic, blogger, lms)
        """
        if variant not in self.variants:
            print(f"❌ Unknown variant: {variant}")
            print(f"Available variants: {', '.join(self.variants.keys())}")
            return

        info = self.variants[variant]
        print(f"🏗️  Setting up {info['name']} variant...")
        print(f"📝 Use case: {info['use_case']}")

        # GitHub Integration logic
        repo = tracker.get(info["repo_key"], tracker.GIT_REPO)
        if repo:
            print(f"🔗 Target Repo: {repo}")
            token = tracker.GIT_TOKEN
            if token:
                mask = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"
                print(f"🔑 Using GitHub token: {mask}")
            else:
                print("⚠️  No GitHub token found. Using default SSH key.")
        else:
            print("⚠️  No specific repository set for this variant. Using default GIT_REPO.")

        # Logic to "create" the variant (Filtering files)
        if info["remove"]:
            print(f"🧹 Filtering apps for {variant}...")
            for app_path in info["remove"]:
                full_path = self.project_dir / app_path
                if full_path.exists():
                    print(f"   - Filtered: {app_path}")
                else:
                    print(f"   - {app_path} not found, skipping.")

        print(f"✅ {info['name']} variant integration defined!")

    @cli_command("Publish variant to GitHub")
    def publish(self, variant: str, message: str = "Update variant", push: bool = True):
        """
        Publish a specific variant to the unified GitHub repository with tags.
        """
        import re
        if variant not in self.variants:
            print(f"❌ Unknown variant: {variant}")
            return

        info = self.variants[variant]
        repo_name = tracker.get(info["repo_key"], tracker.GIT_REPO)

        if not repo_name:
            print(f"❌ No repository configured for variant '{variant}'")
            return

        # Get version from pyproject.toml
        version = "1.0.0"
        try:
            with open(self.project_dir / "pyproject.toml", "r") as f:
                content = f.read()
                version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
                if version_match:
                    version = version_match.group(1)
        except Exception:
            pass

        tag_name = f"v{version}-{variant}"
        target_branch = "main" if variant == "all" else f"release/{variant}"

        print(f"🚀 Publishing {info['name']} variant to {repo_name}...")
        print(f"🏷️  Tag: {tag_name}")
        print(f"🌿 Branch: {target_branch}")

        # Setup paths
        temp_dir = Path("/tmp/publish") / variant
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)

        try:
            # 1. Clone or initialize target repo
            token = tracker.GIT_TOKEN or os.environ.get("GIT_TOKEN")

            # Try to extract token from origin remote if missing
            if not token:
                try:
                    result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
                    url = result.stdout.strip()
                    if "@github.com" in url and "https://" in url:
                        token = url.split("https://")[1].split("@")[0]
                except Exception:
                    pass

            if token:
                repo_url = f"https://{token}@github.com/{repo_name}.git"
            else:
                repo_url = f"git@github.com:{repo_name}.git"

            print(f"📦 Cloning {repo_name}...")
            # We try to clone the specific branch if it exists
            result = subprocess.run(["git", "clone", "--depth", "1", "--branch", target_branch, repo_url, "."], cwd=temp_dir, capture_output=True)

            if result.returncode != 0:
                print(f"✨ Branch '{target_branch}' does not exist, initializing from default...")
                subprocess.run(["git", "clone", "--depth", "1", repo_url, "."], cwd=temp_dir, capture_output=True)
                if not (temp_dir / ".git").exists():
                    subprocess.run(["git", "init"], cwd=temp_dir)
                    subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=temp_dir)
                subprocess.run(["git", "checkout", "-b", target_branch], cwd=temp_dir)

            # 2. Clear target dir except .git
            print("🧹 Preparing workspace...")
            for item in temp_dir.iterdir():
                if item.name != ".git":
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()

            # 3. Copy files from source to target
            print("📂 Copying files...")
            source_dir = self.project_dir
            for item in source_dir.iterdir():
                if item.name in [".git", "node_modules", ".venv", "__pycache__", "db.sqlite3"] + info["remove"]:
                    continue

                dest = temp_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, ignore=shutil.ignore_patterns(".git", "__pycache__"))
                else:
                    shutil.copy2(item, dest)

            # 4. Commit, Tag and Push
            print("💾 Committing changes...")
            subprocess.run(["git", "add", "."], cwd=temp_dir)

            user_name = tracker.GIT_USERNAME or "Xellent Bot"
            user_email = tracker.GIT_EMAIL or "bot@structa.cloud"
            subprocess.run(["git", "config", "user.name", user_name], cwd=temp_dir)
            subprocess.run(["git", "config", "user.email", user_email], cwd=temp_dir)

            status = subprocess.run(["git", "status", "--porcelain"], cwd=temp_dir, capture_output=True, text=True)
            if not status.stdout.strip():
                print("ℹ️ No changes to publish.")
            else:
                commit_msg = f"{message} [{variant} v{version}]"
                subprocess.run(["git", "commit", "-m", commit_msg], cwd=temp_dir)

            # Handle tagging (force update if version matches)
            subprocess.run(["git", "tag", "-d", tag_name], cwd=temp_dir, capture_output=True)
            subprocess.run(["git", "tag", "-a", tag_name, "-m", f"Release {info['name']} v{version}"], cwd=temp_dir)

            if push:
                print("📤 Pushing to GitHub...")
                subprocess.run(["git", "push", "-f", "origin", target_branch], cwd=temp_dir)
                subprocess.run(["git", "push", "-f", "origin", tag_name], cwd=temp_dir)
                print(f"✅ Published successfully to {repo_name} ({target_branch} @ {tag_name})")

        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    @cli_command("Publish all variants")
    def publish_all(self, message: str = "Sync all variants"):
        """Publish all defined project variants."""
        for variant in self.variants.keys():
            self.publish(variant, message)

    @cli_command("Show variant use cases")
    def use_cases(self):
        """Show use cases for all defined variants."""
        print("\n📋 Project Variant Use Cases:")
        print("=" * 30)
        for name, info in self.variants.items():
            print(f"\n🔹 {info['name']}:")
            print(f"   {info['use_case']}")
            if info["remove"]:
                print(f"   Excludes: {', '.join(info['remove'])}")
            else:
                print("   Includes all features.")
        print("")


# ====================================
# 🎯 Main CLI Class
# ====================================
class MainCLI:
    """
    Main CLI interface for Django and Sync operations.

    Examples:
        # Django commands
        python -m configs dev
        python -m configs setup
        python -m configs manage migrate

        # Sync commands
        python -m configs sync --env demo --push
        python -m configs token --list
        python -m configs env --show-all

        # Variant commands
        python -m configs variant setup basic
        python -m configs variant use_cases

        # Interactive menu
        python -m configs menu
    """

    def __init__(self):
        self.django = DjangoCLI()
        self.sync = SyncCLI()
        self.variant = VariantCLI()

    @cli_command("Show interactive menu")
    def menu(self):
        """Show interactive development menu."""
        show_interactive_menu()

    @cli_command("Show comprehensive help")
    def help(self):
        """Show comprehensive help."""
        print("""
🧠 Django Project CLI
=====================

Usage:
  python -m configs <command> [options]

Commands:
  Django Commands:
    dev                   - Run development server
    setup                 - Initial setup
    manage <command>      - Run any com command
    migrate               - Run migrations
    makemigrations        - Create migrations
    shell                 - Open Django shell
    test                  - Run tests
    check                 - System checks
    collectstatic         - Collect static files
    createsuperuser       - Create superuser

  Sync Commands:
    sync                  - Run sync operation
    token                 - Manage tokens
    config                - Manage configuration
    env                   - Show environment

  Variant Commands:
    variant setup <name>  - Setup project variant (basic, blogger, lms)
    variant use_cases     - Show use cases for variants

  Interactive:
    menu                  - Show interactive menu
    help                  - Show this help

Examples:
  # Development
  python -m configs dev --host 0.0.0.0 --port 8080
  python -m configs setup --noinput

  # Sync operations
  python -m configs sync --env demo --push
  python -m configs sync --env main --pull --workflow full

  # Variant operations
  python -m configs variant setup basic
  python -m configs variant use_cases

  # Token management
  python -m configs token --save
  python -m configs token --list
  python -m configs token --test

  # Configuration
  python -m configs config --show
  python -m configs config --set git.username myuser
  python -m configs env --show-all

  # Interactive
  python -m configs menu
        """)


# ====================================
# 🔥 Fire Entry Point
# ====================================
def main():
    """Main entry point for Fire CLI."""
    fire.Fire(MainCLI)

if __name__ == "__main__":
    main()
