"""MOVIMIND backend giriş noktası.

    python main.py                       # gerekirse temizle, eğit, yayınla; sonra servis et
    python main.py --publish-production  # yerel katalogu canlı veritabanına yaz
"""
import sys
from pathlib import Path

# `app` paketi, çalışma dizininden bağımsız import edilebilsin
sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn

from app import bootstrap
from app.config import config
from app.server import create_app

if "--publish-production" in sys.argv:
    bootstrap.publish_production()
    sys.exit(0)

bootstrap.prepare()

app = create_app()


if __name__ == "__main__":
    print(f"[server] http://{config.HOST}:{config.PORT}  (Swagger: /docs)")
    uvicorn.run(app, host=config.HOST, port=config.PORT)
