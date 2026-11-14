"""NetBox WSGI entry point that warms up the worker before it accepts requests."""
import os
import time

from netbox.wsgi import application  # noqa: F401  (runs django.setup())


def _warm():
    if os.environ.get("NETBOX_WARMUP", "true").lower() not in ("1", "true", "yes", "on"):
        return
    t = time.perf_counter()
    try:
        # Imports every urls.py and with them the views, forms, tables,
        # filtersets, API serializers and the GraphQL schema
        from django.urls import get_resolver
        get_resolver().url_patterns
        # Render one page so middleware and base templates are loaded too
        from django.test import Client
        Client(HTTP_HOST="localhost").get("/login/")
    except Exception as e:  # never stop a worker from starting because of warm-up
        print(f"netbox: warm-up failed in pid {os.getpid()}: {e!r}", flush=True)
        return
    print(f"netbox: worker {os.getpid()} warmed up in {time.perf_counter() - t:.1f}s", flush=True)


_warm()

