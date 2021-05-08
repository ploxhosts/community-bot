#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord.ext import commands
import discord

import tools

class Settings(commands.Cog):
    """Commands for setting up the bot"""
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.command(name='prefix', aliases=["setprefix"], usage="prefix <newprefix>")
    @tools.has_perm(manage_guild=True)
    async def prefix(self, ctx, *, new_prefix: str = None):
        db = self.database.bot
        posts = db.serversettings
        prefix_org = ""

        async for x in posts.find({"guild_id": ctx.guild.id}):
            prefix_org = x["prefix"]

        if new_prefix is None:  # If command didn't specify a new prefix
            return await ctx.send(f"The prefix is `{prefix_org}`")

        await posts.update_one({"guild_id": ctx.guild.id}, {"$set": {"prefix": new_prefix}})
        await ctx.send(f"New prefix is `{new_prefix}` from `{prefix_org}`")

    @commands.command(name='logchannel', aliases=["setlogchannel", "logschannel"], usage="logchannel #channel")
    @tools.has_perm(manage_guild=True)
    async def logchannel(self, ctx, *, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        db = self.database.bot
        posts = db.serversettings
        channel_org = 0

        async for x in posts.find({"guild_id": ctx.guild.id}):
            channel_org = x["log_channel"]

        await posts.update_one({"guild_id": ctx.guild.id}, {"$set": {"log_channel": channel.id}})
        if channel_org != 0:
            await ctx.send(f"New log channel is <#{channel.id}> from <#{channel_org}>")
        else:
            await ctx.send(f"New log channel is <#{channel.id}>")


def setup(bot):
    bot.add_cog(Settings(bot))
