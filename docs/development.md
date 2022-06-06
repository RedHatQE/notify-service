# Development

Make sure you have checked the requirement and have checked Pipfile for python packages.

## Build container image

Build production image with:

    $ buildah bud -f Dockerfile -t notify-service:base

Build dev image with:

    $ buildah bud -f Dockerfile.dev -t notify-service:dev

Then push the image to quay.io

## Deploy with Podman

### Update .env

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

Chat webhook config:

    GCHAT_WEBHOOK_URL: str, optional, Google Chat room webhook url
    SLACK_WEBHOOK_URL: str, optional, Slack room webhook url

ActiveMQ message bus config:

    CERT_PATH: str, the message bus cert dir path
    KEY_FILE_NAME: str, the message bus client cert key file name
    CERT_FILE_NAME: str, the message bus client cert file name
    CA_CERTS_NAME: str, the CA server cert file name

    MSG_BUS_HOST_1: str, the ActiveMQ message host name
    MSG_BUS_PORT_1: int, the ActiveMQ message host port
    MSG_BUS_HOST_2: str, optional, the second ActiveMQ message host name
    MSG_BUS_PORT_2: int, optional, the second ActiveMQ message host port

IRC config:

    IRC_SERVER: str, optional, the IRC server host name
    IRC_SERVER_PORT, int, optional, the IRC server host port
    IRC_SSL: boolen, optional, enable or disable ssl, make sure set the right port if is enabled
    IRC_NICKNAME: str, optional, irc nickname
    IRC_PASSWORD: str, optional, set if password not empty
    IRC_TARGET: str, optional, default channel name start with '#' or username

Redis config:

    REDIS_URI: redis uri, required, e.g. redis://${host_ip}:${redis_port}
    REDIS_PASSWORD: redis password if server is configured with password, default to None

Template mount dir:

    TEMPLATE_MOUNT_DIR: target dir where extra templates could be provided or uploaded to, default to /var/tmp

Jira congif:

    JIRA_URL: Your Jira instance URL, required, e.g. https://issues.redhat.com
    JIRA_TOKEN: Your Jira personal token, required

### Run with Podman

Start Redis server at local:

    $ buildah pull centos7/redis-5-centos7
    $ podman run -d --name redis -e REDIS_PASSWORD=${REDIS_PASSWORD} -p 35525:6379 quay.io/centos7/redis-5-centos7

**Note**: 35525 is the redis port exposed on the host, and for rootless container to access the redis, the Redis URI will be redis://${host_ip}:35525

Run with production image:

    $ podman run -d --name notify --env-file dev.env --volume ./extra-template:/var/tmp:Z --volume ./certs/:/var/certs:Z -p 8080:8080 -t quay.io/waynesun09/notify-service:latest

Run dev image:

    $ podman run --name notify --env-file dev.env --rm --volume ./extra-template:/var/tmp:Z --volume ./certs/:/var/certs:Z --volume ./app:/app:Z -p 8080:8080 -t localhost/notify-service:dev

**Note**: Copy the cert files to the ./certs dir if enalbed ActiveMQ config

Stop the container:

    $ podman stop notify

### Check Swagger UI and Redoc

Open browser and access:

    http://localhost:8080/docs

    http://localhost:8080/redoc

## Run pytest with podman

Tests are added under app/tests, make sure you have updated parameters in .test.env or export them in env, then run:

    $ podman run --name notify-test --env-file .test.env --entrypoint= --rm -i --volume ./extra-template:/var/tmp:Z --volume ./app:/opt/app-root/app:Z  -p 8080:8080 -t quay.io/waynesun09/notify-service:latest /bin/bash -c 'pipenv run pytest app/'
