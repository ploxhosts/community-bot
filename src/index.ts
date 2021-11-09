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

	if (connection) { // if the connection could be established
		// check if every table exists, if not create them
		fs.readdir(__dirname + '/db/tables', function (err, files) {
			//handling error
			if (err) {
				return console.log("\x1b[31m"+ 'Unable to scan directory in attempt to load sql tables: ' + err + "\x1b[0m");
			} 
			//listing all files using forEach
			files.forEach(function (file) {
				fs.readFile(__dirname + '/db/tables/' + file, 'utf8', function (err, data) {
					if (err) {
						return console.log("\x1b[31m"+ 'Unable to read file: ' + err + "\x1b[0m");
					}
					connection.query(data, function (err, result) { // Run whatever is in the sql file
						if (err) {
							return console.log("\x1b[31m"+ 'Unable to run query: ' + err + "\x1b[0m");
						}
					});
				});
			});
			// TODO: Create a patches folder within the db folder and put all sql files to update the database in there. Sort of similar to 00-thefirstupdate.sql and 01-thesecondupdate.sql
			// TODO: Loop through patches
		});
		// Created tabels if not created
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


const client: any = new discord.Client({ intents: [new discord.Intents('32766')] }); // Get the value from https://ziad87.net/intents/

// TODO: Update <any> to proper type for discord.Client
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
							connection.query("INSERT INTO ploxy_users (user_id, username, discriminator, user_avatar, premium, banned) VALUES (?, ?, ?, ?, false, 0)", [String(interaction.user.id), interaction.user.username, String(interaction.user.discriminator), String(interaction.user.avatar)], function(err, rows) {
								if (err) {
									console.log("Error querying database: " + err);
								}  else {
									console.log("\x1b[32m"+ "Inserted user into database!" + "\x1b[0m");
								}
							});
						}
					}
				});
				
				connection.query("SELECT * FROM `ploxy_automod` WHERE `guild_id` = " + String(interaction.guild?.id), function(err, rows) {
					if (err) {
						console.log("Error querying database: " + err);
					}  else {
						if (rows.length === 0) {
							connection.query(
								"INSERT INTO ploxy_automod (guild_id, bad_word_check, user_date_check, minimum_user_age, preset_badwords, message_spam_check, on_fail_bad_word, on_fail_spam_check, auto_ban_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
								, [String(interaction.guild?.id), 0, 0, 0, 1, 1, 1, 1, 0], function(err, rows) {
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

	// Log the usage
	console.log(`${interaction.user.tag} in #${(interaction as any).channel?.name} triggered an interaction.`);

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