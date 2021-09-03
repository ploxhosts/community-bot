import discord from 'discord.js';
import fs from 'fs';
import dotenv from 'dotenv';

dotenv.config();

const client: any = new discord.Client({ intents: [discord.Intents.FLAGS.GUILDS] });

(<any>client).commands = new discord.Collection();

const commandFiles = fs.readdirSync(__dirname + '/commands').filter(file => file.endsWith('.js'));

for (const file of commandFiles) {
	const command = require(`./commands/${file}`);
	// Set a new item in the Collection
	// With the key as the command name and the value as the exported module
	(<any>client).commands.set(command.data.name, command);
}

client.on('ready', () => {
 	console.log(`Logged in as ${client.user?.username}!`);
});


client.on('interactionCreate', async (interaction: any)=> {
	const command = (<any>client).commands.get(interaction.commandName);
	if (!command) return;

	try {
		await command.execute(interaction);
	} catch (error) {
		console.error(error);
		await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
	}
});

client.login(process.env.token);