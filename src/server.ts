import discord from 'discord.js';
import fs from 'fs';
import dotenv from 'dotenv';

// Load environment variables from .env file
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

		console.log("\x1b[31m"+ "Failed to connect to database!" + "\x1b[0m" + "\nPlease make sure the database is running and the credentials are correct");
		process.env.DB_MODE = "false";
	}
	if (connection) {

		connection.query("SELECT * FROM `ploxy_users`", function(err, rows) {
			if (err) {
				console.log("Error querying database: " + err);
				process.env.DB_MODE = "false";
				console.log("\x1b[31m"+ "Failed to connect to database!" + "\x1b[0m");
			}  else {
				console.log("\x1b[32m"+ "Connected to database!" + "\x1b[0m");
				process.env.DB_MODE = "true";
			}
		});
		
		connection.release();
	}
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

client.on('interactionCreate', async (interaction: discord.BaseCommandInteraction) => {
	// Get the command from the Collection 
	const command = (<any>client).commands.get(interaction.commandName);

	// If it doesn't exist then return
	if (!command) return;

	// If the command is disabled then return
	if (command.data.disabled) return;

	// insert data to database if not exists
	if (process.env.DB_MODE === "true") {
		connection.getConnection(function(err, connection) {
			if (err) {
				console.log("Error connecting to database: " + err);
				console.log("\x1b[31m"+ "Failed to connect to database!" + "\x1b[0m");
			}
			if (connection) {
				connection.query("SELECT * FROM `ploxy_users` WHERE `user_id` = " + String(interaction.user.id), function(err, rows) {
					if (err) {
						console.log("Error querying database: " + err);
					}  else {
						if (rows.length === 0) {
							connection.query("INSERT INTO ploxy_users (user_id, username, discriminator, user_avatar, premium, banned) VALUES (?, ?, ?, ?, false, ?)", [String(interaction.user.id), interaction.user.username, String(interaction.user.discriminator), String(interaction.user.avatar), 0], function(err, rows) {
								if (err) {
									console.log("Error querying database: " + err);
								}  else {
									console.log("\x1b[32m"+ "Inserted user into database!" + "\x1b[0m");
								}
							});
						}
					}
				});
				connection.release();
			}
		});
	}
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