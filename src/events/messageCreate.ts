import discord from 'discord.js';
import { RedisClientType } from 'redis';

import { getGuildAutoMod as getGuildAutoModule } from '../db/services/AutoMod';
import { createGuild } from '../db/services/Guild';
import { createMessage, getMessageFromUser } from '../db/services/Message';
import { createUser } from '../db/services/User';
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

module.exports = {
    name: 'messageCreate',
    async execute(message: discord.Message) {
        console.log('Message sent');

        if (!message.guild) {
            return;
        }

        let data;

        if (redis)
            data = await redis.get(
                `user:${message.author.id}:has_been_checked`
            );

        if (!data) {
            await createUser(
                message.author.id,
                message.author.username,
                message.author.discriminator,
                message.author.avatarURL(),
                undefined,
                0,
                0
            );

            if (redis)
                await redis.set(
                    `user:${message.author.id}:has_been_checked`,
                    'true'
                );
        }

        data = undefined;

        if (redis)
            data = await redis.get(
                `guild:${message.guild.id}:guild:has_been_checked`
            );

        if (!data) {
            await createGuild(
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

            if (redis)
                await redis.set(
                    `guild:${message.guild.id}:guild:has_been_checked`,
                    'true'
                );
        }

        await createMessage(
            message.id,
            message.author.id,
            message.content,
            message.embeds.toString(),
            message.channel.id,
            message.guild.id,
            message.hasThread
        );
        const autoModule = await getGuildAutoModule(message.guild.id);

        if (!autoModule) {
            return;
        }

        if (autoModule.message_spam_check) {
            const messagesSent = await getMessageFromUser(message.author.id);
            const messagesCount = !messagesSent ? 0 : messagesSent.length;
            const spamScore = await spamCheck(message.content, messagesCount);
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
