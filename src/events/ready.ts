import discord from 'discord.js';
import { RedisClientType } from 'redis';

import { updateTables } from '../db/postgres';

let redis: RedisClientType;

module.exports = {
    name: 'ready',
    once: true,
    async execute(client: discord.Client) {
        console.log(
            '\u001B[36m' +
                `Ready! Logged in as ${client.user?.tag}` +
                '\u001B[0m'
        );
        console.log('Starting to update tables');
        await updateTables();
    },
    setRedis: function (NewRedis: RedisClientType) {
        redis = NewRedis;
    },
};
