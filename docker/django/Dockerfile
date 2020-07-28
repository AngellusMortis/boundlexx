## Base Shared image between dev and production
FROM python:3.8-slim-buster as base

ARG DJANGO_UID=1000

ENV PYTHONUNBUFFERED 1
ENV PYTEST ""
ENV DJANGO_MANAGE ""

RUN apt-get update \
  && apt-get install -y build-essential libpq-dev gettext nodejs npm \
  && npm install -g steam-user \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid ${DJANGO_UID} django \
    && adduser --system --shell /bin/bash --uid ${DJANGO_UID} --ingroup django django

COPY ./docker/bin/auth-ticket.js /auth-ticket.js
RUN chmod +x /auth-ticket.js
RUN mkdir -p /app/.steam
RUN chown -R django:django /app


## Development/CI image
FROM base as dev

ENV PYTHONDONTWRITEBYTECODE 1

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install -r /requirements/dev.txt

RUN apt-get update \
  && apt-get install -y git \
  && npm install -g steam-user \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY --chown=django:django ./docker/django/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./docker/django/dev/start /start
RUN chmod +x /start

COPY --chown=django:django ./docker/celery/dev/worker/start /start-celeryworker
RUN chmod +x /start-celeryworker

COPY --chown=django:django ./docker/celery/dev/beat/start /start-celerybeat
RUN chmod +x /start-celerybeat

COPY --chown=django:django ./docker/celery/dev/flower/start /start-flower
RUN chmod +x /start-flower

COPY --chown=django:django ./docker/bin/lint.sh /format.sh
RUN chmod +x /lint.sh

COPY --chown=django:django ./docker/bin/lint.sh /format.sh
RUN chmod +x /format.sh

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]


## Production Image
FROM base as production

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY --chown=django:django ./docker/django/entrypoint /entrypoint
RUN chmod +x /entrypoint

COPY --chown=django:django ./docker/django/production/start /start
RUN chmod +x /start

COPY --chown=django:django ./docker/celery/production/worker/start /start-celeryworker
RUN chmod +x /start-celeryworker

COPY --chown=django:django ./docker/celery/production/beat/start /start-celerybeat
RUN chmod +x /start-celerybeat

COPY --chown=django:django ./docker/celery/production/flower/start /start-flower
RUN chmod +x /start-flower

COPY --chown=django:django ./manage.py /app/
COPY --chown=django:django ./locale /app/locale
COPY --chown=django:django ./config /app/config
COPY --chown=django:django ./boundlexx /app/boundlexx

USER django

WORKDIR /app

VOLUME /ark /obelisk /logs

ENTRYPOINT ["/entrypoint"]
