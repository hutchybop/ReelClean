# ReelClean Agent Guidelines

## Project Overview
ReelClean is a Flask web app for organizing movie files with TMDB-based renaming, quality scanning, and cleanup workflows.

## Build/Test Commands

### Install Dependencies
```bash
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt  # dev dependencies
```

### Running the Application
```bash
python3 web.py                        # Development
gunicorn --config gunicorn.conf.py web:app  # Production
```

### Running Tests
```bash
# Run all tests
python3 -m unittest discover -s tests

# Run a single test file
python3 -m unittest tests.test_config

# Run a specific test (recommended for debugging)
python3 -m unittest tests.test_config.ConfigTests.test_from_env_parses_values
```

### Linting & Type Checking
```bash
flake8 .                              # Lint with flake8
black .                               # Format with black
mypy .                                # Type check (if installed)
```

### Environment Variables
```bash
TMDB_API_KEY=your_api_key            # Required for TMDB lookups
TMDB_TIMEOUT_SECONDS=10              # API timeout
FFPROBE_BIN=ffprobe                  # FFprobe binary path
FLASK_SECRET_KEY=your_secret         # Session secret
REELCLEAN_HOST=0.0.0.0               # Host
REELCLEAN_PORT=3007                  # Port
REELCLEAN_ALLOWED_DIRS="Movies:/path/to/movies,Downloads:/path/to/downloads"
REELCLEAN_LIBRARY_ROOT=/path/to/media
```

## Code Style Guidelines

### Python Version & General
- Python 3.8+ (target in pyproject.toml)
- Use `#!/usr/bin/env python3` shebang
- Include `from __future__ import annotations` at the top of all files
- 4 spaces for indentation (no tabs)
- Maximum line length: 88 characters (Black default)

### Import Order
Order imports: stdlib → third-party → local modules
```python
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from flask import Flask, abort, redirect, render_template, request

from reelclean.core.config import ReelCleanConfig
from reelclean.core.models import Decision
from reelclean.core.tmdb import TMDBClient
from reelclean.web.job_manager import JobManager
```

### Naming Conventions
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `TMDB_URL`)
- **Classes**: `PascalCase` (e.g., `ReelCleanConfig`, `TMDBClient`)
- **Functions/variables**: `snake_case` with descriptive names
- **Private methods**: prefix with underscore (e.g., `_search`)
- **Dataclass fields**: `snake_case`

### Type Hints
Use modern union syntax (Python 3.10+):
```python
def lookup(self, title: str, year_hint: str | None = None) -> TmdbMatch | None:
```
- Use `dict[str, Any]` for untyped dictionaries
- Include return types on all functions

### Dataclasses for Models
```python
@dataclass
class TmdbMatch:
    title: str
    year: str
    display_name: str
    source_query: str
```

### Error Handling
**API Calls:**
```python
try:
    response = requests.get(url, params=params, timeout=self.timeout_seconds)
    response.raise_for_status()
    payload = response.json()
except (requests.RequestException, ValueError):
    return []  # Return empty on failure
```

**File Operations:**
```python
try:
    path = option.path.expanduser().resolve()
except OSError:
    continue  # Skip invalid paths
```

**Validation:**
```python
def require_tmdb_key(self) -> str:
    if not self.tmdb_api_key:
        raise ValueError("TMDB_API_KEY is not set")
    return self.tmdb_api_key
```

### Documentation
Use triple quotes `"""` for docstrings with description, args, and return types:
```python
def lookup(self, title: str, year_hint: str | None = None) -> TmdbMatch | None:
    """Lookup a movie title with fallback strategies.

    Args:
        title: Raw movie filename to search.
        year_hint: Optional year for better matching.

    Returns:
        Best match from TMDB or None if no results.
    """
```

## Project Structure
```
reelclean/
├── __init__.py
├── core/
│   ├── config.py         # Configuration from environment
│   ├── models.py         # Dataclasses (Decision, TmdbMatch)
│   ├── tmdb.py           # TMDB API client
│   ├── scan.py           # Directory scanning, title cleaning
│   ├── rename_service.py
│   ├── quality_service.py
│   ├── cleanup_service.py
│   └── executor.py
├── web/
│   └── job_manager.py    # Job state machine
├── tests/                # unittest.TestCase tests
├── web.py                # Flask routes
├── templates/            # Jinja2 templates
└── static/              # CSS, JS, assets
```

## Testing Guidelines
- Use `unittest.TestCase` for all tests
- Use `tempfile.TemporaryDirectory()` for file operations
- Mock external APIs (requests, subprocess) when needed
- Include edge cases: empty inputs, invalid values, network errors

## Security
- Never commit API keys or secrets to version control
- Use `.env.example` for required variables
- Validate user input paths to prevent directory traversal attacks
- Use absolute paths for file operations
- Verify all operations stay within allowed directory roots