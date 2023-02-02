from prometheus_flask_exporter.multiprocess import \
    GunicornInternalPrometheusMetrics

# Settings, https://docs.gunicorn.org/en/stable/settings.html
# Check what the server sees: gunicorn --print-config datacube_wps:app
timeout = 600   # 10 mins
worker_class = 'gevent'

def child_exit(server, worker):
    GunicornInternalPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)
