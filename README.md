# ReelClean

ReelClean is a Flask web app that helps you organize movie files with a safe,
review-first workflow:

- scan configured media directories
- generate TMDB-based rename proposals (dry run)
- accept, skip, or retry each movie lookup
- review cleanup candidates with checkboxes before deletion
- optionally run low-quality analysis via `ffprobe`

## Features

- Flask + Bootstrap 5 UI
- Server-side job state (in-memory)
- Dry-run planning with conflict detection
- Safe execution path checks (operations must stay inside allowed roots)
- Quality scan results for `.mkv`, `.mp4`, `.avi`, `.mov`, `.wmv`

## Project Structure

- `app.py` Flask entrypoint
- `reelclean/core/` reusable scan/rename/cleanup/quality services
- `reelclean/web/` web workflow state manager
- `templates/` Jinja templates
- `static/css/` shared and page-specific CSS
- `static/js/` page-specific JavaScript
- `static/favicons/` favicon assets

## Environment Variables

Create `.env` from `.env.example` and set values:

- `TMDB_API_KEY` TMDB key for rename lookups
- `TMDB_TIMEOUT_SECONDS` request timeout (default `10`)
- `FFPROBE_BIN` ffprobe binary (default `ffprobe`)
- `FLASK_SECRET_KEY` session secret
- `REELCLEAN_HOST` default `0.0.0.0`
- `REELCLEAN_PORT` default `8000`
- `REELCLEAN_ALLOWED_DIRS` comma list of `label:path`
  - example: `Movies:/data/movies,Downloads:/data/downloads`
- `REELCLEAN_LIBRARY_ROOT` optional fallback root to auto-discover child dirs

## Local Run

1. Install Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Set env vars in `.env`.

3. Start the web app:

```bash
python3 app.py
```

4. Open `http://localhost:8000`.

## Docker Run

Build image:

```bash
docker build -t reelclean:local .
```

Run container:

```bash
docker run --rm -p 8000:8000 \
  -e FLASK_SECRET_KEY=change-me \
  -e TMDB_API_KEY=your_tmdb_api_key \
  -e REELCLEAN_ALLOWED_DIRS="Movies:/data/movies" \
  -v /srv/media/movies:/data/movies \
  reelclean:local
```

## Docker Compose (Server Pattern)

Use `docker-compose.example.yml` as a starting point:

```bash
docker compose -f docker-compose.example.yml up -d
```

Make sure host mount paths and `REELCLEAN_ALLOWED_DIRS` paths match.

## GHCR Publishing

Workflow file: `.github/workflows/docker-publish.yml`

- triggers on pushes to `main`, tags (`v*`), and manual runs
- publishes to `ghcr.io/<owner>/<repo>`
- tags include branch/tag, `sha-*`, and `latest` (on `main`)

## Tests

Run unit tests:

```bash
python3 -m unittest discover -s tests
```

Health endpoint:

- `GET /health` returns `{"status": "ok"}`
