bind = "0.0.0.0:3007"
worker_class = "gthread"
# The app stores job state in-memory, so use a single process.
workers = 1
threads = 4
timeout = 120
graceful_timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
capture_output = True
loglevel = "info"
