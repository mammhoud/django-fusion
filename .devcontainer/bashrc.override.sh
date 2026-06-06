
#
# .bashrc.override.sh
#
# Dev Container Bash Configuration
# Sets up environment for local SQLite-based Django development

# persistent bash history
HISTFILE=~/.bash_history
PROMPT_COMMAND="history -a; $PROMPT_COMMAND"

# set development environment variables
export RUNNING_ENV=local
export DB_TYPE=sqlite
export DEBUG=true
export RUN_SETUP=true

# set some django env vars
source /entrypoint

# restore default shell options
set +o errexit
set +o pipefail
set +o nounset

# start ssh-agent
# https://code.visualstudio.com/docs/remote/troubleshooting
eval "$(ssh-agent -s)"

# ─── Local Development Welcome Message ───
echo ""
echo "🚀 Welcome to ctc-research Dev Container"
echo "═══════════════════════════════════════"
echo ""
echo "Environment: Local (SQLite)"
echo "Database: db.sqlite3"
echo "Django: Running on http://localhost:8000"
echo ""
echo "Common Commands:"
echo "  python manage.py runserver 0.0.0.0:8000"
echo "  python manage.py migrate"
echo "  python manage.py createsuperuser"
echo "  pytest tests/ -v"
echo ""
