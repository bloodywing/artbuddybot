#!/usr/bin/env python

"""IRC Bot
"""


import sys


from circuits import Component
from circuits.net.sockets import TCPClient, connect
from circuits.protocols.irc import IRC, PRIVMSG, USER, NICK, JOIN, NOTICE

from circuits.protocols.irc import ERR_NICKNAMEINUSE
from circuits.protocols.irc import RPL_ENDOFMOTD, ERR_NOMOTD

import requests


class Bot(Component):

    # Define a separate channel so we can create many instances of ``Bot``
    channel = "artbuddy_test"

    def init(self, host="irc.freenode.net", port="6667", channel=channel):
        self.host = host
        self.port = int(port)
        self.nick = 'ArtBot_dev'

        # Add TCPClient and IRC to the system.
        TCPClient(channel=self.channel).register(self)
        IRC(channel=self.channel).register(self)

    def ready(self, component):
        """Ready Event

        This event is triggered by the underlying ``TCPClient`` Component
        when it is ready to start making a new connection.
        """

        self.fire(connect(self.host, self.port))

    def connected(self, host, port):
        """connected Event

        This event is triggered by the underlying ``TCPClient`` Component
        when a successfully connection has been made.
        """

        self.fire(NICK(self.nick))
        self.fire(USER("circuits", "circuits", host, "Artbuddy IRC Bot by epicmuffin/bloodywing"))

    def disconnected(self):
        """disconnected Event

        This event is triggered by the underlying ``TCPClient`` Component
        when the connection is lost.
        """

        raise SystemExit(0)

    def numeric(self, source, numeric, *args):
        """Numeric Event

        This event is triggered by the ``IRC`` Protocol Component when we have
        received an IRC Numberic Event from server we are connected to.
        """

        if numeric == ERR_NICKNAMEINUSE:
            self.fire(NICK("{0:s}_".format(args[0])))
        elif numeric in (RPL_ENDOFMOTD, ERR_NOMOTD):
            self.fire(JOIN("#artbuddy_test"))

    def privmsg(self, source, target, message):
        """Message Event

        This event is triggered by the ``IRC`` Protocol Component for each
        message we receieve from the server.
        """
        if message.startswith('!mods'):
            message = ', '.join(self._mods())
            self.fire(PRIVMSG(target, message))
        #if target.startswith("#"):
        #    self.fire(PRIVMSG(target, message))
        #else:
        #    self.fire(PRIVMSG(source[0], message))
            
    def join(self, source, channel):
        if source[0].lower() == self.nick.lower():
            print("Joined %s" % channel)
        else:
            
            for line in self._return_faq().split('\n'):
                self.fire(NOTICE(source[0], line))
            
    def _return_faq(self):
        _ = requests.get('https://raw.githubusercontent.com/bloodywing/artbuddybot_text/master/faq.txt')
        return _.text
        
    def _mods(self):
        _ = requests.get('http://www.reddit.com/r/ArtBuddy/about/moderators.json')
        mods_json = _.json()
        print(mods_json)
        return [entry['name'] for entry in mods_json['data']['children']]
        


# Configure and run the system
bot = Bot(*sys.argv[1:])

from circuits import Debugger
Debugger().register(bot)

# To register a 2nd ``Bot`` instance. Simply use a separate channel.
# Bot(*sys.argv[1:], channel="foo").register(bot)

bot.run()