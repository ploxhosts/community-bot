import { SlashCommandBuilder } from '@discordjs/builders';
import crypto from 'crypto';
const safeEval = require('safe-eval')

module.exports = {
	data: new SlashCommandBuilder()
		.setName('maths')
		.setDescription('Does maths for you, easier to do it your head.')
		.addStringOption(option =>
			option.setName('expression')
				.setDescription('Type in the maths you want to execute.')
				.setRequired(true)),
	async execute(interaction: any) {

		interaction.reply('Your answer is: `'+ safeEval(interaction.options.get('expression').value) + '`');
	},
};