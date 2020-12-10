# notify-service

Notify service with multiple supported target

This is a backend service build with FastAPI.

# Requirement

  - Python 3.8
  - Pipenv
  - Podman, buildah on Linux host

Check Pipefile for python packages.

# Setup

## Build container image

Build production image with:

  $ buildah bud -f Dockerfile -t notify-service:base

Build dev image with:

  $ buildah bud -f Dockerfile.dev -t notify-service:dev

## Update .env

Make a copy of the env file and update the parameters:

SECRET_KEY: The API key to authenticate and access the apis, you could generate one with cmd `$openssl rand -hex 32`

SMTP related config:
SMTP_TLS: default to True
SMTP_PORT: str, required
SMTP_HOST: str, required
SMTP_USER: str, optional
SMTP_PASSWORD: str, optional
EMAILS_FROM_NAME: str, service name, e.g. Notify Service
EMAILS_FROM_EMAIL: email address, required

Template mount dir:
TEMPLATE_MOUNT_DIR: target dir where extra templates could be provided or uploaded to, default to /var/tmp

# Run with Podman

Run with production image:

  $ podman run --name notify --env-file dev.env --volume ./extra-template:/var/tmp:Z --volume ./app:/app:Z -p 8080:80 -t localhost/notify-service:base

Run dev image:

  $ podman run --name notify --env-file dev.env --rm --volume ./extra-template:/var/tmp:Z --volume ./app:/app:Z -p 8080:80 -t localhost/notify-service:dev

# Check Swagger UI

Open browser and access:
http://localhost:8080/docs
