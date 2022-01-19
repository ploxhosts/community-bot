import discord from 'discord.js';
import { RedisClientType } from 'redis';
import { updateTables } from '../db/postgres';

let redis: RedisClientType;

module.exports = {
	name: 'ready',
	once: true,
	async execute(client: discord.Client) {
		console.log('\x1b[36m' + `Ready! Logged in as ${client.user?.tag}` + "\x1b[0m");
    console.log("Starting to update tables")
    await updateTables();
	},
  setRedis: function(redis: RedisClientType) {
    redis = redis;
  }
};