FROM python:3.13-alpine AS builder
WORKDIR /app
COPY src/ ./src/
COPY site/ ./site/
ARG PUBLIC_WHATSAPP_NUMBER=""
ARG PUBLIC_SITE_URL=""
ARG PUBLIC_GA4_ID=""
ARG PUBLIC_META_PIXEL_ID=""
ARG PUBLIC_GTM_ID=""
ARG ENABLE_INDEXING="false"
RUN python src/build.py

FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/site/ /usr/share/nginx/html/
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1/health || exit 1
