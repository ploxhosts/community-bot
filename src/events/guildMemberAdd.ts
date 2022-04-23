import discord from 'discord.js';
import { RedisClientType } from 'redis';
import User from '../db/models/User';
import log from '../utils/log';
import GuildEmbeds from '../utils/embeds/GuildEmbeds';
import GuildJoins from '../db/models/GuildJoins';
let redis: RedisClientType;

module.exports = {
    name: 'guildMemberAdd',
    async execute(member: discord.GuildMember) {
        
        log.debug("Member joined", member.user.username, member.user.id);

        let user = await User.findOne({ where: { id: member.user.id }});
        if (!user) {
            user = User.build({
                id: member.user.id,
                username: member.user.username,
                discriminator: member.user.discriminator,
                avatar: member.user.avatarURL() || `https://cdn.discordapp.com/embed/avatars/${Number.parseInt(member.user.discriminator) % 5}.png`,
                premium: 0,
                banned: false,
                verified: false,
                timedOut: false,
                lastSeen: Date.now(),
                nickname: member.nickname || member.user.username,
            });
            await user.save();
        }
    
        GuildJoins.build({
            user_id: member.user.id,
            invite_link: "", // TODO: Check what invite link they used
        }).save();


    },
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
};
