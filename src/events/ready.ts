import discord from 'discord.js';
import { RedisClientType } from 'redis';

let redis: RedisClientType;

module.exports = {
	name: 'ready',
	once: true,
	async execute(client: discord.Client) {
		console.log('\x1b[36m' + `Ready! Logged in as ${client.user?.tag}` + "\x1b[0m");
	},
  setRedis: function(redis: RedisClientType) {
    redis = redis;
  }
};