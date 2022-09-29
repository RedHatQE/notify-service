import logging
from pathlib import Path

import stomp

from app.core.config import settings


logger = logging.getLogger(__name__)

KEY_FILE = Path(settings.CERT_PATH).joinpath(settings.KEY_FILE_NAME)
CERT_FILE = Path(settings.CERT_PATH).joinpath(settings.CERT_FILE_NAME)
CA_CERTS = Path(settings.CERT_PATH).joinpath(settings.CA_CERTS_NAME)

MSG_BUS_HOSTS = []

if settings.MSG_BUS_HOST_1:
    MSG_BUS_HOSTS.append((settings.MSG_BUS_HOST_1, settings.MSG_BUS_PORT_1))
elif settings.MSG_BUS_HOST_2:
    MSG_BUS_HOSTS.append((settings.MSG_BUS_HOST_2, settings.MSG_BUS_PORT_2))

# Message body example from https://pagure.io/fedora-ci/messages/blob/master/f/examples/container-image.test.complete.json
MESSAGE_BODY_EXAMPLE = {
    "contact": {
        "name": "C3I Jenkins",
        "team": "DevOps",
        "url": "https://example.com",
        "docs": "https://example.com/user-documentation",
        "irc": "#some-channel",
        "email": "someone@example.com",
    },
    "run": {
        "url": "https://somewhere.com/job/ci-job/4794",
        "log": "https://somewhere.com/job/ci-job/4794/console",
        "log_raw": "https://somewhere.com/job/ci-job/4794/consoleText",
        "log_stream": "https://somewhere.com/job/ci-job/4794/consoleText",
        "debug": "https://somewhere.com/job/ci-job/4794/artifacts/debug.txt",
        "rebuild": "https://somewhere.com/job/ci-job/4794/rebuild/parametrized",
    },
    "artifact": {
        "type": "container-image",
        "repository": "someapp",
        "digest": "sha256:017eb7de7927da933a04a6c1ff59da0c41dcea194aaa6b5dd7148df286b92433",
        "pull_ref": "docker://registry.fedoraproject.org/someapp@sha256:017eb7de7927da933a04a6c1ff59da0c41dcea194aaa6b5dd7148df286b92433",
        "source": "git+https://src.fedoraproject.org/rpms/setup.git?#5e0ae23a",
        "id": "someapp@sha256:017eb7de7927da933a04a6c1ff59da0c41dcea194aaa6b5dd7148df286b92433",
    },
    "pipeline": {"id": "ac11dcddf99a", "name": "ci-job"},
    "test": {
        "type": "tier1",
        "category": "functional",
        "result": "failed",
        "namespace": "factory2.c3i-ci",
        "note": "Some notes.",
        "label": ["fast", "aarch64"],
        "xunit": "https://somewhere.com/job/ci-openstack/4794/artifacts/results.xml",
    },
    "system": [
        {
            "os": "docker.io/openshift/jenkins-slave-base-centos7:latest",
            "provider": "openshift",
            "architecture": "x86_64",
        }
    ],
    "notification": {"recipients": ["ovasik", "mvadkert"]},
    "generated_at": "2018-05-10 08:58:31.222602",
    "version": "0.2.1",
}


def make_connection(on_message_fn=None, on_error_fn=None):
    """
    Create a subscription to the message bus.
    """

    class NotifyListener(stomp.ConnectionListener):
        """
        NotifyListener handler Class
        """

        def __init__(self):
            self.conn = None
            self.keep_going = True

        def on_disconnected(self, *args, **kwargs):
            logger.info("=" * 72)
            logger.info("Disconnected")
            self.keep_going = False

        def on_error(self, headers, message):
            """
            Handler on error
            """
            on_error_fn and on_error_fn(self, headers, message)
            logger.info("=" * 72)
            logger.error("RECEIVED AN ERROR.")
            logger.error("Message headers:\n%s", headers)
            logger.error("Message body:\n%s", message)

        def on_message(self, headers, message):
            """
            Handler on message
            """
            on_message_fn and on_message_fn(self, headers, message)
            logger.debug("=" * 72)
            logger.debug("Message headers:\n%s", headers)
            logger.debug("Message body:\n%s", message)

        def on_receiver_loop_completed(self, *args):
            logger.debug("=" * 72)
            logger.info("Receiver loop ended")
            if self.keep_going:
                logger.info("Trying to reconnect")
                self._connect()
            else:
                self.conn.disconnect()

        def _connect(self):
            if not self.conn:
                self.conn = stomp.Connection(MSG_BUS_HOSTS)
                self.conn.set_listener("Notify Service Listener", self)
                self.conn.set_ssl(
                    for_hosts=MSG_BUS_HOSTS,
                    key_file=KEY_FILE,
                    cert_file=CERT_FILE,
                    ca_certs=CA_CERTS,
                )
            else:
                logger.info("Disconnecting existing Message Bus connection")
                self.conn.disconnect()
            logger.info("Connecting to Message Bus")
            self.conn.connect(wait=True)
            return self.conn

    return NotifyListener()._connect()


def quick_send(topic, headers, body):
    """
    Send a message then disconnect
    """

    conn = make_connection()

    conn.send(topic, body, headers=headers)

    logger.info("Message send succeed")
    conn.disconnect()
    logger.info("Disconnected with server")

    return conn
