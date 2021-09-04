import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import crypto from 'crypto';

module.exports = {
	data: new SlashCommandBuilder()
		.setName('flip')
		.setDescription('Gives you the ability to flip a coin giving Heads or Tails.'),
	async execute(interaction: any) {
		const Embed = new discord.MessageEmbed().setTitle('Coin Flip')
		.setColor(process.env.themeColor as discord.ColorResolvable)
		.setFooter(`${process.env.brandName} - Commands`, interaction.client.user?.displayAvatarURL());
		crypto.randomInt(1, 2) === 1 ? Embed.setDescription(`:coin: The coin shows Heads`) : Embed.setDescription(`:coin: The coin shows Tails`);
		await interaction.reply({ embeds: [Embed] });
	},
};