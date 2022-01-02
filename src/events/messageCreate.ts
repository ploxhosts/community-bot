import discord from 'discord.js';
import { badWordCheck } from '../utils/badWordCheck';

module.exports = {
	name: 'messageCreate',
	async execute(message: discord.Message) {
		console.log("Message sent");
		await badWordCheck(message.content, true);
	},
};