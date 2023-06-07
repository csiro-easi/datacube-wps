import os
import gevent.monkey
gevent.monkey.patch_all()

from prometheus_flask_exporter.multiprocess import \
    GunicornInternalPrometheusMetrics

from datacube_wps.startup_utils import get_pod_vcpus
from dask.distributed import LocalCluster, Client

# Settings, https://docs.gunicorn.org/en/stable/settings.html
# Check what the server sees: gunicorn --print-config datacube_wps:app
timeout = 600   # 10 mins
worker_class = 'gevent'
workers = get_pod_vcpus() * 2 + 1
reload = True

def _num_dask_workers():
    """Number of dask workers"""
    return int(os.getenv("DATACUBE_WPS_NUM_WORKERS", "4"))

def _create_dask_cluster():
    cluster = LocalCluster(n_workers=_num_dask_workers(), scheduler_port=0, threads_per_worker=1)
    return cluster

def post_fork(server, worker):
    worker.dask_cluster = _create_dask_cluster()
    worker.dask_client = Client(worker.dask_cluster)    

def child_exit(server, worker):
    GunicornInternalPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)
