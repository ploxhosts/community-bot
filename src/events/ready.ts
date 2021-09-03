import discord from 'discord.js';

module.exports = {
	name: 'ready',
	once: true,
	execute(client: discord.Client) {
		console.log(`Ready! Logged in as ${client.user?.tag}`);
	},
};