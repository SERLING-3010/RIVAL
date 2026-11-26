# Imagen del backend de RIVAL (Sprint 28). La misma imagen sirve para la API, las migraciones,
# el enviador de avisos y la limpieza de sesiones: solo cambia el comando (ver deploy/docker-compose.yml).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Primero las dependencias: si no cambian, Docker reutiliza esta capa.
COPY requirements.txt requirements-prod.txt ./
RUN pip install -r requirements-prod.txt

COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app

# Nunca correr como root dentro del contenedor.
RUN useradd --create-home --uid 10001 rival && chown -R rival:rival /app
USER rival

EXPOSE 8000

# --proxy-headers: detrás del proxy HTTPS, la IP del cliente sale de X-Forwarded-For, pero solo si
# viene de una IP en FORWARDED_ALLOW_IPS (variable de entorno; por defecto 127.0.0.1).
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
