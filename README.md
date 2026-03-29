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

Docker images default `REELCLEAN_LIBRARY_ROOT` to `/data`, so directory options are
discovered from mounted folders without extra env vars.

The app defaults to `0.0.0.0:3007` (you can still override with
`REELCLEAN_HOST`/`REELCLEAN_PORT` when needed).

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

4. Open `http://localhost:3007`.

## Docker Run

Build image:

```bash
docker build -t reelclean:local .
```

Run container:

```bash
docker run --rm -p 3007:3007 \
  -e FLASK_SECRET_KEY=change-me \
  -e TMDB_API_KEY=your_tmdb_api_key \
  -v /mnt/4tb/Storage/Films:/data/4tb-Films \
  -v /mnt/4tb/Storage/New_Films:/data/4tb-New_Films \
  -v /home/hutch/downloads/complete:/data/Downloads \
  reelclean:local
```

## Docker Compose (Server Pattern)

Use `docker-compose.example.yml` as a starting point:

```bash
docker compose -f docker-compose.example.yml up -d
```

Directory setup is defined once in `docker-compose.example.yml` via volume mounts:

- `/mnt/4tb/Storage/Films:/data/4tb-Films`
- `/mnt/4tb/Storage/New_Films:/data/4tb-New_Films`
- `/home/hutch/downloads/complete:/data/Downloads`

ReelClean auto-discovers these three folder names (`4tb-Films`,
`4tb-New_Films`, `Downloads`) in the UI.

It does not publish host ports; attach the service to your reverse proxy network.

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
