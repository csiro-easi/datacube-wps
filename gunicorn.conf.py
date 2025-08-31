#import gevent.monkey
#gevent.monkey.patch_all()

from prometheus_flask_exporter.multiprocess import \
    GunicornInternalPrometheusMetrics

from datacube_wps.startup_utils import get_pod_vcpus

# Settings, https://docs.gunicorn.org/en/stable/settings.html
# Check what the server sees: gunicorn --print-config datacube_wps:app
timeout = 600   # 10 mins
#worker_class = 'gevent'
workers = get_pod_vcpus() * 2 + 1
reload = True

def child_exit(server, worker):
    GunicornInternalPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)
