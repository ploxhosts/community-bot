import discord from 'discord.js';
import { RedisClientType } from 'redis';

import Guild from '../db/services/Guild';
import AutoMod from '../db/services/AutoMod';
import BadWords from '../db/services/BadWords';
import Links from '../db/services/Links';

import GuildMember from '../db/services/GuildMembers';

import log from '../utils/log';
let redis: RedisClientType;

module.exports = {
    name: 'guildDelete',
    async execute(guild: discord.Guild) {

        log.debug('Left guild 1');

        // TODO: Run after 30 days of this happening (incase abusive user kicked it)
        await Guild.deleteGuild(
            guild.id
        );

        await AutoMod.deleteGuildAutoMod(guild.id);

        await GuildMember.deleteGuildMembers(guild.id); // Why take up space?

        await BadWords.deleteAll(guild.id);
        await Links.deleteAll(guild.id);

        // Don't delete users, they can remove data on the website
        
        log.info('Left guild', guild.name, guild.id);
    },
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
};
