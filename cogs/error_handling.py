from discord.ext import commands
from discord.ext.commands.errors import *
from tools import RevokedAddedPerms, MissingAddedPerms
import discord
import sys

class Error_handling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.Cog.listener()
    async def on_command_error(self, ctx, exception):
        db = self.database.bot
        posts = db.serversettings
        prefix = "?"
        for x in posts.find({"guild_id": ctx.guild.id}):
            prefix = x['prefix']

        def get_listed(start_list: list):
            end_list = []
            for role in start_list:
                if isinstance(role, discord.Role):
                    end_list.append(role.name)
                else:
                    end_list.append(str(role).replace('_', ' '))
            return ', '.join(end_list)

        error = getattr(exception, "original", exception)
        embed = discord.Embed(colour=0xac6f8f)

        if hasattr(ctx.command, "on_error"):  # If a command has it's own handler
            return

        elif isinstance(error, CheckFailure):
            embed = discord.Embed(colour=0xac6f8f, description=f"{error}")
            embed.set_footer(text="Ploxy | Permission Management")
            await ctx.send(embed=embed)
            return

        elif isinstance(error, RevokedAddedPerms):
            embed = discord.Embed(colour=0xac6f8f, description=f"{error}")
            embed.set_footer(text="Ploxy | Permission Management")
            await ctx.send(embed=embed)
            return
        elif isinstance(error, MissingPermissions):
            embed = discord.Embed(colour=0xac6f8f, description=f"{error}")
            embed.set_footer(text="Ploxy | Permission Management")
            await ctx.send(embed=embed)
            return

        elif isinstance(error, CommandNotFound):
            return

        if isinstance(error, (BadUnionArgument, CommandOnCooldown, PrivateMessageOnly,
                              NoPrivateMessage, MissingRequiredArgument, ConversionError)):

            embed.add_field(name="Error Message:", value=f"\n{error}\nUsage: {prefix}{ctx.command.usage}", inline=False)

        elif isinstance(error, BotMissingPermissions):
            embed.add_field(name="I am missing these permissions to do this command:",
                            value=f"\n{get_listed(error.missing_perms)}", inline=False)

        elif isinstance(error, MissingPermissions):
            embed.add_field(name="You are missing these permissions to do this command:",
                            value=f"\n{get_listed(error.missing_perms)}", inline=False)

        elif isinstance(error, (BotMissingAnyRole, BotMissingRole)):
            embed.add_field(name="I am missing these roles to do this command:",
                            value=f"\n{get_listed(error.missing_roles or [error.missing_role])}", inline=False)

        elif isinstance(error, (MissingRole, MissingAnyRole, MissingAnyRole)):
            embed.add_field(name="You are missing these roles to do this command:",
                            value=f"\n{get_listed(error.missing_roles or [error.missing_role])}", inline=False)
        elif isinstance(error, discord.Forbidden):
            embed.add_field(name="I am not allowed to do this!",
                            value=f"Make sure I am above that user in the roles list and having the correct perms to do so.",
                            inline=False)
        elif isinstance(error, BadArgument):
            print(error)
            embed.add_field(name="Error:",
                            value=f"\n{error}\nUsage: {prefix}{ctx.command.usage}", inline=False)

        else:
            # noinspection PyBroadException
            try:
                error_channel = await self.bot.fetch_channel(809129113985876020)
                await error_channel.send(f"Command: {ctx.command.name}\nGuild ID: {ctx.guild.id}\nUser ID: {ctx.author.id}\nError: {error}")
                await ctx.send(
                    f"Something happened, retry the command. If the issue persists contact the developers!")
            except:
                await ctx.send(
                    f"Something happened, retry the command. If the issue persists contact the developers! Error:\n ```{error}```")
            raise error
        embed.set_footer(text="Ploxy")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Error_handling(bot))
