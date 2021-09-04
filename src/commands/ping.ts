import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';

module.exports = {
	data: new SlashCommandBuilder()
		.setName('ping')
		.setDescription('Replies with Pong!'),
	async execute(interaction: discord.CommandInteraction) {
		const Embed = new discord.MessageEmbed()
			.setColor(process.env.themeColor as discord.ColorResolvable)
			.setDescription(`:hourglass: ${new Date().getTime() - interaction.createdTimestamp}ms\n\n:heartbeat: ${interaction.client.ws.ping} ms`)
			.setFooter(`${process.env.brandName} - Commands`, interaction.client.user?.displayAvatarURL())
		await interaction.reply({ embeds: [Embed] });
	},
};