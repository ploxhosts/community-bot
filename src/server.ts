import discord from 'discord.js';
import fs from 'fs';
import dotenv from 'dotenv';
dotenv.config();

import connection from './db/mysql';


// Stop the bot from running if there is not a valid token
if (!process.env.token) {
	console.log("Please specify a token to connect to the Discord API!\n Please create a bot from https://discord.com/developers/applications and copy the token, make sure there are no spaces within the .env");
	process.exit(1);
};

connection.getConnection(function(err, connection) {
	if (err) {
		console.log("Error connecting to database: " + err);
		console.log("Could not connect to the database!\n Please make sure the database is running and the credentials are correct");
		process.exit(1);
	}
	connection.query("SELECT * FROM `users`", function(err, rows) {
		if (err) {
			console.log("Error querying database: " + err);
			process.exit(1);
		} 
		console.log("Connected to database!");
	});
});

// Fill the environment variables if non existant

if (process.env.brandName === undefined || process.env.brandName === '') {
	process.env.brandName = 'Ploxy Community Bot';
} 

if (process.env.themeColor === undefined || process.env.themeColor === '') {
	process.env.themeColor = '#39b5af';
}

const client: any = new discord.Client({ intents: [discord.Intents.FLAGS.GUILDS] });

(<any>client).commands = new discord.Collection();

// Load files

const commandFiles = fs.readdirSync(__dirname + '/commands').filter(file => file.endsWith('.js'));
const eventFiles = fs.readdirSync(__dirname + '/events').filter(file => file.endsWith('.js'));


// Event handler, no reason for anyone to touch this
for (const file of eventFiles) {
	const event = require(`./events/${file}`);
	if (event.once) {
		client.once(event.name, (...args: any) => event.execute(...args));
	} else {
		client.on(event.name, (...args: any) => event.execute(...args));
	}
}

// Command handler do not touch other than modifiying checks such as adding to a database in here

for (const file of commandFiles) {
	const command = require(`./commands/${file}`);
	// Set a new item in the Collection
	// With the key as the command name and the value as the exported module
	(<any>client).commands.set(command.data.name, command);
}

client.on('interactionCreate', async (interaction: any)=> {
	// Get the command from the Collection 
	const command = (<any>client).commands.get(interaction.commandName);

	// If it doesn't exist then return
	if (!command) return;

	try {
		// Run code here to execute the command
		await command.execute(interaction);
	} catch (error) {
		console.error(error);
		await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
	}
});


// Login to the api
client.login(process.env.token);