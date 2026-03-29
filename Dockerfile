FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    REELCLEAN_LIBRARY_ROOT=/data

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y ffmpeg ca-certificates \
    && ffprobe -version \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/requirements.txt

COPY . /app

RUN useradd --create-home --shell /bin/bash reelclean \
    && chown -R reelclean:reelclean /app

USER reelclean

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:3007/health', timeout=3).read()" || exit 1

EXPOSE 3007

CMD ["gunicorn", "--config", "gunicorn.conf.py", "web:app"]
