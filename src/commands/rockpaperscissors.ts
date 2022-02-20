import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import crypto from 'node:crypto';

module.exports = {
    data: new SlashCommandBuilder()
        .setName('rps')
        .setDescription('Play rock paper scissors with the bot')
        .addStringOption((option) =>
            option
                .setName('choice')
                .setDescription('Your choice to play rock paper scissors')
                .setRequired(true)
                .addChoice('Rock', 'rock')
                .addChoice('Paper', 'paper')
                .addChoice('Scissors', 'scissors')
        ),

    async execute(interaction: any) {
        const choice = crypto.randomInt(1, 100);
        let userChoice = interaction.options.getString('choice');
        let botChoice = '';

        if (choice <= 33) {
            botChoice = ':rock: rock';
        } else if (choice <= 66) {
            botChoice = ':roll_of_paper: paper';
        } else {
            botChoice = ':scissors: scissors';
        }

        if (userChoice == 'rock') {
            userChoice = ':rock: rock';
        } else if (userChoice == 'paper') {
            userChoice = ':roll_of_paper: paper';
        } else if (userChoice == 'scissors') {
            userChoice = ':scissors: scissors';
        }

        let result = '';

        if (userChoice === botChoice) {
            result = ':hand_splayed: It\'s a tie!';
        } else if (
            userChoice === ':rock: rock' &&
            botChoice === ':scissors: scissors'
        ) {
            result = 'You win!';
        } else if (
            userChoice === ':roll_of_paper: paper' &&
            botChoice === ':rock: rock'
        ) {
            result = 'You win!';
        } else if (
            userChoice === ':scissors:  scissors' &&
            botChoice === ':roll_of_paper: paper'
        ) {
            result = 'You win!';
        } else {
            result = 'You lose!';
        }

        const Embed = new discord.MessageEmbed({
            title: 'Rock Paper Scissors',
            color: process.env.themeColor as discord.ColorResolvable,
            description: `You chose ${userChoice}, I chose ${botChoice}.\n**${result}**`,
            footer: {
                text: `${process.env.brandName} - Commands`,
                iconURL: interaction.client.user?.displayAvatarURL(),
            },
        })

        await interaction.reply({ embeds: [Embed] });
    },
};
