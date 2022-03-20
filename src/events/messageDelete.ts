import discord from 'discord.js';
import { RedisClientType } from 'redis';

import Message from '../db/services/Message';

let redis: RedisClientType;

module.exports = {
    name: 'messageDelete',
    async execute(message: discord.Message) {
        if (!message.guild) {
            return;
        }

        await Message.deleteMessage(message.id);

        console.log('Message deleted');

        // TOOD: Send to log channel
    },
    setRedis: function (NewRedis: RedisClientType) {
        redis = NewRedis;
    },
};
