"""Render ücretsiz servisini uyanık tutar: kendi genel adresine düzenli istek atar.

Render, 15 dakika gelen istek almayan ücretsiz servisi uyutur. İstek genel adres
üzerinden gittiği için Render'a dışarıdan gelen trafik olarak ulaşır.
"""
from __future__ import annotations

import threading
import time

import httpx

from app.config import config


def _loop(url: str) -> None:
    while True:
        time.sleep(config.KEEPALIVE_INTERVAL_MINUTES * 60)
        try:
            httpx.get(f"{url}/api/health", timeout=30)
        except httpx.HTTPError:
            pass  # bir sonraki turda yeniden denenir


def start() -> None:
    """`KEEPALIVE_ENABLED` açıksa ve genel adres biliniyorsa arka plan döngüsünü başlatır."""
    url = config.KEEPALIVE_URL.rstrip("/")
    if not config.KEEPALIVE_ENABLED or not url:
        return
    threading.Thread(target=_loop, args=(url,), daemon=True, name="keepalive").start()
    print(f"[keepalive] {config.KEEPALIVE_INTERVAL_MINUTES} dk'da bir -> {url}/api/health")
