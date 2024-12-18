# base image used by other stages
FROM python:3.9-slim-buster AS base

ARG DJANGO_UID=1000

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app
ENV PYTEST ""
ENV DJANGO_MANAGE ""
ENV HUEY_WORKER_COUNT 2

RUN addgroup --system --gid ${DJANGO_UID} django \
  && adduser --system --shell /bin/bash --uid ${DJANGO_UID} --ingroup django django

RUN apt-get update \
  && apt-get install -y libpq-dev gettext nodejs npm git python3-mpltoolkits.basemap python3-pillow lsb-release \
  && npm install -g steam-user@4.19.12 \
  && pip install pip --upgrade \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

COPY ./requirements /requirements
COPY ./docker/bin/* /usr/local/bin/
RUN chmod +x /usr/local/bin/steam-auth-ticket /usr/local/bin/convert-atlas /usr/local/bin/lint-code /usr/local/bin/format-code /usr/local/bin/entrypoint /usr/local/bin/start-celerybeat /usr/local/bin/start-celeryworker /usr/local/bin/start-huey-consumer /usr/local/bin/start-huey-scheduler
RUN mkdir -p /app/.steam
RUN chown -R django:django /app


# production builder
FROM base AS builder

ENV PYTHONDONTWRITEBYTECODE 1
RUN apt-get update \
  && apt-get install -y build-essential \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r /requirements/production.txt


# production stage
FROM base AS production
ENV PYTHONDONTWRITEBYTECODE 1

COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.9/ /usr/local/lib/python3.9/
COPY --chown=django:django ./docker/django/production/start /usr/local/bin/start
COPY --chown=django:django ./manage.py /app/manage.py
COPY --chown=django:django ./locale /app/locale
COPY --chown=django:django ./config /app/config
COPY --chown=django:django ./boundlexx /app/boundlexx
COPY --chown=django:django ./boundlexx_client/client.py /app/boundlexx/boundless/game/client.py

RUN chmod +x /usr/local/bin/start \
  && rm /requirements -rf

USER django
WORKDIR /app
ENTRYPOINT ["/usr/local/bin/entrypoint"]

# dev builder
FROM builder AS builder-dev
RUN pip install --no-cache-dir -r /requirements/dev.txt


# dev stage
FROM base AS dev
ENV PYTHONDONTWRITEBYTECODE 1

COPY --from=builder-dev /usr/local/bin/ /usr/local/bin/
COPY --from=builder-dev /usr/local/lib/python3.9/ /usr/local/lib/python3.9/
COPY --chown=django:django ./docker/django/dev/start /usr/local/bin/start

RUN chmod +x /usr/local/bin/start \
  && rm /requirements -rf

USER django
ENV CELERY_WORKER_QUEUES "default,distance,cache,notify,poll,shop,control"
ENV CELERY_WORKER_NAME "celery"
ENV CELERY_DEBUG_LEVEL "INFO"
WORKDIR /app

ENTRYPOINT ["/usr/local/bin/entrypoint"]
