# Environment Setup

Detailed instructions for configuring your development environment.

## System Requirements

### Minimum
- 4GB RAM
- 10GB disk space
- Modern operating system (macOS, Linux, Windows)

### Recommended
- 8GB+ RAM
- 20GB+ disk space
- SSD for faster builds

## Node.js Setup

### Installation

**macOS (using Homebrew)**
```bash
brew install node
```

**Linux (Ubuntu/Debian)**
```bash
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows**
Download from https://nodejs.org/ and run installer

### Verification
```bash
node --version  # Should be 16.0.0 or higher
npm --version   # Should be 7.0.0 or higher
```

## Python Setup (for precis-ctc)

### Installation

**macOS**
```bash
brew install python@3.9
```

**Linux (Ubuntu/Debian)**
```bash
sudo apt-get install python3.9 python3.9-venv
```

**Windows**
Download from https://www.python.org/ and run installer

### Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

## Database Setup

### PostgreSQL (for precis-ctc)

**macOS**
```bash
brew install postgresql
brew services start postgresql
```

**Linux**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Docker (Recommended)**
```bash
docker run --name postgres -e POSTGRES_PASSWORD=password -d postgres
```

## Environment Variables

Create `.env` file in project root:

```bash
# precis-ctc
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ALLOWED_HOSTS=localhost,127.0.0.1

# structa
VITE_API_URL=http://localhost:8000

# blinko
NODE_ENV=development
```

## IDE Setup

### VS Code Extensions (Recommended)

- **Python** - ms-python.python
- **Pylance** - ms-python.vscode-pylance
- **ESLint** - dbaeumer.vscode-eslint
- **Prettier** - esbenp.prettier-vscode
- **Thunder Client** - rangav.vscode-thunder-client

### Configuration

Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.python",
    "editor.formatOnSave": true
  }
}
```

## Docker Setup (Optional)

### Installation

**macOS/Windows**
Download Docker Desktop from https://www.docker.com/products/docker-desktop

**Linux**
```bash
sudo apt-get install docker.io docker-compose
```

### Verify Installation
```bash
docker --version
docker-compose --version
```

## Troubleshooting

### Node.js Issues
- Clear npm cache: `npm cache clean --force`
- Reinstall dependencies: `rm -rf node_modules && npm install`

### Python Issues
- Upgrade pip: `pip install --upgrade pip`
- Clear cache: `pip cache purge`

### Database Issues
- Check PostgreSQL status: `pg_isready`
- Reset database: `python manage.py migrate --reset`

## Next Steps

- Run [Quick Start Guide](01-quick-start.md)
- Check [Common Tasks](04-common-tasks.md)
- Review [Project Structure](03-project-structure.md)
