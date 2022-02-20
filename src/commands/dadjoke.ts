import { SlashCommandBuilder } from '@discordjs/builders';
import axios from 'axios';
import discord from 'discord.js';
import crypto from 'node:crypto';

module.exports = {
    data: new SlashCommandBuilder()
        .setName('dadjoke')
        .setDescription('Get a random dad joke.'),

    async execute(interaction: any) {
        const dadJoke = await axios.get('https://icanhazdadjoke.com/', {
            headers: {
                Accept: 'application/json',
                'User-Agent':
                    'Ploxy (https://github.com/PloxHost-LLC/community-bot)',
            },
        });

        const Embed = new discord.MessageEmbed(
            {
                title: ':man_red_haired: Dad Joke',
                description: `${dadJoke.data.joke}`,
                color:process.env.themeColor as discord.ColorResolvable,
                footer: {
                    text: `${process.env.brandName} - Commands`,
                    iconURL: interaction.client.user?.displayAvatarURL(),
                }
            }
        )

        await interaction.reply({ embeds: [Embed] });
    },
};
