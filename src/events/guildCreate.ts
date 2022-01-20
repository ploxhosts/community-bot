import discord from 'discord.js';
import {createGuild, getGuild} from '../db/services/Guild';
import { RedisClientType } from 'redis';
import createGuildEmbed from '../utils/embeds/createGuildEmbed';

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
}

module.exports = {
	name: 'guildCreate',
	async execute(guild: discord.Guild) {
		console.log("Joined guild");
		await createGuild(guild.id, guild.name, guild.iconURL(), guild.ownerId
      , getTier(guild.premiumTier), 0, 0, false, false, false, false);
    const guild_data = await getGuild(guild.id);
    if (guild_data) {
      console.log(guild_data);
    }
    const embed = createGuildEmbed();
    
    let sent = false;

    if (guild.systemChannel) {
      await guild.systemChannel.send({ embeds: [embed] });
      sent = true;
    }

    guild.channels.cache.forEach(async (channel)=>{
      if (channel && channel.isText() && !sent){
        if (guild.me && guild.me.permissionsIn(channel).has("SEND_MESSAGES")){
          await channel.send({ embeds: [embed] });
          sent = true;
        } else {
          channel.send({ embeds: [embed] });
          sent = true;
        }
      }
    })
	},
  setRedis: function(redis: RedisClientType) {
    redis = redis;
  }
};