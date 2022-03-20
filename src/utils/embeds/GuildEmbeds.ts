import discord from 'discord.js';

class GuildEmbeds {
    createGuildEmbed = () => {
        return new discord.MessageEmbed({
            title: '**Thanks for inviting Ploxy**',
            description: 
            "Ploxy is a multi purpose bot - it can do a lot of things, it's main purpose is to help out in the [official PloxHost discord](https://plox.host/discord).\n\n" +
                'The main bot is open source on [GitHub](https://github.com/ploxhosts/community-bot), however most support modules are not. *These can be manually enabled in the dashboard.*\n\n' +
                '**Ploxy is currently in beta, so please report any bugs or issues you find.**' +
                'To get started use the `/setup` command, or use `/help` if you need any support with it. Feel free to come into the official discord and ask questions.',
            color: process.env.themeColor as discord.ColorResolvable,
            footer: {
                text: `Ploxy`,
                iconURL: 'https://cdn.discordapp.com/icons/346715007469355009/a_a62d793864db69bd10223479af4838a2.webp',
            },
            timestamp: new Date(),

        })
    }

    createUnderageKickEmbed = (user: discord.User) => {
        return new discord.MessageEmbed({
            title: `${user.username}#${user.discriminator} || ${user.id}`,
            description: 'Didn\'t satisy the age requirement',
            color: process.env.themeColor as discord.ColorResolvable,
            footer: {
                text: `Ploxy`,
                iconURL: 'https://cdn.discordapp.com/icons/346715007469355009/a_a62d793864db69bd10223479af4838a2.webp',
            },
            timestamp: new Date(),
        })
    }

    MissingPermissionsEmbed = (permissions: string[]) => {
        return new discord.MessageEmbed({
            title: 'Missing permissions',
            description: `Missing permissions: ${permissions.join(', ')}`,
            color: process.env.themeColor as discord.ColorResolvable,
            footer: {
                text: `Ploxy`,
                iconURL: 'https://cdn.discordapp.com/icons/346715007469355009/a_a62d793864db69bd10223479af4838a2.webp',
            },
            timestamp: new Date(),
        })
    }


}

export default new GuildEmbeds();
