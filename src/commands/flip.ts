import { SlashCommandBuilder } from '@discordjs/builders';
import crypto from 'crypto';

module.exports = {
	data: new SlashCommandBuilder()
		.setName('flip')
		.setDescription('Gives you the ability to flip a coin giving Heads or Tails.'),
	async execute(interaction: any) {
		crypto.randomInt(1, 2) === 1 ? interaction.reply('Heads') : interaction.reply('Tails');
	},
};