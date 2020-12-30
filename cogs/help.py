from typing import Iterator

import discord
from discord.ext import commands
import datetime
import asyncio


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    def get_all_commands(self) -> Iterator[commands.Command]:
        """Yield all commands for all cogs in all extensions."""
        for module in self.bot.walk_modules():
            for cog in self.bot.walk_cogs(module):
                for cmd in self.bot.walk_commands(cog):
                    yield cmd

    @commands.command(name="help", description="Returns all commands available",
                      aliases=["command", "commands", "commandslist", "listcommands", "lscmds", "cmds", "lscommands"], usage="help")
    async def help(self, ctx, cog=None):
        db = self.database.bot
        posts = db.serversettings
        prefix = "?"
        for x in posts.find({"guild_id": ctx.guild.id}):
            prefix = x['prefix']

        embed = discord.Embed(colour=0xac6f8f, title="Help command")
        if cog is None:
            commands_list = {}
            cog_names = {""}
            for cmd in self.bot.walk_commands():
                if cmd.cog:
                    if isinstance(cmd, commands.Group):
                        commands_list[cmd.name] = {
                            "name": cmd.name,
                            "subcommands": cmd.commands,
                            "aliases": cmd.aliases,
                            "cog": cmd.cog.qualified_name,
                            "usage": cmd.usage,
                            "desc": cmd.description,
                        }
                    else:
                        commands_list[cmd.name] = {
                            "name": cmd.name,
                            "aliases": cmd.aliases,
                            "cog": cmd.cog.qualified_name,
                            "usage": cmd.usage,
                            "desc": cmd.description,
                        }
                    cog_names.add(cmd.cog.qualified_name)

            for c in cog_names:

                if c.lower() in ["", "help"]:  # Ignore these
                    pass
                else:
                    embed.add_field(name=c, value=self.bot.get_cog(c).description, inline=False)
            embed.add_field(name="To get more detailed information", value=f"{prefix}help <cog> for example: `{prefix}help Mod`", inline=False)
        else:
            print(cog)
            try:
                if self.bot.get_cog(cog.capitalize()):  # Check if it exists
                    pass

                embed = discord.Embed(colour=0xac6f8f, title=f"{cog.capitalize()} commands")


                if cog.lower() in ["customcommands", "customcommand", "cc"]:  # Generates some errors
                    cog = "CustomCommands"
                else:
                    cog = cog.capitalize()
                for x in self.bot.get_cog(cog).get_commands():
                    if isinstance(x, commands.Group):
                        # Is a command
                        for subcmd in x.commands:
                            embed.add_field(name=f"{x.name.capitalize()} {subcmd.name.capitalize()}",
                                            value=f"Description: {x.description}\nUsage: {prefix}{subcmd.usage}",
                                            inline=False)
                    embed.add_field(name=f"{x.name.capitalize()}",
                                    value=f"Description: {x.description}\nUsage: {prefix}{x.usage}", inline=False)
            except:
                embed.add_field(name="No cogs found", value="You have used a name of a non existent cog.", inline=False)

        embed.set_footer(text="PloxHost community bot | Help command")
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
