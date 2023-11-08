import logging
import os
from pathlib import Path
import psutil

import sentry_sdk
from prometheus_flask_exporter.multiprocess import \
    GunicornInternalPrometheusMetrics
from sentry_sdk.integrations.flask import FlaskIntegration

LOG_FORMAT = ('%(asctime)s] [%(levelname)s] file=%(pathname)s line=%(lineno)s '
              'module=%(module)s function=%(funcName)s %(message)s')


def setup_logger():
    logger = logging.getLogger('PYWPS')
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)


def initialise_prometheus(app, log=None):
    if os.environ.get("PROMETHEUS_MULTIPROC_DIR", False):
        metrics = GunicornInternalPrometheusMetrics(app)
        if log:
            log.info("Prometheus metrics enabled")
        return metrics
    return None


def setup_sentry():
    env = os.environ

    if "SENTRY_KEY" in env and "SENTRY_PROJECT" in env and "SENTRY_ORG" in env:
        sentry_sdk.init(
            dsn="https://%s@o%s.ingest.sentry.io/%s" % (env["SENTRY_KEY"],
                                                        env["SENTRY_ORG"],
                                                        env["SENTRY_PROJECT"]),
            environment=env.get("SENTRY_ENV_TAG", "dev"),
            integrations=[FlaskIntegration()]
        )


def get_pod_memory(ratio:float = 0.9) -> str:
    """Return an Xmx value ("xG"), as available memory * ratio"""
    x = psutil.virtual_memory().total
    # Try cgroup but if its too large then use psutil
    mem_sysfile = Path('/sys/fs/cgroup/memory/memory.limit_in_bytes')  # K8s pod
    if mem_sysfile.is_file():
        with open(mem_sysfile) as f:
            y = int(f.readline().strip())
            if y > 0 and y < x: x = y
    x = x * ratio / 1024**3
    return f'{x:.0f}G'

def get_pod_vcpus(exclude:int = 0) -> int:
    """Return the number of available virtual CPUs, as cpu_count - exclude"""
    x = psutil.cpu_count()
    # Try cgroup but if its
    # /sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us 2400000
    cpu_sysfile = Path('/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us')  # K8s pod
    if cpu_sysfile.is_file():
        with open(cpu_sysfile) as f:
            y = int(int(f.readline().strip()) / 10**5)
            if y > 0 and y < x: x = y
    y = x - exclude
    if y < 1: x = 1
    return int(x)
