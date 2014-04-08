supybot-redis
=============

Plugin for supybot to subscribe to redis for commands and messages
Redis plugin for supybot

It will subscribe to a channel with the same name as the bot, when messages
are received on that channel they will be used as commands for the bot

It will subscribe to channels, one for each room as defined in it's config
When a message is recieved on the channel, if it is IRC message parsable
it will update the room

Finally, it will provide a some commands for managing the KV store
