import discord from 'discord.js';

function createGuildEmbed() {
  const embed = new discord.MessageEmbed()
    .setColor('#0099ff')
    .setTitle('**Thanks for inviting Ploxy**')
    .setDescription(
      "Ploxy is a multi purpose bot - it can do a lot of things, it's main purpose is to help out in the (official PloxHost discord)[https://plox.host/discord].\n\n" 
      +"The main bot is open source on (GitHub)[https://github.com/ploxhosts/community-bot], however most support modules are not. *These can be manually enabled in the dashboard.*\n\n"
      + "**Ploxy is currently in beta, so please report any bugs or issues you find.**"
      + "To get started use the `/setup` command, or use `/help` if you need any support with it. Feel free to come into the official discord and ask questions.")
    .setTimestamp()
    .setFooter('Ploxy', 'https://cdn.discordapp.com/icons/346715007469355009/a_a62d793864db69bd10223479af4838a2.webp');
  return embed;
}

export default createGuildEmbed;