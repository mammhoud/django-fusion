install:
	@echo "Installing dependencies via uv..."
	uv sync

check:
	@echo "Running Django checks..."
	uv run python manage.py check

run:
	@echo "Starting development server..."
	uv run python manage.py runserver
