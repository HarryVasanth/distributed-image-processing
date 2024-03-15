"""Celery application shared by clients and workers."""

from __future__ import annotations

from celery import Celery

from .config import settings

app = Celery(
    "distributed-image-processing",
    broker=settings.broker_url,
    backend=settings.result_backend,
    include=["imageproc.tasks"],
)

app.conf.update(
    # JSON only: pickle deserialisation is a remote-code-execution risk.
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    enable_utc=True,
    timezone="UTC",
    task_track_started=True,
    worker_send_task_events=True,
    task_send_sent_event=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=int(settings.task_timeout),
    task_soft_time_limit=max(1, int(settings.task_timeout) - 10),
    result_expires=3600,
)
