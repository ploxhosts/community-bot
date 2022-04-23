import discord from 'discord.js';
import { RedisClientType } from 'redis';
import log from '../utils/log';
let redis: RedisClientType;

module.exports = {
    name: 'guildDelete',
    async execute(guild: discord.Guild) {
        log.info('Left guild', guild.name, guild.id);
    },
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
};
