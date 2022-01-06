<img src="docs/static/notify-logo.svg" height="75px"></img>

[![Flake8 Status](https://github.com/waynesun09/notify-service/workflows/Flake8/badge.svg)](https://github.com/waynesun09/notify-service/actions)
[![Helm Chart Lint and Test](https://github.com/waynesun09/notify-service/workflows/Lint%20and%20Test%20Charts/badge.svg)](https://github.com/waynesun09/notify-service/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# notify-service

Notify service with multiple supported target

This is a backend service build with FastAPI.

## Requirement

  - Python 3.9
  - Pipenv
  - Podman, buildah on Linux host
  - Helm 3
  - Redis

Check Pipfile for python packages.

## Deploy with Helm

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/S0Vn9BM3iMA/0.jpg)](https://youtu.be/S0Vn9BM3iMA)


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

Make sure you have login your cluster.

#### Install latest from helm repo
    
Add helm repo with:

    $ helm repo add notify https://waynesun09.github.io/notify-service/
    
Check the latest release on the project with:

    $ helm search repo notify-service
    
Then install with:

    $ helm install ns notify-service -f dev.value.yaml
    
#### Install from current repo:

    $ helm install ns chart/ -f dev.value.yaml

## Access the service and API docs

The API docs are automatically generated on Swagger UI and Redoc UI.

### Swagger UI

After deployment is done access the app Swagger UI:

    http://${ openshift.hosts }:8080/docs

You could try the apis on Swagger UI and check parameters and request body samples in description.

### Redoc

After the deployment is done, Redoc UI could be accessed at:

    http://${ openshift.hosts }:8080/redoc

The Redoc UI is more developer friendly with detail on descriptins, parameters, schemas, payload, code samples, etc.

### Request body template and samples

For each API, both Swagger UI and Redoc UI provide request body schema, while Redoc UI with more details and provide drop list with different supported schemas and details.

Check [sample](docs/sample) dir under doc for some request body with the matching template names under [app/templates/build](app/templates/build) or [app/templates/src](app/templates/src).

## Templates

The repo have provided few templates under `app/templates/`, which includes templates for email, Google Chat and Slack.

All templates are Jinja templates. Check following for how each target templates are generated, remember to add new request body sample under [sample](docs/sample) dir for each templates.

### Email MJML template

The email templates are generated with [MJML](https://mjml.io/documentation/), you could create a mjml template online with [try-it-live](https://mjml.io/try-it-live/).

After edit done, you could save the mjml file with suffix `.mjml` under [app/templates/src](app/templates/src), and SAVE THE HTML file with suffix '.html' under [app/templates/build](app/templates/build), the `HTML` file will be directly used as email template.
Then you could raise PR for adding new templates, make sure your template is unique.

**Note:** Use Jinja semantic for templating.

### Google Chat template

Google chat message support simple text and cards:

- [Simple text](https://developers.google.com/hangouts/chat/reference/message-formats/basic) contains plain text content with limited text formatting.
- [Cards](https://developers.google.com/hangouts/chat/reference/message-formats/cards) define the format, content, and behavior of cards to be displayed in the target space.

Follow the docs and create your own google chat templates and save the template file with suffix '.jinja' under [app/templates/build](app/templates/build).
Then you could raise PR for adding new templates, make sure your template is unique.

**Note:** Use Jinja semantic for templating.

### Slack template

Slace message use mrkdwn formatting syntax and support layouts, check:

- [Formatting text](https://api.slack.com/messaging/composing/formatting) in messages
- [Composing layouts](https://api.slack.com/messaging/composing/layouts) for layouts

Follow the docs and create your own slack templates and save the template file with suffix '.jinja' under [app/templates/build](app/templates/build).
Then you could raise PR for adding new templates, make sure your template is unique.

**Note:** Use Jinja semantic for templating.

### Upload templates

No need to raise PRs for each template, if the template is not for common use for all users, user could choose upload templates to a running instance use the Update Tempalte API.
Check on the Swagger UI or Redoc UI with PUT method under template APIs on a running instance.

The templates are saved on a volume mounted to dir specified as `templateMountDir` in helm chart, make sure `persistence.enabled` is true. Then the templates will be saved in a persistent volumn on your OCP cluster.

TODO: Supprt S3 storage

### Remote url templates

User could also store templates on a github repo or other places which could be accessed by url, then could specify the template url in email, gchat, slack target apis.

For remote urls, cache with default 300 secs timeout will be enabled, so no fetching if request same template between 300 secs.

**Note:** Make sure you have matching request body for Jinja templating.

## Development

For develop, build, test and debug, please check [Development Doc](docs/development.md) for more info.

## Helm Chart Release

For update and release the Helm chart of the repo to github webpage, please check [Helm Chart Release Doc](docs/chart_release.md) for more info.

## Contributing
You can contribute by:

- Raising any issues you find using notify-service
- Fixing issues by opening [Pull Requests](https://github.com/waynesun09/notify-service/pulls)
- Submitting a patch or opening a PR
- Improving documentation
- Talking about notify-service

All bugs, tasks or enhancements are tracked as [GitHub issues](https://github.com/waynesun09/notify-service/issues).

## CI
The Github Action will run flake8 against .py files, pytest and helm chart test.
