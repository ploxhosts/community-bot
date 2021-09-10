import discord from 'discord.js';
import checkForBadWords from './utils/checkForBadWords'

module.exports = {
	name: 'messageCreate',
	dbRequired: true,
	async execute(message: discord.Message) {
		console.log("Message sent");
		await checkForBadWords(message);
	},
};