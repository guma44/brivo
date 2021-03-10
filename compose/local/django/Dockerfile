FROM python:3.8-slim-buster

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
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# RUN mkdir /gocode && \
#     export GOPATH=/gocode && \
#     go get github.com/mailhog/MailHog && \
#     mv /gocode/bin/MailHog /usr/local/bin/mailhog && \
#     rm -rf /gocode

# EXPOSE 1025 8025

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/local.txt

# RUN \
#   cd /tmp && \
#   wget http://download.redis.io/redis-stable.tar.gz && \
#   tar xvzf redis-stable.tar.gz && \
#   cd redis-stable && \
#   make && \
#   make install && \
#   cp -f src/redis-sentinel /usr/local/bin && \
#   mkdir -p /etc/redis && \
#   cp -f *.conf /etc/redis && \
#   rm -rf /tmp/redis-stable* && \
#   sed -i 's/^\(dir .*\)$/# \1\ndir \/vol\/web\/redis-data/' /etc/redis/redis.conf

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

# COPY ./compose/local/django/supervisord.conf /etc/supervisord.conf

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./compose/local/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker

COPY ./compose/local/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat

COPY ./compose/local/django/celery/flower/start /start-flower
RUN sed -i 's/\r$//g' /start-flower
RUN chmod +x /start-flower

WORKDIR /app
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/data
# RUN mkdir -p /var/www/html
# RUN mkdir -p /var/log/redis
# RUN mkdir -p /vol/web/redis-data
ENTRYPOINT ["/entrypoint"]
