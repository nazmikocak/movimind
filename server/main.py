"""MOVIMIND backend giriş noktası.

Çalıştır:  python main.py

Açılışta gerekirse veriyi temizler, modeli eğitir, ardından API'yi başlatır.
Sanal ortam gerekmez; sistemdeki Python kullanılır.
"""
import sys
from pathlib import Path

# 'app' paketini import edilebilir kıl
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn

from app import bootstrap
from app.config import config
from app.server import create_app

# Veri + model hazır olsun (recommender belleğe yüklenir)
bootstrap.prepare()

app = create_app()


if __name__ == "__main__":
    print(f"[server] http://{config.HOST}:{config.PORT}  (Swagger: /docs)")
    uvicorn.run(app, host=config.HOST, port=config.PORT)
