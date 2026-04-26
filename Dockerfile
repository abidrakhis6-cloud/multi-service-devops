# ==========================================
# MultiServe - Multi-Stage Dockerfile
# Python 3.11 + Django + Gunicorn
# ==========================================

# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.11-slim as builder

WORKDIR /app

# Empêcher l'écriture de bytecode Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installation des dépendances de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# ==========================================
# Stage 2: Production
# ==========================================
FROM python:3.11-slim as production

WORKDIR /app

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONPATH=/app

# Installation des dépendances runtime uniquement
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Créer utilisateur non-root pour la sécurité
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app appuser

# Copier les wheels du builder et installer
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Créer les répertoires nécessaires
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R appuser:appgroup /app

# Copier le code de l'application
COPY --chown=appuser:appgroup . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput || true

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Passer à l'utilisateur non-root
USER appuser

# Exposer le port
EXPOSE 8000


# Commande de démarrage avec Gunicorn
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--worker-tmp-dir", "/dev/shm", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "--capture-output", \
     "--enable-stdio-inheritance", \
     "config.wsgi:application"]

# ==========================================
# Stage 3: Development (optionnel)
# ==========================================
FROM production as development

# Re-passer en root pour installer les déps de dev
USER root

# Installer les outils de développement
RUN pip install \
    pytest-django \
    pytest-cov \
    black \
    flake8 \
    ipdb \
    django-debug-toolbar

# Re-passer à l'utilisateur non-root
USER appuser

# Commande de développement (Django runserver)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
