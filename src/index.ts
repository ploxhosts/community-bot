import { shimLog } from '@lvksh/logger';
import discord from 'discord.js';
import fs from 'node:fs';
import * as redis from 'redis';
import env from './env';
import log from './utils/log';

const RedisClient = redis.createClient();

RedisClient.connect();

RedisClient.on('connect', () => {
    console.log('redis connected');
    console.log(`connected ${RedisClient}`);
}).on('error', (error) => {
    console.log(error);
});

shimLog(log, 'debug');

connection.connect();

// Stop the bot from running if there is not a valid token
if (!process.env.token) {
    log.error(
        'Please specify a token to connect to the Discord API!\n Please create a bot from https://discord.com/developers/applications and copy the token, make sure there are no spaces within the .env'
    );
    throw new Error('No token specified!');
}

// Fill the environment variables if non existant

if (env.brandName === undefined || env.brandName === '') {
    process.env.brandName = 'Ploxy Community Bot';
    env.brandName = 'Ploxy Community Bot';
}

if (env.themeColor === undefined || env.themeColor === '') {
    process.env.themeColor = '#39b5af';
    env.themeColor = '#39b5af';
}

const client: any = new discord.Client({
    intents: [new discord.Intents('32767')],
}); // Get the value from https://ziad87.net/intents/

// TODO: Update <any> to proper type for discord.Client
(<any>client).commands = new discord.Collection();

// Load files

const commandFiles = fs.readdirSync(__dirname + '/commands');

const eventFiles = fs.readdirSync(__dirname + '/events');
const serviceFiles = fs.readdirSync(__dirname + '/db/services');

// Loop through services files to set redis connection
for (const file of serviceFiles) {
    const service = require(`./db/services/${file}`);

    service.setRedis(RedisClient);
}

// Event handler, no reason for anyone to touch this
for (const file of eventFiles) {
    const event = require(`./events/${file}`);

    event.setRedis(RedisClient);

    if (event.once) {
        client.once(event.name, (...arguments_: any) =>
            event.execute(...arguments_)
        );
    } else {
        client.on(event.name, (...arguments_: any) =>
            event.execute(...arguments_)
        );
    }
}

// Command handler do not touch other than modifiying checks such as adding to a database in here

for (const file of commandFiles) {
    const command = require(`./commands/${file}`);

    // Set a new item in the Collection
    // With the key as the command name and the value as the exported module
    (<any>client).commands.set(command.data.name, command);
}

// Command Handler
client.on(
    'interactionCreate',
    async (interaction: discord.BaseCommandInteraction) => {
        // Get the command from the Collection
        const command = (<any>client).commands.get(interaction.commandName);

        // If it doesn't exist then return
        if (!command) return;

        // If the command is disabled then return
        if (command.data.disabled) return;

        // Log the usage
        log.debug(
            `${interaction.user.tag} in #${
                (interaction as any).channel?.name
            } triggered an interaction.`
        );

        try {
            // Run code here to execute the command
            try {
                await command.execute(interaction);
            } catch (error) {
                console.log(error);
                interaction.reply(
                    'Something went wrong, please try again later.'
                );
            }
        } catch (error: any) {
            log.error(error);
            await interaction.reply({
                content: 'There was an error while executing this command!',
                ephemeral: true,
            });
        }
    }
);

client.login(env.token);