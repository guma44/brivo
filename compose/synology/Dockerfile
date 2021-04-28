FROM python:3.8

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  && apt-get install -y python3-dev python3-cffi \
  && apt-get install -y libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
  && apt-get install -y libgdk-pixbuf2.0-0 libffi-dev shared-mime-info \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  && apt-get install -y golang-go \
  && apt-get install -y git \
  && apt-get install -y wget \
  && apt-get install -y tar \
  && apt-get install -y vim \
  && apt-get install -y supervisor \
  && apt-get install -y redis \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# needs to be set else Celery gives an error (because docker runs commands inside container as root)
# https://github.com/pm990320/docker-flask-celery/blob/master/Dockerfile
# ENV C_FORCE_ROOT=1

RUN addgroup --system django \
    && adduser --system --ingroup django django

# Requirements are installed here to ensure they will be cached.
COPY --chown=django:django ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt && rm -rf /requirements

# RUN echo "VERSION: 1.0.4"
# RUN git clone https://github.com/guma44/brivo && mv brivo /app && chown -R django:django /app
COPY --chown=django:django . /app

RUN \
  mkdir -p /var/log/celery && \
  mkdir -p /var/log/redis && \
  mkdir -p /var/log/django && \
  mkdir -p /var/log/supervisor && \
  mkdir -p /var/run && \
  mkdir -p /vol/web/media && \
  mkdir -p /vol/web/data && \
  mkdir -p /var/www/html && \
  mkdir -p /vol/web/redis-data && \
  chown -R django:django /var/log/celery && \
  chown -R django:django /var/log/redis && \
  chown -R django:django /var/log/django && \
  chown -R django:django /var/log/supervisor && \
  chown -R django:django /var/run && \
  chown -R django:django /vol/web/media && \
  chown -R django:django /vol/web/data && \
  chown -R django:django /var/www/html && \
  chown -R django:django /vol/web/redis-data && \
  sed -i 's/^\(dir .*\)$/# \1\ndir \/vol\/web\/redis-data/' /etc/redis/redis.conf

COPY --chown=django:django ./compose/synology/start-django /start-django
RUN sed -i 's/\r$//g' /start-django
RUN chmod +x /start-django

ENV DJANGO_SETTINGS_MODULE="config.settings.synology"

COPY --chown=django:django ./compose/synology/supervisor.conf /etc/supervisord.conf
EXPOSE 5000

WORKDIR /app

USER django


CMD ["supervisord", "-c", "/etc/supervisord.conf"]