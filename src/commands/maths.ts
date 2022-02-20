import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import math from 'mathjs';

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
        const limitedEvaluate = math.evaluate

        math.import({
          import: function () { throw new Error('Function import is disabled') },
          createUnit: function () { throw new Error('Function createUnit is disabled') },
          evaluate: function () { throw new Error('Function evaluate is disabled') },
          parse: function () { throw new Error('Function parse is disabled') },
          simplify: function () { throw new Error('Function simplify is disabled') },
          derivative: function () { throw new Error('Function derivative is disabled') }
        }, { override: true })
        
        
        const Embed = new discord.MessageEmbed({
            title: 'Maths',
            description: `:abacus:  \`${
                expression
            } = ${limitedEvaluate(expression)}\``,
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

