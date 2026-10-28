# MOVIMIND API — canlı (Render) ve yerel (docker compose) için aynı imaj.
# Build bağlamı depo kökü:  docker build -f server/Dockerfile .
# Model dosyası (artifacts/knn_model.pkl) build'den önce yerinde olmalı:
#   yerelde eğitimin çıktısı, CI'da son "model-*" GitHub Release'inden indirilir.
FROM python:3.13.3-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app/server

# Bağımlılıklar ayrı katmanda: kod değişince yeniden kurulmaz
COPY server/requirements.txt .
RUN pip install -r requirements.txt

# Root olmayan kullanıcı; sahiplik COPY sırasında verilir (chown -R katmanı kopyalar)
RUN useradd --create-home --uid 1000 app
COPY --chown=app:app database/ /app/database/
COPY --chown=app:app server/ /app/server/
USER app

# Render PORT'u kendisi verir; HOST container içinde dışarıya açık olmalı
ENV HOST=0.0.0.0 \
    PORT=8000
EXPOSE 8000

CMD ["python", "main.py"]
