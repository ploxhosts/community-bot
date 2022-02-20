import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import crypto from 'node:crypto';

module.exports = {
    data: new SlashCommandBuilder()
        .setName('flip')
        .setDescription(
            'Gives you the ability to flip a coin giving Heads or Tails.'
        ),
    async execute(interaction: any) {
        const random = crypto.randomInt(1, 2);
        const Embed = new discord.MessageEmbed(
            {
                title: 'Coin Flip',
                description: random === 1
                ? ':coin: The coin shows Heads'
                : ':coin: The coin shows Tails',
                color: process.env.themeColor as discord.ColorResolvable,
                footer: {
                    text: `${process.env.brandName} - Commands`,
                    iconURL: interaction.client.user?.displayAvatarURL(),
                },

            }
        )
        await interaction.reply({ embeds: [Embed] });
    },
};
