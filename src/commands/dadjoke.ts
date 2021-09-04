import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import axios from 'axios';
import crypto from 'crypto';

module.exports = {
	data: new SlashCommandBuilder()
		.setName('dadjoke')
		.setDescription('Get a random dad joke.'),

	async execute(interaction: any) {
		const dadJoke = await axios.get('https://icanhazdadjoke.com/', {
			headers: {
				Accept: 'application/json',
				'User-Agent': 'Ploxy (https://github.com/PloxHost-LLC/community-bot)',
			},
		});

		const Embed = new discord.MessageEmbed()
			.setTitle(':man_red_haired: Dad Joke')
			.setDescription(`${dadJoke.data.joke}`)
			.setColor(process.env.themeColor as discord.ColorResolvable)
			.setFooter(`${process.env.brandName} - Commands`, interaction.client.user?.displayAvatarURL())
		await interaction.reply({ embeds: [Embed] });
	},
};