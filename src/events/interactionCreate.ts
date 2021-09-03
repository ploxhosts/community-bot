import discord from 'discord.js';

module.exports = {
	name: 'interactionCreate',
	execute(interaction: any) {
		console.log(`${interaction.user.tag} in #${interaction.channel.name} triggered an interaction.`);
	},
};