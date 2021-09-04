import { SlashCommandBuilder } from '@discordjs/builders';
import discord from 'discord.js';
import crypto from 'crypto';

module.exports = {
	data: new SlashCommandBuilder()
		.setName('rps')
		.setDescription('Play rock paper scissors with the bot')
			.addStringOption(option =>
				option.setName('choice')
					.setDescription('One of the users you want to compare')
					.setRequired(true)
				.addChoice('Rock', 'rock')
				.addChoice('Paper', 'paper')
				.addChoice('Scissors', 'scissors')),

	async execute(interaction: any) {
		let choice = crypto.randomInt(1, 100);
		let userChoice = interaction.options.getString('choice');
		let botChoice = '';
		if (choice <= 33) {
			botChoice = ':rock: rock';
		} else if (choice <= 66) {
			botChoice = ':roll_of_paper: paper';
		} else {
			botChoice = ':scissors: scissors';
		}
		if (userChoice == "rock"){
			userChoice = ':rock: rock';
		} else if (userChoice == "paper"){
			userChoice = ':roll_of_paper: paper';
		} else if (userChoice == "scissors"){
			userChoice = ':scissors: scissors';
		}
		let result = '';
		if (userChoice === botChoice) {
			result = ':hand_splayed: It\'s a tie!';
		} else if (userChoice === ':rock: rock' && botChoice === ':scissors: scissors') {
			result = 'You win!';
		} else if (userChoice === ':roll_of_paper: paper' && botChoice === ':rock: rock') {
			result = 'You win!';
		} else if (userChoice === ':scissors:  scissors' && botChoice === ':roll_of_paper: paper') {
			result = 'You win!';
		} else {
			result = 'You lose!';
		}
		const Embed = new discord.MessageEmbed()
			.setTitle('Rock Paper Scissors')
			.setColor(process.env.themeColor as discord.ColorResolvable)
			.setDescription(`You chose ${userChoice}, I chose ${botChoice}.\n**${result}**`)
			.setFooter(`${process.env.brandName} - Commands`, interaction.client.user?.displayAvatarURL())
		await interaction.reply({ embeds: [Embed] });
	},
};