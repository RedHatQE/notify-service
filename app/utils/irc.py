import asyncio
import logging

from irc import client_aio
from irc import client
from typing import Any, Optional

from app.core.config import settings


logger = logging.getLogger(__name__)


class AioReactor(client_aio.AioReactor):
    """
    Processes message from on or more asyncio-based IRC server connections.

    This class inherits from irc.client_aio.Reactor, and mainly replaces
    the process_forever function.
    """

    def process_forever(self):
        """Override the `process_forever` function and Skip infinite loop.

        The event loop aquired from get_event_loop() have already been
        started in FastAPI, so did not need to call `run_forever` to
        start the loop.
        """
        pass


class AioSimpleIRCClient(client.SimpleIRCClient):
    """Replace the irc.client_aio.AioSimpleIRCClient class.

    The difference is using the override AioReactor for
    asyncio-based loops. Also the use `asyncio.ensure_future` for the
    connection rather than start the loop with `run_until_complete` as
    the loop have already been started.

    For more information on AioSimpleIRCClient, see the documentation
    on irc.client.SimpleIRCClient
    """

    reactor_class = AioReactor

    def connect(self, *args, **kwargs):
        asyncio.ensure_future(self.connection.connect(*args, **kwargs))


class AioIRCCat(AioSimpleIRCClient):
    def __init__(self, target, message):
        client.SimpleIRCClient.__init__(self)
        self.future = None
        self.target = target
        self.message = message


    def on_welcome(self, connection, event):
        if client.is_channel(self.target):
            connection.join(self.target)
        else:
            self.future = asyncio.ensure_future(
                self.send_it(), loop=connection.reactor.loop
            )


    def on_join(self, connection, event):
        self.future = asyncio.ensure_future(
            self.send_it(), loop=connection.reactor.loop
        )


    def on_disconnect(self, connection, event):
        if self.future:
            self.future.cancel()


    async def send_it(self):
        self.connection.privmsg(self.target, self.message)
        self.connection.quit("Notify done, Ciao!")


async def send_message(message: str, target: Optional[str]) -> Any:
    """
    Connect to the IRC server and send out message
    """
    server = settings.IRC_SERVER
    port = settings.IRC_SERVER_PORT
    nickname = settings.IRC_NICKNAME
    password = settings.IRC_PASSWORD
    if not target:
        target = settings.IRC_TARGET

    c = AioIRCCat(target, message)
    c.connect(server, port, nickname, password=password)

    try:
        c.start()
    finally:
        c.connection.disconnect()
