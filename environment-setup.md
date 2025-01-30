# Fisheries Project Environment Setup Guide

This guide provides complete instructions for setting up and maintaining your development environment for the fisheries data analysis project. It covers initial setup, SSH configuration, Git workflow, and daily development practices.

## Project Structure

Our project follows a standardized structure designed for clarity and maintainability:

```
/Volumes/dataDude/Scripts/fisheries_project/
├── data/
│   ├── raw/         # Original, immutable data storage
│   └── processed/   # Cleaned and transformed data
├── src/            # Source code for data processing and analysis
├── notebooks/      # Jupyter notebooks for analysis and visualization
├── docs/          # Project documentation
└── .gitignore     # Git ignore patterns
```

## Initial Git Setup

Initialize your Git repository with these commands:

```bash
cd /Volumes/dataDude/Scripts/fisheries_project
git init
```

Create and configure .gitignore with these essential patterns:

```
# Environment and IDE
.env
.vscode/*
!.vscode/settings.json
!.vscode/extensions.json

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# Data files
*.csv
*.xlsx
*.xls
*.parquet
*.feather
/data/raw/*
!/data/raw/.gitkeep
/data/processed/*
!/data/processed/.gitkeep

# Database
*.sqlite
*.db

# PostgreSQL
*.dump
*.sql
*.bak
postgres-data/
pg_data/
postgresql/
*.psql
pgdata/
pg_stat_tmp/
postmaster.*
postgresql.conf.old
recovery.conf
standby.signal
postgresql-*.auto.conf
*.pid

# Logs and temporary files
*.log
*.tmp
.DS_Store
```

## SSH Configuration

Initial SSH key generation and setup:

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "your.github@email.com" -f ~/.ssh/github_ed25519

# Add SSH key to GitHub:
# 1. Copy the public key
cat ~/.ssh/github_ed25519.pub
# 2. Go to GitHub.com → Settings → SSH and GPG keys
# 3. Click "New SSH key"
# 4. Paste the public key and save

# Test GitHub connection
ssh -T git@github.com
```

## Session Initialization

At the start of each development session, follow these steps to ensure proper GitHub authentication:

```bash
# Start the SSH agent
eval "$(ssh-agent -s)"

# Check if any keys are loaded
ssh-add -l

# If no identities are shown, add your GitHub key
ssh-add ~/.ssh/github_ed25519

# Verify GitHub connectivity
ssh -T git@github.com
```

These steps ensure your SSH authentication is properly configured for the current session, enabling smooth interaction with GitHub for pushing changes and other operations requiring authentication.

## Branch Management

Our project uses a three-branch strategy:

```bash
# Set up main branch (stable production code)
git checkout -b main

# Set up development branch
git checkout -b dev

# Create feature branches from dev
git checkout -b feature/your-feature-name
```

## Development Workflow

Follow these steps for development:

1. Start a new feature:
```bash
git checkout dev
git checkout -b feature/your-feature-name
```

2. Make changes and commit regularly:
```bash
git add <changed-files>
git commit -m "Descriptive message about changes"
```

3. Push changes to remote repository:
```bash
git push origin feature/your-feature-name
```

## Best Practices

1. Commit Messages:
   - Use clear, descriptive messages
   - Start with a verb (Add, Update, Fix, etc.)
   - Keep first line under 50 characters
   - Add detailed description if needed

2. Branch Usage:
   - Create feature branches from dev
   - Use the format: feature/feature-name
   - Merge completed features into dev
   - Regular merges from main to dev to stay current

3. Data Management:
   - Keep raw data in data/raw
   - Store processed data in data/processed
   - Document data transformations in notebooks

4. Code Organization:
   - Keep source code in src/
   - Use notebooks/ for analysis and visualization
   - Maintain documentation in docs/

## Troubleshooting

Common issues and solutions:

1. SSH Authentication:
   - Verify SSH agent is running: `eval "$(ssh-agent -s)"`
   - Confirm key is added: `ssh-add -l`
   - Test GitHub connection: `ssh -T git@github.com`

2. Git Push/Pull Issues:
   - Check remote URL: `git remote -v`
   - Verify branch tracking: `git branch -vv`
   - Resolve conflicts with: `git pull --rebase`

3. VS Code Integration:
   - Reload window if Git features aren't visible
   - Check Git extension status
   - Verify .git directory exists in project root
