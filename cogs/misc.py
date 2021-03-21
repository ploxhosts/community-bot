from discord.ext import commands
import discord
import asyncio
import datetime
import time
import random
import tools


class Misc(commands.Cog):
    """Random commands for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.command(name='invite', aliases=["getinvite", "botinvite"],
                      usage="invite", description="Invite the bot to your own server")
    async def invite(self, ctx):
        await ctx.send(
            "You can invite me here: https://discord.com/oauth2/authorize?client_id=809122042573357106&scope=bot&permissions=808840439")


def setup(bot):
    bot.add_cog(Misc(bot))
