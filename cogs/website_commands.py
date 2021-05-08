#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands


# noinspection PyBroadException
class Web(commands.Cog):
    """Commands made for the dashboard"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.group(name='web', aliases=["dashboard", "websitesettings", "websettings"], usage="web")
    async def web(self, ctx):
        pass




def setup(bot):
    bot.add_cog(Web(bot))
