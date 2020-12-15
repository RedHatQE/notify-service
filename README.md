# notify-service

Notify service with multiple supported target

This is a backend service build with FastAPI.

# Requirement

  - Python 3.8
  - Pipenv
  - Podman, buildah on Linux host
  - Redis

Check Pipfile for python packages.

# Setup

## Build container image

Build production image with:

    $ buildah bud -f Dockerfile -t notify-service:base

Build dev image with:

    $ buildah bud -f Dockerfile.dev -t notify-service:dev

## Update .env

Make a copy of the env file and update the parameters.

Auth API key:

    SECRET_KEY: The API key to authenticate and access the apis, you could generate one with cmd `$openssl rand -hex 32`

SMTP related config:

    SMTP_TLS: default to True
    SMTP_PORT: str, required
    SMTP_HOST: str, required
    SMTP_USER: str, optional
    SMTP_PASSWORD: str, optional
    EMAILS_FROM_NAME: str, service name, e.g. Notify Service
    EMAILS_FROM_EMAIL: email address, required

Redis config:

    REDIS_URI: redis uri, required, e.g. redis://${host_ip}:${redis_port}
    REDIS_PASSWORD: redis password if server is configured with password, default to None

Template mount dir:

    TEMPLATE_MOUNT_DIR: target dir where extra templates could be provided or uploaded to, default to /var/tmp

# Run with Podman

Start Redis server at local:

    $ buildah pull centos7/redis-5-centos7
    $ podman run -d --name redis -e REDIS_PASSWORD=${REDIS_PASSWORD} -p 35525:6379 quay.io/centos7/redis-5-centos7

**Note**: 35525 is the redis port exposed on the host, and for rootless container to access the redis, the Redis URI will be redis://${host_ip}:35525

Run with production image:

    $ podman run -d --name notify --env-file dev.env --volume ./extra-template:/var/tmp:Z -p 8080:80 -t localhost/notify-service:base

Run dev image:

    $ podman run --name notify --env-file dev.env --rm --volume ./extra-template:/var/tmp:Z --volume ./app:/app:Z -p 8080:80 -t localhost/notify-service:dev

Stop the container:

    $ podman stop notify

# Check Swagger UI

Open browser and access:
http://localhost:8080/docs

# Run pytest

Install pytest:

    $ pipenv shell
    $ pip install pytest py pytest-dotenv

Tests are added under app/tests, make sure you have updated parameters or export them in env, then run:

    $ py.test --rootdir app/ --envfile dev.env
