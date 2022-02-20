import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import crypto from 'node:crypto';

module.exports = {
    data: new SlashCommandBuilder()
        .setName('love')
        .setDescription('Check the love rating between 2 users.')
        .addUserOption((option) =>
            option
                .setName('user1')
                .setDescription('One of the users you want to compare')
                .setRequired(true)
        )
        .addUserOption((option) =>
            option
                .setName('user2')
                .setDescription('One of the users you want to compare')
                .setRequired(true)
        ),

    async execute(interaction: any) {
        const choice = crypto.randomInt(1, 100);
        const user1: discord.User = interaction.options.getUser('user1');
        const user2: discord.User = interaction.options.getUser('user2');

        // TODO: use user's chat history to check if they are friends or like the same things
        const Embed = new discord.MessageEmbed({
            title: 'Love calculator',
            color: process.env.themeColor as discord.ColorResolvable,
            description: 
            `:heart:  <@${user1.id}> and <@${user2.id}> have a ${choice}% chance of love!`,
            footer: {
                text: `${process.env.brandName} - Commands`,
                iconURL: interaction.client.user?.displayAvatarURL(),
            },
        })

        await interaction.reply({ embeds: [Embed] });
    },
};
