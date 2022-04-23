import discord from 'discord.js';
import { RedisClientType } from 'redis';
import GuildEmbeds from '../utils/embeds/GuildEmbeds';
import log from '../utils/log';
let redis: RedisClientType;

module.exports = {
    name: 'guildCreate',
    async execute(guild: discord.Guild) {

        const embed = GuildEmbeds.createGuildEmbed(); // Get the default guild embed

        let sent = false;

        try {
            if (guild.systemChannel) {
                await guild.systemChannel.send({ embeds: [embed] });
                sent = true;
            }
        } catch (error) {
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
                log.info('Could not direct message owner of a guild join', guild.id, guild.ownerId);
            }
        }
        await guild.leave();
        log.info('Joined guild, leaving', guild.name, guild.id);
    },
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
};
