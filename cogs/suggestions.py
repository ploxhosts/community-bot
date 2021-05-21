import asyncio
import datetime
import random
import time

import discord
from discord.ext import commands

import tools


# noinspection PyBroadException
class Suggestions(commands.Cog):
    """Commands for suggesting new features in the server"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.command(name='suggest', aliases=["suggestion"], usage="suggest <suggestion>")
    @tools.has_perm()
    async def suggest(self, ctx, *, suggestion):
        db = self.database.bot
        posts = db.serversettings

        suggestions_config = 0
        flake = (int((time.time() - 946702800) * 1000) << 23) + random.SystemRandom().getrandbits(23)

        async for x in posts.find({"guild_id": ctx.guild.id}):
            suggestions_config = x["suggestions"]

        suggestions_channel = suggestions_config['intake_channel']

        embed = discord.Embed(color=0xffffff)
        embed.add_field(name="Suggestion:", value=f"\n{suggestion}")
        embed.set_footer(text=f"ID: {flake} | Ploxy suggestions")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        channel = ctx.guild.get_channel(suggestions_channel)
        if channel is None:
            embed = discord.Embed(colour=0x36a39f,
                                  description=f"{ctx.guild} does not have suggestions setup.\n This can be done with the `{ctx.prefix}suggestions setup` command")
            embed.set_footer(text="Ploxy | Suggestions")
            return await ctx.send(embed=embed)
        message = await channel.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("🟧")
        await message.add_reaction("❌")
        posts = db.suggestions
        posts.insert_one({"guild_id": ctx.guild.id, "user_id": ctx.author.id, "message_id": message.id,
                          "time_sent": datetime.datetime.now().timestamp(), "edits": 0, "g_votes": 0, "n_votes": 0,
                          "b_votes": 0, "status": "awaiting for approval",
                          "id": flake, "suggestion": suggestion, "sent_messages": [], "comments": []})
        await ctx.author.send("Suggestions added! 🧧")
        await asyncio.sleep(1)
        await ctx.message.delete()

    @commands.group(name='suggestions', aliases=["suggests"], usage="suggestions")
    async def suggestions(self, ctx):
        pass

    @suggestions.command(name='approve', aliases=["approvesuggestion", "suggestapprove", "accept", "acceptsuggestion"],
                         usage="suggestions approve <id> <reason>")
    @tools.has_perm(manage_guild=True)
    async def approve(self, ctx, flake: int, *, reason=None):
        db = self.database.bot
        posts = db.serversettings

        approve_channel = 0
        suggestions_channel = 0
        denied_channel = 0

        sent_messages = []
        async for x in posts.find({"guild_id": ctx.guild.id}):
            denied_channel = x["suggestions"]['denied_channel']
            approve_channel = x["suggestions"]['approved_channel']
            suggestions_channel = x["suggestions"]['intake_channel']
        posts = db.suggestions
        suggestion = None
        user_id = 0
        message_id = 0
        g_votes = 0
        n_votes = 0
        b_votes = 0

        async for x in posts.find({"guild_id": ctx.guild.id, "id": flake}):
            suggestion = x["suggestion"]
            user_id = x["user_id"]
            message_id = x["message_id"]
            sent_messages = x["sent_messages"]
            try:
                g_votes = x["g_votes"]  # good votes
                n_votes = x["n_votes"]  # neutral
                b_votes = x["b_votes"]  # bad votes
            except:
                pass

        if suggestion is None:
            return await ctx.send("That suggestion does not exist yet.")

        sender = ctx.guild.get_member(user_id)

        embed = discord.Embed(color=0x00FF00, title="Suggestion Accepted")
        if reason is not None:
            embed.add_field(name="Suggestion:",
                            value=f"\n{suggestion}\n\n**Accepted by {ctx.author.mention}**\n{reason}\n\nVotes:\n✅ {g_votes} | 🟧 {n_votes} | ❌ {b_votes}\n")
        else:
            embed.add_field(name="Suggestion:",
                            value=f"\n{suggestion}\n\n**Accepted by {ctx.author.mention}**\n\nVotes:\n✅ {g_votes} | 🟧 {n_votes} | ❌ {b_votes}\n")
        embed.set_footer(text=f"ID: {flake} | Ploxy suggestions")
        embed.set_author(name=sender.name, icon_url=sender.avatar_url)

        channel = ctx.guild.get_channel(suggestions_channel)
        message = await channel.fetch_message(message_id)
        await message.clear_reactions()

        await message.edit(embed=embed)
        if approve_channel not in [0, channel.id]:
            accept_channel = ctx.guild.get_channel(approve_channel)
            newmsg = await accept_channel.send(embed=embed)
            if sent_messages:
                deny_channel = ctx.guild.get_channel(denied_channel)
                for message_sent in sent_messages:
                    message_sent_obj = 0
                    try:
                        message_sent_obj = await deny_channel.fetch_message(message_sent)
                    except:
                        try:
                            message_sent_obj = await accept_channel.fetch_message(message_sent)
                        except:
                            pass  # Not found
                    await message_sent_obj.delete()  # We want to overwrite the previous message

            sent_messages = [newmsg.id]
        await posts.update_one({"guild_id": ctx.guild.id, "message_id": message_id},
                               {"$set": {"status": "approved", "sent_messages": sent_messages}})
        await ctx.send("Accepted the suggestion")

    @suggestions.command(name='deny', aliases=["denysuggestion", "reject"], usage="suggestions deny <id> <reason>")
    @tools.has_perm(manage_guild=True)
    async def deny(self, ctx, flake: int, *, reason=None):
        db = self.database.bot
        posts = db.serversettings

        denied_channel = 0
        suggestions_channel = 0
        approved_channel = 0
        async for x in posts.find({"guild_id": ctx.guild.id}):
            denied_channel = x["suggestions"]['denied_channel']
            suggestions_channel = x["suggestions"]['intake_channel']
            approved_channel = x["suggestions"]["approved_channel"]
        posts = db.suggestions
        suggestion = None
        user_id = 0
        message_id = 0
        sent_messages = []
        g_votes = 0
        n_votes = 0
        b_votes = 0

        async for x in posts.find({"guild_id": ctx.guild.id, "id": flake}):
            suggestion = x["suggestion"]
            user_id = x["user_id"]
            message_id = x["message_id"]
            sent_messages = x["sent_messages"]
            try:
                g_votes = x["g_votes"]  # good votes
                n_votes = x["n_votes"]  # neutral
                b_votes = x["b_votes"]  # bad votes
            except:
                pass

        if suggestion is None:
            return await ctx.send("That suggestion does not exist yet.")

        sender = ctx.guild.get_member(user_id)

        embed = discord.Embed(color=0xFF0000, title="Suggestion Denied")
        if reason is not None:
            embed.add_field(name="Suggestion:",
                            value=f"\n{suggestion}\n\n**Denied by {ctx.author.mention}**\n**{reason}**\n\nVotes:\n✅ {g_votes} | 🟧 {n_votes} | ❌ {b_votes}\n")
        else:
            embed.add_field(name="Suggestion:",
                            value=f"\n{suggestion}\n\n**Denied by {ctx.author.mention}**\n\nVotes:\n✅ {g_votes} | 🟧 {n_votes} | ❌ {b_votes}\n")
        embed.set_footer(text=f"ID: {flake} | Ploxy suggestions")
        embed.set_author(name=sender.name, icon_url=sender.avatar_url)

        channel = ctx.guild.get_channel(suggestions_channel)
        message = await channel.fetch_message(message_id)

        await message.edit(embed=embed)
        await message.clear_reactions()

        if denied_channel not in [0, channel.id]:
            deny_channel = ctx.guild.get_channel(denied_channel)
            newmsg = await deny_channel.send(embed=embed)
            if sent_messages:
                accept_channel = ctx.guild.get_channel(approved_channel)
                for message_sent in sent_messages:
                    message_sent_obj = 0
                    try:
                        message_sent_obj = await deny_channel.fetch_message(message_sent)
                    except:
                        try:
                            message_sent_obj = await accept_channel.fetch_message(message_sent)
                        except:
                            pass  # Not found
                    await message_sent_obj.delete()  # We want to overwrite the previous message

            sent_messages = [newmsg.id]
        await posts.update_one({"guild_id": ctx.guild.id, "message_id": message_id},
                               {"$set": {"status": "denied", "sent_messages": sent_messages}})
        await ctx.send("Denied the suggestion")

    # noinspection PyBroadException
    @suggestions.command(name="setup", alias=["channels"], usage="suggestions setup")
    @tools.has_perm(manage_guild=True)
    async def setup(self, ctx):
        db = self.database.bot
        posts = db.serversettings

        def check(msg):
            return msg.channel == ctx.message.channel and msg.author == ctx.author

        embed = discord.Embed(color=0x36a39f, description="Where should suggestions be sent?")
        embed.set_footer(text=f"Ploxy | Suggestions Setup")
        first_message = await ctx.send(embed=embed)
        try:
            intake = await self.bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            return await ctx.send("You must reply in time!")
        except Exception as e:
            return print(e)

        try:
            intake_channel = intake.channel_mentions[0].id
        except:
            return await ctx.send("It must be a channel mention!")
        embed = discord.Embed(color=0x36a39f,
                              description="Where should suggestions be accepted?\n This can left as 0 to use the same channel as before")
        embed.add_field(name="Suggestions channel", value=f"{intake_channel}")
        embed.set_footer(text=f"Ploxy | Suggestions Setup")
        await first_message.edit(embed=embed)
        try:
            intake = await self.bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            return await ctx.send("You must reply in time!")
        try:
            if intake.content == "0":
                accepted_channel = intake_channel
            else:
                accepted_channel = intake.channel_mentions[0].id
        except:
            return await ctx.send("It must be a channel mention!")

        embed = discord.Embed(color=0x36a39f,
                              description="Where should suggestions be denied?\n This can left as 0 to use the same channel as before")
        embed.add_field(name="Suggestions channel", value=f"{intake_channel}")
        embed.add_field(name="Accepted suggestions channel", value=f"{accepted_channel}")
        embed.set_footer(text=f"Ploxy | Suggestions Setup")
        await first_message.edit(embed=embed)
        try:
            intake = await self.bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            return await ctx.send("You must reply in time!")
        try:
            if intake.content == "0":
                denied_channel = accepted_channel
            else:
                denied_channel = intake.channel_mentions[0].id
        except:
            return await ctx.send("It must be a channel mention!")

        embed = discord.Embed(color=0x36a39f,
                              description="Suggestions setup!")
        embed.add_field(name="Suggestions channel", value=f"{intake_channel}")
        embed.add_field(name="Accepted suggestions channel", value=f"{accepted_channel}")
        embed.add_field(name="Denied suggestions channel", value=f"{denied_channel}")
        embed.set_footer(text=f"Ploxy | Suggestions Setup")
        await first_message.edit(embed=embed)

        await posts.update_one({"guild_id": ctx.guild.id}, {"$set": {
            "suggestions": {"intake_channel": intake_channel, "approved_channel": accepted_channel,
                            "denied_channel": denied_channel}}})

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        db = self.database.bot
        posts = db.suggestions
        g_votes = 0
        n_votes = 0
        b_votes = 0
        valid = False
        try:
            async for x in posts.find({"guild_id": payload.guild_id, "message_id": payload.message_id}):
                valid = x["user_id"]
                g_votes = x["g_votes"]  # good votes
                n_votes = x["n_votes"]  # neutral
                b_votes = x["b_votes"]  # bad votes
        except KeyError:
            pass
        if not valid:
            return
        if str(payload.emoji) == "✅":
            g_votes -= 1
        elif str(payload.emoji) == "🟧":
            n_votes -= 1
        elif str(payload.emoji) == "❌":
            b_votes -= 1
        await posts.update_one({"guild_id": payload.guild_id, "message_id": payload.message_id},
                               {"$set": {"g_votes": g_votes, "n_votes": n_votes, "b_votes": b_votes}})

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        db = self.database.bot
        posts = db.suggestions
        g_votes = 0
        n_votes = 0
        b_votes = 0
        valid = False
        try:
            async for x in posts.find({"guild_id": payload.guild_id, "message_id": payload.message_id}):
                valid = x["user_id"]
                g_votes = x["g_votes"]  # good votes
                n_votes = x["n_votes"]  # neutral
                b_votes = x["b_votes"]  # bad votes
        except KeyError:
            pass
        if not valid:
            return
        if str(payload.emoji) == "✅":
            g_votes += 1
        elif str(payload.emoji) == "🟧":
            n_votes += 1
        elif str(payload.emoji) == "❌":
            b_votes += 1
        await posts.update_one({"guild_id": payload.guild_id, "message_id": payload.message_id},
                               {"$set": {"g_votes": g_votes, "n_votes": n_votes, "b_votes": b_votes}})


def setup(bot):
    bot.add_cog(Suggestions(bot))
