const { SlashCommandBuilder } = require('@discordjs/builders');
const { REST } = require('@discordjs/rest');
const { Routes } = require('discord-api-types/v9');
const dotenv = require('dotenv');

dotenv.config();

const commands = [
	new SlashCommandBuilder().setName('ping').setDescription('Replies with pong!'),
].map(command => command.toJSON());

const rest = new REST({ version: '9' }).setToken(process.env.token);

(async () => {
	try {
		await rest.put(
			Routes.applicationGuildCommands(process.env.clientId, process.env.guildId),
			{ body: commands },
		);

		console.log('Successfully registered application commands.');
	}
	catch (error) {
		console.error(error);
	}
})();