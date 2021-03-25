<img src="docs/static/notify-logo.svg" height="75px"></img>

[![Flake8 Status](https://github.com/waynesun09/notify-service/workflows/Flake8/badge.svg)](https://github.com/waynesun09/notify-service/actions)
[![Helm Chart Lint and Test](https://github.com/waynesun09/notify-service/workflows/Lint%20and%20Test%20Charts/badge.svg)](https://github.com/waynesun09/notify-service/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# notify-service

Notify service with multiple supported target

This is a backend service build with FastAPI.

## Requirement

  - Python 3.8
  - Pipenv
  - Podman, buildah on Linux host
  - Helm 3
  - Redis

Check Pipfile for python packages.

## Deploy with Helm

### Update Helm chart value

Make a copy of the `chart/values.yaml`, e.g. dev.value.yaml and update.

Update api key:

    apiKeyValue: The API key to authenticate and access the apis, you could generate one with cmd `$openssl rand -hex 32`

SMTP related config:

    smtp.endpoint.enableTls: default to True
    smtp.endpoint.port: int, required
    smtp.endpoint.host: str, required
    smtp.endpoint.user: str, optional
    smtp.endpoint.password: str, optional

Email related config:

    fromName: str, service name, e.g. Notify Service
    fromEmail: str, the email from

Chat Webhook URL:

    chatWebhook.enabled: boolen, enable or disable chat webhook
    chatWebhook.gchat: str, Google Chat room webhook
    chatWebhook.slack: str, Slack room webhook

ActiveMQ message bus:

    activeMQ.enabled: boolen, enable or disable ActiveMQ message bus config
    activeMQ.cert_mount_path: str, specify where the certs will be mounted in the container
    activeMQ.ca_certs: multiline str, the CA server certificate
    activeMQ.client_cert: multiline str, the message bus client certificate
    activeMQ.client_key: multiline str, the message bus client key
    activeMQ.msg_bus_host_1: str, the message bus host name
    activeMQ.msg_bus_host_1: int, the message bus host port
    activeMQ.msg_bus_host_2: str, optional, the second message bus host name
    activeMQ.msg_bus_host_2: int, optional, the second message bus host port

IRC config:

    irc.enabled: boolen, enable or disable IRC config
    irc.server: str, IRC host name
    irc.port: int, the IRC host port
    irc.ssl: boolen, enable or disable ssl, make sure set the right port if is enabled
    irc.nickname: str, IRC username
    irc.password: str, set if password exist
    irc.default_target: str, the default channel name start with '#' or username

Persistent volume config:

    persistence.enabled: boolen, true or false
    persistence.subPath: str, sub path
    persistence.existingClaim, str, using existing pvc
    persistence.accessMode: str, ReadWriteOnce, ReadWriteMany or ReadOnlyOnce
    persistence.size: str, volume size, e.g. 1G
    persistence.storageClass: str, storage class name
    persistence.VolumeName: str, volume name

If deploy to Openshift (default) update OpenShift route url:

    openshift.enabled: boolen, true or false
    openshift.hosts: str, the full app host name

or else update the ingress part.

### Run helm install

Make sure you have login your cluster, run with updated chart values:

    $ helm install ns chart/ -f dev.value.yaml

After deploy done access the app Swagger UI:

    http://${ openshift.hosts }:8080/docs

## Development

For develop, build, test and debug, please check [Development Doc](docs/development.md) for more info.

## Contributing
You can contribute by:

- Raising any issues you find using notify-service
- Fixing issues by opening [Pull Requests](https://github.com/waynesun09/notify-service/pulls)
- Submitting a patch or opening a PR
- Improving documentation
- Talking about notify-service

All bugs, tasks or enhancements are tracked as [GitHub issues](https://github.com/waynesun09/notify-service/issues).

## CI
The Github Action will run flake8 against .py files.
