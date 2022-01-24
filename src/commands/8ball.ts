import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import crypto from 'node:crypto';

module.exports = {
    data: new SlashCommandBuilder()
        .setName('8ball')
        .setDescription(
            'Get help with important life decisions and answers for common questions'
        )
        .addStringOption((option) =>
            option
                .setName('question')
                .setDescription('A question you want to ask the 8ball')
                .setRequired(true)
        ),

    async execute(interaction: any) {
        const question = interaction.options.getString('question');
        const answers = [
            'It is certain',
            'It is decidedly so',
            'Without a doubt',
            'Yes definitely',
            'You may rely on it',
            'As I see it, yes',
            'Most likely',
            'Outlook good',
            'Yes',
            'Signs point to yes',
            'Reply hazy try again',
            'Ask again later',
            'Better not tell you now',
            'Cannot predict now',
            'Concentrate and ask again',
            'Don\'t count on it',
            'My reply is no',
            'Computer says no',
            'My sources say no',
            'Outlook not so good',
            'Very doubtful',
            'No',
        ];
        const answer = answers.at(Math.floor(Math.random() * answers.length));
        const Embed = new discord.MessageEmbed()
            .setTitle('8ball')
            .setDescription(`:question: ${question}\n:8ball: ${answer}`)
            .setColor(process.env.themeColor as discord.ColorResolvable)
            .setFooter(
                `${process.env.brandName} - Commands`,
                interaction.client.user?.displayAvatarURL()
            );

        await interaction.reply({ embeds: [Embed] });
    },
};
