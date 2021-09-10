import discord from 'discord.js';

module.exports = {
	name: 'messageCreate',
	dbRequired: true,
	execute(message: discord.Message) {
		console.log("Message sent");
	},
};