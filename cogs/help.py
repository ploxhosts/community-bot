import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.command(name="credit", description="Get the names of the people who developed the bot", usage="credit")
    async def credit(self, ctx):
        embed = discord.Embed(colour=0x36a39f, title="The list of contributors", description="FluxedScript")
        embed.set_footer(text="Ploxy")
        await ctx.send(embed=embed)

    @commands.command(name="help", description="Returns all commands available",
                      aliases=["command", "commands", "commandslist", "listcommands", "lscmds", "cmds", "lscommands"],
                      usage="help")
    async def help(self, ctx, cog=None):
        db = self.database.bot
        posts = db.serversettings
        prefix = "?"
        async for x in posts.find({"guild_id": ctx.guild.id}):
            prefix = x['prefix']

        embed = discord.Embed(colour=0x36a39f, title="Help command")
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

                if c.lower() in ["", "help", "example"]:  # Ignore these
                    pass
                else:
                    if ctx.guild.id not in [346715007469355009, 742055439088353341] and c.lower() == "support":
                        pass
                    else:
                        embed.add_field(name=c, value=self.bot.get_cog(c).description, inline=True)
            embed.add_field(name="To get more detailed information",
                            value=f"{prefix}help <cog> for example: `{prefix}help Mod`", inline=False)
        else:
            # noinspection PyBroadException
            try:
                if self.bot.get_cog(cog.capitalize()):  # Check if it exists
                    pass

                embed = discord.Embed(colour=0x36a39f, title=f"{cog.capitalize()} commands")

                if cog.lower() in ["customcommands", "customcommand", "cc"]:  # Generates some errors
                    cog = "CustomCommands"
                else:
                    cog = cog.capitalize()
                for x in self.bot.get_cog(cog).get_commands():
                    if isinstance(x, commands.Group):
                        # Is a command
                        for subcmd in x.commands:
                            description = x.description
                            if not description:
                                description = "No description provided"
                            embed.add_field(name=f"{x.name.capitalize()} {subcmd.name.capitalize()}",
                                            value=f"Description: {description}\n\nUsage: {prefix}{subcmd.usage}\n\n\u200b",
                                            inline=True)
                    else:
                        description = x.description
                        if not description:
                            description = "No description provided"
                        embed.add_field(name=f"{x.name.capitalize()}", value=f"Description: {description}\n\nUsage: {prefix}{x.usage}\n\n\u200b", inline=True)
            except:
                embed.add_field(name="No cogs found", value="You have used a name of a non existent cog.", inline=False)

        embed.set_footer(text="Ploxy | Help command")
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
