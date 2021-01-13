import logging
import sys
import stomp

from pathlib import Path

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
            logger.error('RECEIVED AN ERROR.')
            logger.error('Message headers:\n%s', headers)
            logger.error('Message body:\n%s', message)

        def on_message(self, headers, message):
            """
            Handler on message
            """
            on_message_fn and on_message_fn(self, headers, message)
            logger.debug("=" * 72)
            logger.debug('Message headers:\n%s', headers)
            logger.debug('Message body:\n%s', message)

        def on_receiver_loop_completed(self, *args):
            logger.debug("=" * 72)
            logger.info('Receiver loop ended')
            if self.keep_going:
                logger.info('Trying to reconnect')
                self._connect()
            else:
                sys.exit(0)

        def _connect(self):
            if not self.conn:
                self.conn = stomp.Connection(MSG_BUS_HOSTS)
                self.conn.set_listener('Notify Service Listener', self)
                self.conn.set_ssl(for_hosts=MSG_BUS_HOSTS,
                                  key_file=KEY_FILE,
                                  cert_file=CERT_FILE,
                                  ca_certs=CA_CERTS)
            else:
                logger.info('Disconnecting existing Message Bus connection')
                self.conn.disconnect()
            logger.info('Connecting to Message Bus')
            self.conn.connect(wait=True)
            return self.conn

    return NotifyListener()._connect()


def quick_send(topic, headers, body):
    """
    Send a message then disconnect
    """

    conn = make_connection()

    conn.send(topic, body, headers=headers)

    logger.info('Message send succeed')
    conn.disconnect()
    logger.info('Disconnected with server')

    return conn
