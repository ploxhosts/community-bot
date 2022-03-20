import discord from 'discord.js';
import { RedisClientType } from 'redis';

import AutoMod from '../db/services/AutoMod';
import Guild from '../db/services/Guild';
import Message from '../db/services/Message';
import User from '../db/services/User';
import GuildMembers from '../db/services/GuildMembers';
import { badWordCheck } from '../utils/badWordCheck';
import { copyPastaCheck } from '../utils/copyPastaCheck';
import { spamCheck } from '../utils/spamCheck';

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
const checkTimes = (storedDate: number, currentDate: number): boolean => {
    const timeDifference = currentDate - storedDate;
    if (timeDifference < 60000 * 60) {
        return false;
    }
    return true;
};

module.exports = {
    name: 'messageCreate',
    async execute(message: discord.Message) {
        console.log('Message sent');
        if (!message.guild) {
            return;
        }


        // Creates a user if they don't exist
        let data;

        if (redis){
            data = await redis.get(
                `user:${message.author.id}:has_been_checked`
            );
        }

        // If the user has been checked in the last 60 minutes, don't check again and it's not a bot
        if (checkTimes(Number(data), Date.now()) && message.author.bot === false) {
            await User.createUser(
                message.author.id,
                message.author.username,
                message.author.discriminator,
                message.author.avatarURL() || undefined,
                undefined,
                0,
                0
            );

            if (redis){
                await redis.set(
                    `user:${message.author.id}:has_been_checked`,
                    Date.now()
                );
            }
        }

        // Creates a guild if they don't exist
        data = undefined;

        if (redis){
            data = await redis.get(
                `guild:${message.guild.id}:guild:has_been_checked`
            );
        }

        if (checkTimes(Number(data), Date.now())) {
            await Guild.createGuild(
                message.guild.id,
                message.guild.name,
                message.guild.iconURL(),
                message.guild.ownerId,
                getTier(message.guild.premiumTier),
                0,
                0,
                false,
                false,
                false,
                false
            );

            if (redis){
                await redis.set(
                    `guild:${message.guild.id}:guild:has_been_checked`,
                    Date.now()
                );
            }
        }

        if (message.member) {
            data = undefined;

            if (redis){
                data = await redis.get(
                    `guild:${message.guild.id}:${message.author.id}:guild:has_been_checked`
                );
            }

            if (checkTimes(Number(data), Date.now())) {
                await GuildMembers.createGuildMember(
                    message.guild.id,
                    message.author.id,
                    false,
                    message.member.roles.cache.map((role) => role.id),
                    message.member.nickname || message.author.username,
                    message.author.avatarURL() || `https://cdn.discordapp.com/embed/avatars/${Number.parseInt(message.author.discriminator) % 5}.png` ,
                    false
                );

                if (redis){
                    await redis.set(
                        `user:${message.author.id}:${message.author.id}:has_been_checked`,
                        Date.now()
                    );
                }
            }
        }

        await Message.createMessage(
            message.id,
            message.author.id,
            message.content,
            JSON.stringify(message.embeds),
            message.channel.id,
            message.guild.id,
            message.hasThread
        );

        const autoModule = await AutoMod.getGuildAutoMod(message.guild.id);

        if (!autoModule) {
            return console.log('No auto mod found', message.guild.id);
        }

        if (autoModule.message_spam_check) {
            const messagesSent = await Message.getMessagesFromUser(message.author.id);
            const messagesCount = !messagesSent ? 0 : messagesSent.length;
            const spamScore = await spamCheck(
                message.content,
                messagesCount,
                0,
                false,
                false,
                message.guild.id
            );
        }

        if (autoModule.message_pasta_check) {
            const copyPastas = await copyPastaCheck(message.content);
        }

        if (autoModule.bad_word_check) {
            const badwords = await badWordCheck(message.content, true); // TODO: replace true with guild config
        }
    },
    setRedis(redisIn: RedisClientType) {
        redis = redisIn;
    },
};
