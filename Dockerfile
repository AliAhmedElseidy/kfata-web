FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 DJANGO_SETTINGS_MODULE=config.settings.production
WORKDIR /app
RUN groupadd --gid 10001 kfata && useradd --uid 10001 --gid 10001 --create-home kfata
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=kfata:kfata . .
RUN mkdir -p /app/media /app/private-media /app/static && chown -R kfata:kfata /app
USER kfata
RUN DJANGO_SETTINGS_MODULE=config.settings.build python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "45", "--access-logfile", "-", "--error-logfile", "-"]
