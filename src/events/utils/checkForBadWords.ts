import discord from 'discord.js';
import connection from '../../db/mysql';

module.exports = {
	check(message: discord.Message) {
		let badWords: string[] = [];
		if (!message.guild) {
			return false;
		}
		if (process.env.DB_MODE === "true") {
			connection.getConnection(function(err, connection) {
				if (err) {
					console.log("Error connecting to database: " + err);
					console.log("\x1b[31m"+ "Failed to connect to database!" + "\x1b[0m");
					
					return null;
				}
				if (connection) {
					connection.query("SELECT * FROM ploxy_bad_words WHERE guild_id = ?", String(message.guild?.id), function(err, rows) {
						if (err) {
							console.log("Error querying database: " + err);
							console.log("\x1b[31m"+ "Failed to query database!" + "\x1b[0m");
						}
						if (rows) {
							for (let i = 0; i < rows.length; i++) {
								badWords.push(rows[i].word);
							}
						}
						connection.release();
					});
				}
			});
		}
		if (badWords.length > 0) {
			for (let i = 0; i < badWords.length; i++) {
				if (message.content.toLowerCase().includes(badWords[i])) {
					message.delete();
					message.channel.send(`${message.author} you are not allowed to use that word!`);
					return true;
				}
			}
		}
		return false;

	},
};