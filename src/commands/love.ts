import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import crypto from 'crypto';

module.exports = {
	data: new SlashCommandBuilder()
		.setName('love')
		.setDescription('Check the love rating between 2 users.')
			.addUserOption(option =>
				option.setName('user1')
					.setDescription('One of the users you want to compare')
					.setRequired(true))
			.addUserOption(option =>
				option.setName('user2')
					.setDescription('One of the users you want to compare')
					.setRequired(true)),

	async execute(interaction: any) {
		let choice = crypto.randomInt(1, 100);
		const user1: discord.User = interaction.options.getUser('user1');
		const user2: discord.User  = interaction.options.getUser('user2');
		const Embed = new discord.MessageEmbed()
			.setTitle('Love calculator')
			.setColor(process.env.themeColor as discord.ColorResolvable)
			.setDescription(`:heart:  <@${user1.id}> and <@${user2.id}> have a ${choice}% chance of love!`)
			.setFooter(`${process.env.brandName} - Commands`, interaction.client.user?.displayAvatarURL())
		await interaction.reply({ embeds: [Embed] });
	},
};