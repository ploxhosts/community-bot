import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
const safeEval = require('safe-eval');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('maths')
        .setDescription('Does maths for you, easier to do it your head.')
        .addStringOption((option) =>
            option
                .setName('expression')
                .setDescription('Type in the maths you want to execute.')
                .setRequired(true)
        ),
    async execute(interaction: any) {
        const dangerousKeywords = [
            'eval',
            'exec',
            'system',
            'shell',
            'token',
            'env',
            'process',
            'throw',
        ];

        if (interaction.options.get('expression').value.length > 500) {
            await interaction.reply('I can\'t do that, too long.');

            return;
        }

        if (
            dangerousKeywords.some((word: string) =>
                interaction.options.get('expression').value.includes(word)
            )
        ) {
            await interaction.reply('I am sorry I cannot do that!');

            return;
        }

        const Embed = new discord.MessageEmbed()
            .setTitle('Calculate maths command')
            .setColor(process.env.themeColor as discord.ColorResolvable)
            .setDescription(
                `:abacus:  \`${
                    interaction.options.get('expression').value
                } = ${safeEval(interaction.options.get('expression').value)}\``
            )
            .setFooter(
                `${process.env.brandName} - Commands`,
                interaction.client.user?.displayAvatarURL()
            );

        await interaction.reply({ embeds: [Embed] });
    },
};
