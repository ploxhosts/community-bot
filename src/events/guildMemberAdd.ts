import discord from 'discord.js';
import { RedisClientType } from 'redis';

import AutoModClass from '../db/services/AutoMod';
import UserClass from '../db/services/User';
import GuildMemberClass from '../db/services/GuildMembers';

import log from '../utils/log';
import GuildEmbedsClass from '../utils/embeds/GuildEmbeds';
let redis: RedisClientType;

module.exports = {
    name: 'guildMemberAdd',
    async execute(member: discord.GuildMember) {
        const AutoMod = new AutoModClass();
        const GuildMember = new GuildMemberClass();
        const User = new UserClass();
        const guildEmbeds = new GuildEmbedsClass();
        
        log.debug("Member joined", member.user.username, member.user.id);

        await User.createUser(
            member.user.id,
            member.user.username,
            member.user.discriminator,
            member.user.avatarURL() || `https://cdn.discordapp.com/embed/avatars/${Number.parseInt(member.user.discriminator) % 5}.png`,
            undefined,
            0,
            0
        );

        await GuildMember.createGuildMember(
            member.guild.id,
            member.user.id,
            false,
            [],
            member.nickname || member.user.username,
            member.user.avatarURL() || `https://cdn.discordapp.com/embed/avatars/${Number.parseInt(member.user.discriminator) % 5}.png`,
            false,
        );

        await GuildMember.memberJoin(member.guild.id, member.user.id, ""); // TODO: Invite manager here

        const AutoModSettings = await AutoMod.getGuildAutoMod(member.guild.id);

        // User date check
        if (AutoModSettings != false && AutoModSettings.user_date_check) {
            const userCreatedDate = new Date(member.user.createdAt);
            const minimumUserAgeDate = new Date(
                userCreatedDate.getTime() + AutoModSettings.minimum_user_age * 24 * 60
            );
            if (minimumUserAgeDate < new Date()) {
                if (member.kickable) {
                    if (AutoModSettings.log_channel){
                        const embed = guildEmbeds.createUnderageKickEmbed(member.user);
                        const channel = member.guild.channels.cache.get(AutoModSettings.log_channel);
                        channel && (channel as discord.TextChannel).send({embeds: [embed]});
                        return await member.kick("User is too young");
                    }
                } else {
                    log.info("Member is not kickable", member.user.username, member.user.id, member.guild.id);
                    if (AutoModSettings.log_channel){
                        const embed = guildEmbeds.MissingPermissionsEmbed(["KICK_MEMBERS"]);
                        const channel = member.guild.channels.cache.get(AutoModSettings.log_channel);
                        channel && (channel as discord.TextChannel).send({embeds: [embed]});
                    } 
                }
            }   
        }
        



    },
    setRedis: function (redisIn: RedisClientType) {
        redis = redisIn;
    },
};
