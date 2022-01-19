import discord from 'discord.js';
import { badWordCheck } from '../utils/badWordCheck';
import { copyPastaCheck } from '../utils/copyPastaCheck';
import { spamCheck } from '../utils/spamCheck';

import { RedisClientType } from 'redis';

let redis: RedisClientType;

module.exports = {
	name: 'messageCreate',
	async execute(message: discord.Message) {
		console.log("Message sent");
		const badwords = await badWordCheck(message.content, true);
    const copyPastas = await copyPastaCheck(message.content);
    const spamScore = await spamCheck(message.content, 0)
    console.log(badwords, copyPastas, spamScore);
	},
  setRedis(redis: RedisClientType) {
    redis = redis;
  }
};