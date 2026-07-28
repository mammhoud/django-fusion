# Project Structure

Understanding the workspace and project organization.

## Workspace Layout

```
workspace/
├── ctc-research/          # Django + React research platform
├── structa/               # Vite + React data visualization
├── blinko/                # Full-stack note-taking app
├── compose/               # Docker Compose configurations
├── docs/                  # Unified documentation
└── README.md              # Workspace overview
```

## ctc-research Structure

```
ctc-research/
├── backend/               # Django application
│   ├── manage.py
│   ├── requirements.txt
│   ├── settings/
│   ├── urls.py
│   └── apps/
├── frontend/              # React application
│   ├── package.json
│   ├── src/
│   ├── public/
│   └── vite.config.js
├── assets/                # Static assets
├── tests/                 # Test files
├── docker-compose.yml
└── .env.example
```

### Key Directories

- **backend/settings/** - Django configuration
- **backend/apps/** - Django applications
- **frontend/src/** - React components and pages
- **frontend/public/** - Static files
- **assets/static/** - CSS, images, fonts

## structa Structure

```
structa/
├── src/                   # Source code
│   ├── components/        # React components
│   ├── pages/             # Page components
│   ├── utils/             # Utility functions
│   ├── styles/            # CSS files
│   └── App.jsx
├── public/                # Static files
├── package.json
├── vite.config.js
└── .env.example
```

### Key Directories

- **src/components/** - Reusable React components
- **src/pages/** - Page-level components
- **src/utils/** - Helper functions and utilities
- **src/styles/** - Global and component styles

## blinko Structure

```
blinko/
├── src/                   # Source code
│   ├── components/        # React components
│   ├── pages/             # Page components
│   ├── api/               # API integration
│   ├── hooks/             # Custom React hooks
│   ├── utils/             # Utility functions
│   └── App.jsx
├── public/                # Static files
├── package.json
├── docker-compose.yml
└── .env.example
```

### Key Directories

- **src/components/** - Reusable components
- **src/pages/** - Page components
- **src/api/** - API client and endpoints
- **src/hooks/** - Custom React hooks

## Documentation Structure

```
docs/
├── README.md              # Documentation home
├── _sidebar.md            # Navigation
├── getting-started/       # Quick start guides
├── architecture/          # System design
├── npm-scripts/           # NPM commands
├── dependencies/          # Project dependencies
├── build-tools/           # Build configuration
├── development-server/    # Dev server setup
├── styling/               # CSS frameworks
├── api/                   # API documentation
├── configuration/         # Config files
├── deployment/            # Deployment guides
└── troubleshooting/       # Common issues
```

## File Naming Conventions

- **Directories**: lowercase with hyphens (e.g., `getting-started`)
- **Files**: numbered prefix with hyphens (e.g., `01-quick-start.md`)
- **Components**: PascalCase (e.g., `UserProfile.jsx`)
- **Utilities**: camelCase (e.g., `formatDate.js`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)

## Important Files

### Configuration Files
- `package.json` - Node.js project metadata
- `vite.config.js` - Vite build configuration
- `webpack.config.js` - Webpack build configuration
- `tsconfig.json` - TypeScript configuration
- `.env` - Environment variables
- `.gitignore` - Git ignore rules

### Documentation Files
- `README.md` - Project overview
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Version history
- `LICENSE.md` - License information

## Navigation Tips

- Use `_sidebar.md` for documentation navigation
- Check `README.md` in each directory for section overview
- Follow numbered file naming for sequential reading
- Use cross-references between related sections

## Next Steps

- Read [Common Tasks](04-common-tasks.md) for development workflows
- Check [Environment Setup](02-environment-setup.md) for configuration
- Review [Architecture Overview](../../README.md) for system design
