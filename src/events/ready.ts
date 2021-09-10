import discord from 'discord.js';

module.exports = {
	name: 'ready',
	dbRequired: false,
	once: true,
	execute(client: discord.Client) {
		console.log('\x1b[36m' + `Ready! Logged in as ${client.user?.tag}` + "\x1b[0m");
	},
};