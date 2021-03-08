import asyncio
import logging

from irc import client_aio
from irc import client
from irc.connection import AioFactory

from typing import Any, Optional

from app.core.config import settings


logger = logging.getLogger(__name__)


class AioConnection(client_aio.AioConnection):
    """
    An IRC server connection.

    AioConnection objects are instantiated by calling the server
    method on a AioReactor object.

    Note: because AioConnection inherits from
    irc.client.ServerConnection, it has all the convenience
    methods on ServerConnection for handling outgoing data,
    including (but not limited to):

        * join(channel, key="")
        * part(channel, message="")
        * privmsg(target, text)
        * privmsg_many(targets, text)
        * quit(message="")

    And many more.  See the documentation on
    irc.client.ServerConnection for a full list of convience
    functions available.
    """

    async def connect(
        self,
        server,
        port,
        nickname,
        password=None,
        username=None,
        ircname=None,
        ssl=False,
        connect_factory=None,
    ):
        """Connect/reconnect to a server.

        Arguments:

        * server - Server name
        * port - Port number
        * nickname - The nickname
        * password - Password (if any)
        * username - The username
        * ircname - The IRC name ("realname")

        * connect_factory - An async callable that takes the event loop and the
          server address, and returns a connection (with a socket interface)

        This function can be called to reconnect a closed connection.

        Returns the AioProtocol instance (used for handling incoming
        IRC data) and the transport instance (used for handling
        outgoing data).
        """
        if self.connected:
            self.disconnect("Changing servers")

        self.buffer = self.buffer_class()
        self.handlers = {}
        self.real_server_name = ""
        self.real_nickname = nickname
        self.server = server
        self.port = port
        self.server_address = (server, port)
        self.nickname = nickname
        self.username = username or nickname
        self.ircname = ircname or nickname
        self.password = password
        self.ssl = ssl
        if not connect_factory:
            self.connect_factory = AioFactory(ssl=ssl)
        else:
            self.connect_factory = connect_factory

        protocol_instance = self.protocol_class(self, self.reactor.loop)
        connection = self.connect_factory(protocol_instance, self.server_address)
        transport, protocol = await connection

        self.transport = transport
        self.protocol = protocol

        self.connected = True
        self.reactor._on_connect(self.protocol, self.transport)

        # Log on...
        if self.password:
            self.pass_(self.password)
        self.nick(self.nickname)
        self.user(self.username, self.ircname)
        return self


class AioReactor(client_aio.AioReactor):
    """
    Processes message from on or more asyncio-based IRC server connections.

    This class inherits from irc.client_aio.Reactor, and mainly replaces
    the process_forever function.
    """

    connection_class = AioConnection

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

    async def connect(self, *args, **kwargs):
        await asyncio.gather(self.connection.connect(*args, **kwargs))


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
    ssl = settings.IRC_SSL
    if not target:
        # Use default channel from settings
        target = settings.IRC_TARGET

    c = AioIRCCat(target, message)
    await c.connect(server, port, nickname, password=password, ssl=ssl)

    try:
        c.start()
    finally:
        c.connection.disconnect()
