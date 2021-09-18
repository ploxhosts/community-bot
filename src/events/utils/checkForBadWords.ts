import discord from 'discord.js';
import connection from '../../db/mysql';


async function check(message: discord.Message) {
	let badWords: string[] = [];
	let userBadWords: string[] = [];
	let preset_badwords = 1; // 0 = custom, 1 = regular bad words, 3 = regular bad words with custom bad words
	let bad_word_check	= true; // Default's to true without a database
	let on_fail_bad_word = 1; // 0 = do nothing, 1 = delete message, 2 = mute user, 3 = kick user, 4 = ban user
	let on_fail_bad_word_reason = "";
	let on_fail_bad_word_duration = 0; // increments based on how many bad words detected
	if (!message.guild) {
		return false;
	}
	if (process.env.DB_MODE === "true") {
		await connection.getConnection(async function(err, connection) {
			if (err) {
				console.log("Error connecting to database: " + err);
				console.log("\x1b[31m"+ "Failed to connect to database!" + "\x1b[0m");
					
				return null;
			}
			if (connection) {
				await connection.query("SELECT * FROM ploxy_automod WHERE guild_id = ?", String(message.guild?.id), function(err, row) {
					if (err) {
						console.log("Error querying database: " + err);
						console.log("\x1b[31m"+ "Failed to query database!" + "\x1b[0m");
					}
					if (row.length === 1) {
						bad_word_check = Boolean(row[0].bad_word_check);
						on_fail_bad_word = Number(row[0].on_fail_bad_word);
						preset_badwords = Number(row[0].preset_badwords);
					}

				});

				await connection.query("SELECT * FROM ploxy_badwords WHERE guild_id = ?", String(message.guild?.id), function(err, rows) {
					if (err) {
						console.log("Error querying database: " + err);
						console.log("\x1b[31m"+ "Failed to query database!" + "\x1b[0m");
					}
					if (rows) {
						for (let i = 0; i < rows.length; i++) {
							userBadWords.push(rows[i].word);
						}
					}
				});
				
				connection.release();
			}
		});
	}
	if (preset_badwords === 1 || 3) {
		// Credit for bad words from: https://github.com/RobertJGabriel/Google-profanity-words
		// Had the choice of making an api for this and checking but found out most people who want to break the rules won't adventure into code as they are either
		// an art student or a child.
		badWords = ['4r5e', '5h1t', '5hit', 'a55', 'anal', 'anus', 'ar5e', 'arrse', 'arse', 'ass', 'ass-fucker', 
					'asses', 'assfucker', 'assfukka', 'asshole', 'assholes', 'asswhole', 'a_s_s', 'b!tch', 'b00bs', 
					'b17ch', 'b1tch', 'ballbag', 'balls', 'ballsack', 'bastard', 'beastial', 'beastiality', 'bellend', 
					'bestial', 'bestiality', 'bi+ch', 'biatch', 'bitch', 'bitcher', 'bitchers', 'bitches', 'bitchin', 
					'bitching', 'bloody', 'blow job', 'blowjob', 'blowjobs', 'boiolas', 'bollock', 'bollok', 'boner', 
					'boob', 'boobs', 'booobs', 'boooobs', 'booooobs', 'booooooobs', 'breasts', 'buceta', 'bugger', 'bum', 
					'bunny fucker', 'butt', 'butthole', 'buttmunch', 'buttplug', 'c0ck', 'c0cksucker', 'carpet muncher', 
					'cawk', 'chink', 'cipa', 'cl1t', 'clit', 'clitoris', 'clits', 'cnut', 'cock', 'cock-sucker', 'cockface', 
					'cockhead', 'cockmunch', 'cockmuncher', 'cocks', 'cocksuck ', 'cocksucked ', 'cocksucker', 'cocksucking', 
					'cocksucks ', 'cocksuka', 'cocksukka', 'cok', 'cokmuncher', 'coksucka', 'coon', 'cox', 'crap', 'cum', 
					'cummer', 'cumming', 'cums', 'cumshot', 'cunilingus', 'cunillingus', 'cunnilingus', 'cunt', 'cuntlick ', 
					'cuntlicker ', 'cuntlicking ', 'cunts', 'cyalis', 'cyberfuc', 'cyberfuck ', 'cyberfucked ', 'cyberfucker', 
					'cyberfuckers', 'cyberfucking ', 'd1ck', 'damn', 'dick', 'dickhead', 'dildo', 'dildos', 'dink', 'dinks', 'dirsa', 
					'dlck', 'dog-fucker', 'doggin', 'dogging', 'donkeyribber', 'doosh', 'duche', 'dyke', 'ejaculate', 'ejaculated', 
					'ejaculates ', 'ejaculating ', 'ejaculatings', 'ejaculation', 'ejakulate', 'fuck', 'fucker', 'f4nny', 'fag', 
					'fagging', 'faggitt', 'faggot', 'faggs', 'fagot', 'fagots', 'fags', 'fanny', 'fannyflaps', 'fannyfucker', 'fanyy', 
					'fatass', 'fcuk', 'fcuker', 'fcuking', 'feck', 'fecker', 'felching', 'fellate', 'fellatio', 'fingerfuck ', 
					'fingerfucked ', 'fingerfucker ', 'fingerfuckers', 'fingerfucking ', 'fingerfucks ', 'fistfuck', 'fistfucked ', 
					'fistfucker ', 'fistfuckers ', 'fistfucking ', 'fistfuckings ', 'fistfucks ', 'flange', 'fook', 'fooker', 'fuck', 
					'fucka', 'fucked', 'fucker', 'fuckers', 'fuckhead', 'fuckheads', 'fuckin', 'fucking', 'fuckings', 'fuckingshitmotherfucker', 
					'fuckme ', 'fucks', 'fuckwhit', 'fuckwit', 'fudge packer', 'fudgepacker', 'fuk', 'fuker', 'fukker', 'fukkin', 'fuks', 'fukwhit', 
					'fukwit', 'fux', 'fux0r', 'f_u_c_k', 'gangbang', 'gangbanged ', 'gangbangs ', 'gaylord', 'gaysex', 'goatse', 'God', 'god-dam', 
					'god-damned', 'goddamn', 'goddamned', 'hardcoresex ', 'hell', 'heshe', 'hoar', 'hoare', 'hoer', 'homo', 'hore', 'horniest', 
					'horny', 'hotsex', 'jack-off ', 'jackoff', 'jap', 'jerk-off ', 'jism', 'jiz ', 'jizm ', 'jizz', 'kawk', 'knob', 'knobead', 
					'knobed', 'knobend', 'knobhead', 'knobjocky', 'knobjokey', 'kock', 'kondum', 'kondums', 'kum', 'kummer', 'kumming', 'kums', 
					'kunilingus', 'l3i+ch', 'l3itch', 'labia', 'lmfao', 'lust', 'lusting', 'm0f0', 'm0fo', 'm45terbate', 'ma5terb8', 'ma5terbate', 
					'masochist', 'master-bate', 'masterb8', 'masterbat*', 'masterbat3', 'masterbate', 'masterbation', 'masterbations', 'masturbate', 
					'mo-fo', 'mof0', 'mofo', 'mothafuck', 'mothafucka', 'mothafuckas', 'mothafuckaz', 'mothafucked ', 'mothafucker', 'mothafuckers', 
					'mothafuckin', 'mothafucking ', 'mothafuckings', 'mothafucks', 'mother fucker', 'motherfuck', 'motherfucked', 'motherfucker', 
					'motherfuckers', 'motherfuckin', 'motherfucking', 'motherfuckings', 'motherfuckka', 'motherfucks', 'muff', 'mutha', 'muthafecker', 
					'muthafuckker', 'muther', 'mutherfucker', 'n1gga', 'n1gger', 'nazi', 'nigg3r', 'nigg4h', 'nigga', 'niggah', 'niggas', 'niggaz', 
					'nigger', 'niggers ', 'nob', 'nob jokey', 'nobhead', 'nobjocky', 'nobjokey', 'numbnuts', 'nutsack', 'orgasim ', 'orgasims ', 
					'orgasm', 'orgasms ', 'p0rn', 'pawn', 'pecker', 'penis', 'penisfucker', 'phonesex', 'phuck', 'phuk', 'phuked', 'phuking', 
					'phukked', 'phukking', 'phuks', 'phuq', 'pigfucker', 'pimpis', 'piss', 'pissed', 'pisser', 'pissers', 'pisses ', 'pissflaps', 
					'pissin ', 'pissing', 'pissoff ', 'poop', 'porn', 'porno', 'pornography', 'pornos', 'prick', 'pricks ', 'pron', 'pube', 'pusse', 
					'pussi', 'pussies', 'pussy', 'pussys ', 'rectum', 'retard', 'rimjaw', 'rimming', 's hit', 's.o.b.', 'sadist', 'schlong', 'screwing', 
					'scroat', 'scrote', 'scrotum', 'semen', 'sex', 'sh!+', 'sh!t', 'sh1t', 'shag', 'shagger', 'shaggin', 'shagging', 'shemale', 'shi+', 
					'shit', 'shitdick', 'shite', 'shited', 'shitey', 'shitfuck', 'shitfull', 'shithead', 'shiting', 'shitings', 'shits', 'shitted', 'shitter', 
					'shitters ', 'shitting', 'shittings', 'shitty ', 'skank', 'slut', 'sluts', 'smegma', 'smut', 'snatch', 'son-of-a-bitch', 'spac', 'spunk',
					's_h_i_t', 't1tt1e5', 't1tties', 'teets', 'teez', 'testical', 'testicle', 'tit', 'titfuck', 'tits', 'titt', 'tittie5', 'tittiefucker',
					'titties', 'tittyfuck', 'tittywank', 'titwank', 'tosser', 'turd', 'tw4t', 'twat', 'twathead', 'twatty', 'twunt', 'twunter', 'v14gra',
					'v1gra', 'vagina', 'viagra', 'vulva', 'w00se', 'wang', 'wank', 'wanker', 'wanky', 'whoar', 'whore', 'willies', 'willy', 'xrated', 'xxx'
				]
	}
	if (preset_badwords === 3) {
		for (var i = 0; i < userBadWords.length; i ++){
			badWords.push(userBadWords[i])
		}
	}

	let contains_bad_word = false;
	let badWordNum = 0;

	if (bad_word_check) {
		let badWordsCheck = new RegExp(badWords.join('|'), 'gi');

		const countOccurrencesInRegex = (str: String) => {
			return ((str || '').match(badWordsCheck) || []).length
		}

		if (badWordsCheck.test(message.content)) {
			contains_bad_word = true;
			badWordNum = countOccurrencesInRegex(message.content);
		}
	}

	if (contains_bad_word === true) {
		if (on_fail_bad_word === 1) {
			message.delete().catch(console.error);
			message.channel.send('**' + message.author.username + '**, your message has been removed for containing a bad word.');
		}
		if (on_fail_bad_word === 2) {
			message.author.send("You have been muted for bad words.").catch(console.error);
			// TODO: Process muting with another utility function
		}
		if (on_fail_bad_word === 3) {
			message.author.send("You have been kicked for bad words.").catch(console.error);
			(message.author as any).kick().then((member: discord.GuildMember) => {
				message.channel.send(":wave: " + member.displayName + " has been kicked due to saying a bad word!");
			}).catch(() => {
				// Something went wrong
				console.log("Something went wrong when trying to kick a user for bad words! Please make sure I am above the user's role, have kick perms");
			});
		}
		if (on_fail_bad_word === 4) {
			message.author.send("You have been banned for bad words.").catch(console.error);
			(message.author as any).ban().then((member: discord.GuildMember) => {
				message.channel.send(":wave: " + member.displayName + " has been banned due to saying a bad word!");
			}).catch(() => {
				// Something went wrong
				console.log("Something went wrong when trying to ban a user for bad words! Please make sure I am above the user's role, have kick and ban perms");
			});
		}
		return true;
	}
	return false;
}

export default check;