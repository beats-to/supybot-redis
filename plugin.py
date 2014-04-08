###
# Copyright (c) 2014, beats to radio
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#pylint: disable=W0233
###

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import wrap
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.log as log
import supybot.world as world
import redis
import threading
from string import lower


class RedisListener(threading.Thread):
    """
    This class runs a thread for supy bot to subscribe to channel
    TODO: to channel
    """
    def __init__(self, plugin, irc, sender, to, channels):
        name = 'RedisListener(#%s)' % world.threadsSpawned
        world.threadsSpawned += 1
        threading.Thread.__init__(self, name=name)
        self.name = name
        self.irc = irc
        self.plugin = plugin
        self.redis = redis.Redis()
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channels)
        self.start()
        self.sender = sender
        self.to = to
        log.info('%s Started' % name)

    def run(self):
        for item in self.pubsub.listen():
            try:
                if item['type'] != 'message':
                    continue
                log.warning('{%s}' % item['data'][0:6])
                if item['channel'] == 'safehouse':
                    tokens = callbacks.tokenize(item['data'])
                    msg = ircmsgs.privmsg(self.to, item['data'], prefix=self.sender, msg=None)
                    self.plugin.Proxy(self.irc.irc, msg, tokens)
                    continue
                if lower(item['data'][0:7]) == '/topic ':
                    msg = ircmsgs.topic(item['channel'], item['data'][7:])
                    self.irc.queueMsg(msg)
                    continue
                msg = ircmsgs.privmsg(item['channel'], item['data'])
                self.irc.queueMsg(msg)
            # exceptions, sometimes you've gotta catch em all
            # supybot seemed to swallow mine
            #pylint: disable=W0703
            except Exception as error:
            #pylint: enable=W0703
                log.warning('Error sendering %s' % error)

    def die(self):
        """ Exit thread """
        log.info('Stopping %s' % self.name)
        self.pubsub.unsubscribe()


class Redis(callbacks.Plugin):
    """redisstatus to show the thread for this plugin
    """
    threaded = True

    def __init__(self, irc):
        self.__parent = super(Redis, self)
        self.__parent.__init__(irc)
        sender = self.registryValue('sender')
        to = self.registryValue('to')
        channels = [conf.supybot.nick()]
        for channel in self.registryValue('channels'):
            channels.append(channel)
        self.listener = RedisListener(self, irc, sender, to, channels)

    def redistatus(self, irc):
        """ How's it going? """
        irc.reply('my listener is %s' % self.listener)
    redistatus = wrap(redistatus)

    def die(self):
        """ Exit plugin """
        self.listener.die()
        self.__parent.die()

Class = Redis

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
