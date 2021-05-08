#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from discord.ext import commands
import discord

import tools

default_prefix = os.getenv('prefix')


class Welcome(commands.Cog):
    """Commands that relate to users"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    async def cog_check(self, ctx):
        return ctx.guild.id in [346715007469355009, 742055439088353341]  # Replace list with people who you trust

    @commands.command(name='welcomechannel', aliases=["wchannel", "welcomchannel", "channelwelcome"],
                      usage="welcomechannel #channel", description="Allow the use of welcome messages")
    @tools.has_perm(manage_messages=True)
    async def welcomechannel(self, ctx, *, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        db = self.database.bot
        posts = db.serversettings
        channel_org = 0

        async for x in posts.find({"guild_id": ctx.guild.id}):
            channel_org = x["welcome"]["channel"]

        await posts.update_one({"guild_id": ctx.guild.id}, {"$set": {"welcome.channel": channel.id}})
        if channel_org != 0:
            await ctx.send(f"New welcome channel is <#{channel.id}> from <#{channel_org}>")
        else:
            await ctx.send(f"New welcome channel is <#{channel.id}>")

    @commands.group(name='welcome', aliases=["walcome", "wcme"],
                    usage="welcome", description="Welcome commands")
    @tools.has_perm(manage_messages=True)
    async def welcome(self, ctx):
        embed = discord.Embed(colour=0x36a39f, title=f"Welcome Commands")
        embed.add_field(name="Set welcome channel:",
                        value=f"`{ctx.prefix}welcomechannel #channel`",
                        inline=False)
        embed.add_field(name="Shows this message:",
                        value=f"`{ctx.prefix}welcome`",
                        inline=False)
        embed.add_field(name="Set a welcome message:",
                        value=f"`{ctx.prefix}welcome text <This is welcome text>` - Allows you to set the welcome message",
                        inline=False)
        embed.set_footer(text="Ploxy | Permissions Management")
        await ctx.send(embed=embed)

    @welcome.command(name='text', aliases=["message", "txt"],
                     usage="welcome text Welcome to the great server", description="Set a custom welcome message")
    @tools.has_perm(manage_messages=True)
    async def text(self, ctx, *, message=None):

        db = self.database.bot
        posts = db.serversettings
        welcome_message = 0

        async for x in posts.find({"guild_id": ctx.guild.id}):
            welcome_message = x["welcome"]["message"]

        if message:
            await posts.update_one({"guild_id": ctx.guild.id}, {"$set": {"welcome.message": message}})
            await ctx.send(f"New welcome message is `{message}` from `{welcome_message}`")
        else:
            await ctx.send(f"The welcome message is `{message}`")


def setup(bot):
    bot.add_cog(Welcome(bot))
