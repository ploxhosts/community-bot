#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
import discord

import tools


class Misc(commands.Cog):
    """Random commands for the bot"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.command(name='invite', aliases=["getinvite", "botinvite"],
                      usage="invite", description="Invite the bot to your own server")
    @tools.has_perm()
    async def invite(self, ctx):
        await ctx.send(
            "You can invite me here: https://discord.com/oauth2/authorize?client_id=809122042573357106&permissions=808840439&scope=bot%20applications.commands")

    @commands.command(name="credit", description="Get the names of the people who developed the bot", usage="credit")
    async def credit(self, ctx):
        embed = discord.Embed(colour=0x36a39f, title="The list of contributors", description="FluxedScript")
        embed.set_footer(text="Ploxy | Contributor list")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Misc(bot))
