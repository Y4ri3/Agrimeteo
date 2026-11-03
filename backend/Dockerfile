# Contexte de build = racine du dépôt (le backend dépend de ./ml).
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
COPY ml ./ml
COPY backend ./backend
RUN pip install --no-cache-dir ./ml ./backend \
 && useradd --uid 10001 --no-create-home app \
 && mkdir -p /var/cache/agrimeteo && chown app /var/cache/agrimeteo
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
