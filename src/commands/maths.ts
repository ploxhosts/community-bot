import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import * as math from 'mathjs';

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

        const expression = interaction.options.get('expression').value;
        // calculate the expression without eval
        

        if (expression.length > 300) {
            await interaction.reply('I can\'t do that, it\'s too long.');

            return;
        }
        const limitedEvaluate = math.parser();

        let description;
        try {
            description = `:abacus:  \`${
                expression
            } = ${limitedEvaluate.evaluate(expression)}\``
        } catch (error: unknown) {
            if (typeof error === "string") {
                description = `:x:  \`${error}\``
            } else if (error instanceof Error) {
                description = `:x:  \`${error.message}\``
            }
        }
        
        const Embed = new discord.MessageEmbed({
            title: 'Maths',
            description,
            color: process.env.themeColor as discord.ColorResolvable,
            footer: {
                text: `${process.env.brandName} - Commands`,
                iconURL: 
                interaction.client.user?.displayAvatarURL()
            },
        });

        await interaction.reply({ embeds: [Embed] });
    },
};

