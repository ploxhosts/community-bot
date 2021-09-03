import discord from 'discord.js';
import dotenv from 'dotenv';

dotenv.config();

const client = new discord.Client({ intents: [discord.Intents.FLAGS.GUILDS] });

client.on('ready', () => {
 	console.log(`Logged in as ${client.user?.username}!`);
});


client.on('interactionCreate', async interaction => {
	if (!interaction.isCommand()) return;

	if (interaction.commandName === 'ping') {
		await interaction.reply('Pong!');
	}
});

client.login(process.env.token);