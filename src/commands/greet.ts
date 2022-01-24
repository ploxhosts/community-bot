import { SlashCommandBuilder } from '@discordjs/builders';
import crypto from 'node:crypto';

module.exports = {
    data: new SlashCommandBuilder()
        .setName('greet')
        .setDescription('Greets someone with a positive message.'),
    async execute(interaction: any) {
        const choices = [
            'Hi!',
            'Great!',
            'Hello there!',
            'Welcome!',
            'Hello hello!',
        ];
        const choice = crypto.randomInt(1, choices.length);
        let message = '';

        message = choices[choice];
        interaction.reply(message);
    },
};
