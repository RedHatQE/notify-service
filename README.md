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

    chatWebhook.gchat:
    chatWebhook.slack:

If deploy to Openshift (default) update OpenShift route url:

    openshift.enabled: true
    openshift.hosts:

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
