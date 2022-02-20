import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';

module.exports = {
    data: new SlashCommandBuilder()
        .setName('ping')
        .setDescription('Replies with Pong!'),
    async execute(interaction: discord.CommandInteraction) {
        const Embed = new discord.MessageEmbed(
            {
                title: ':ping_pong: Pong!',
                description: 
                `:hourglass: ${
                    Date.now() - interaction.createdTimestamp
                }ms\n\n:heartbeat: ${interaction.client.ws.ping} ms`,
                color: process.env.themeColor as discord.ColorResolvable,
                footer: {
                    text:  `${process.env.brandName} - Commands`,
                    iconURL: interaction.client.user?.displayAvatarURL(),
                }
            }
        )

        await interaction.reply({ embeds: [Embed] });
    },
};
