# Quick Start Guide

Get any project in the workspace running in minutes.

## For ctc-research (Django + React)

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (or use Docker)

### Setup Steps

```bash
# Clone and navigate
git clone <repository>
cd ctc-research

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
npm install

# Database setup
python manage.py migrate

# Start development servers
# Terminal 1: Django backend
python manage.py runserver

# Terminal 2: React frontend
npm run dev
```

### Access Application
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

---

## For structa (Vite + React)

### Prerequisites
- Node.js 16+

### Setup Steps

```bash
# Clone and navigate
git clone <repository>
cd structa

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access Application
- Application: http://localhost:5173

---

## For blinko (Full-stack)

### Prerequisites
- Node.js 16+
- Docker (recommended)

### Setup Steps

```bash
# Clone and navigate
git clone <repository>
cd blinko

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access Application
- Application: http://localhost:3000

---

## Verify Installation

Run these commands to verify everything is working:

```bash
# Check Node.js
node --version

# Check Python (if applicable)
python --version

# Check npm
npm --version

# Run tests
npm run test

# Build project
npm run build
```

## Next Steps

- Read [Environment Setup](02-environment-setup.md) for detailed configuration
- Check [Common Tasks](04-common-tasks.md) for development workflows
- Review [Project Structure](03-project-structure.md) to understand the codebase
