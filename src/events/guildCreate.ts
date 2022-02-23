import discord from 'discord.js';
import { RedisClientType } from 'redis';

import GuildClass from '../db/services/Guild';
import createGuildEmbed from '../utils/embeds/createGuildEmbed';
import log from '../utils/log';
let redis: RedisClientType;

const getTier = (tier: string): number => {
    switch (tier) {
        case 'TIER_1':
            return 1;
        case 'TIER_2':
            return 2;
        case 'TIER_3':
            return 3;
        default:
            return 0;
    }
};

module.exports = {
    name: 'guildCreate',
    async execute(guild: discord.Guild) {
        const Guild = new GuildClass();
        log.debug('Joined guild 1');

        const guildData = await Guild.createGuild(
            guild.id,
            guild.name,
            guild.iconURL(),
            guild.ownerId,
            getTier(guild.premiumTier),
            0,
            0,
            false,
            false,
            false,
            false
        );

        if (!guildData) {
            log.error(`Failed to create guild ${guild.id}`);
        }
        const botCount = guild.members.cache.filter(
            (member) => member.user.bot
        ).size; // Amount of bots that are in a guild

        const memberCount = guild.members.cache.filter(
            (member) => !member.user.bot
        ).size; // Amount of members excluding bots that are in a guild

        if (botCount > 50) {
            if (memberCount < 400) { // If bot count is greater than 50 and member count is less than 400
                await guild.leave();
                log.info('Left suspicious guild', guild.name, guild.id);
            } else if (memberCount > 1000) { // If bot count is greater than 50 and member count is greater than 1000
                log.info(
                    'Possible suspicious guild',
                    memberCount,
                    guild.id,
                    guild.ownerId,
                    botCount
                );
            }
        }

        const embed = createGuildEmbed(); // Get the default guild embed

        let sent = false;

        try {
            if (guild.systemChannel) { // If the guild has a system channel such as where it welcomes members
                await guild.systemChannel.send({ embeds: [embed] });
                sent = true;
            }
        } catch (error) {
            // eslint-disable-next-line unicorn/no-array-for-each
            guild.channels.cache.forEach(async (channel) => {
                if (
                    channel &&
                    channel.isText() &&
                    !sent &&
                    guild.me &&
                    guild.me.permissionsIn(channel).has('SEND_MESSAGES')
                ) {
                    try {
                        
                        await channel.send({ embeds: [embed] });
                        sent = true;
                    } catch (error: any) {
                       log.error("Error sending guild embed", error);
                    }
                }
            });
        }
        
        if (!sent) {
            log.info('Could not find channel', guild.id);
            try {    
                guild.fetchOwner().then((owner) => {
                    owner.send({ embeds: [embed] });
                });
            } catch {
                log.info('Could not direct message owner', guild.id, guild.ownerId);
            }
        }
        
        log.info('Joined guild', guild.name, guild.id);
    },
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
};
