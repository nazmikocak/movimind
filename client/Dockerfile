# MOVIMIND web arayüzü — yerel çalıştırma (docker compose) için.
# Canlıda gerekmez: Cloudflare Pages build çıktısını (dist/) doğrudan sunar.

# 1) Build: Vite statik dosyaları üretir
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Tarayıcının erişeceği API adresi build sırasında koda gömülür
ARG VITE_API_BASE=http://localhost:8000
ARG VITE_SITE_URL=http://localhost:5173
ENV VITE_API_BASE=$VITE_API_BASE \
    VITE_SITE_URL=$VITE_SITE_URL
RUN npm run build

# 2) Sun: nginx statik dosyaları verir, bilinmeyen yolları index.html'e yönlendirir
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
