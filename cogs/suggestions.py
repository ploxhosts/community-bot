from discord.ext import commands
import discord
import asyncio
import datetime
import time
import random
import tools

# noinspection PyBroadException
class Suggestions(commands.Cog):
    """Commands for suggesting new features"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.command(name='suggest', aliases=["suggestion"], usage="suggest <suggestion>")
    async def suggest(self, ctx, *, suggestion):
        db = self.database.bot
        posts = db.serversettings

        suggestions_config = 0
        flake = (int((time.time() - 946702800) * 1000) << 23) + random.SystemRandom().getrandbits(23)

        for x in posts.find({"guild_id": ctx.guild.id}):
            suggestions_config = x["suggestions"]

        suggestions_channel = suggestions_config['intake_channel']

        embed = discord.Embed(color=0xffffff)
        embed.add_field(name="Suggestion:", value=f"\n{suggestion}")
        embed.set_footer(text=f"ID: {flake} | PloxHost community bot suggestions")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        channel = ctx.guild.get_channel(suggestions_channel)
        message = await channel.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("🟧")
        await message.add_reaction("❌")
        posts = db.suggestions
        posts.insert_one({"guild_id": ctx.guild.id, "user_id": ctx.author.id, "message_id": message.id,
                          "time_sent": datetime.datetime.now().timestamp(), "status": "awaiting for approval",
                          "id": flake, "suggestion": suggestion, "sent_messages": []})
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
        for x in posts.find({"guild_id": ctx.guild.id}):
            denied_channel = x["suggestions"]['denied_channel']
            approve_channel = x["suggestions"]['approved_channel']
            suggestions_channel = x["suggestions"]['intake_channel']
        posts = db.suggestions
        suggestion = None
        user_id = 0
        message_id = 0

        for x in posts.find({"guild_id": ctx.guild.id, "id": flake}):
            suggestion = x["suggestion"]
            user_id = x["user_id"]
            message_id = x["message_id"]
            sent_messages = x["sent_messages"]

        if suggestion is None:
            return await ctx.send("That suggestion does not exist yet.")

        sender = ctx.guild.get_member(user_id)

        embed = discord.Embed(color=0x00FF00, title="Suggestion Accepted")
        if reason is not None:
            embed.add_field(name="Suggestion:",
                            value=f"\n{suggestion}\n\n**Accepted by {ctx.author.mention}**\n{reason}")
        else:
            embed.add_field(name="Suggestion:",
                            value=f"\n{suggestion}\n\n**Accepted by {ctx.author.mention}**")
        embed.set_footer(text=f"ID: {flake} | PloxHost community bot suggestions")
        embed.set_author(name=sender.name, icon_url=sender.avatar_url)

        channel = ctx.guild.get_channel(suggestions_channel)
        message = await channel.fetch_message(message_id)

        await message.edit(embed=embed)
        if approve_channel != 0 and approve_channel != channel.id:
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
        posts.update_one({"guild_id": ctx.guild.id, "message_id": message_id},
                         {"$set": {"status": "approved", "sent_messages": sent_messages}})

    @suggestions.command(name='deny', aliases=["denysuggestion", "reject"], usage="suggestions deny <id> <reason>")
    @tools.has_perm(manage_guild=True)
    async def deny(self, ctx, flake: int, *, reason=None):
        db = self.database.bot
        posts = db.serversettings

        denied_channel = 0
        suggestions_channel = 0
        approved_channel = 0
        for x in posts.find({"guild_id": ctx.guild.id}):
            denied_channel = x["suggestions"]['denied_channel']
            suggestions_channel = x["suggestions"]['intake_channel']
            approved_channel = x["suggestions"]["approved_channel"]
        posts = db.suggestions
        suggestion = None
        user_id = 0
        message_id = 0
        sent_messages = []

        for x in posts.find({"guild_id": ctx.guild.id, "id": flake}):
            suggestion = x["suggestion"]
            user_id = x["user_id"]
            message_id = x["message_id"]
            sent_messages = x["sent_messages"]

        if suggestion is None:
            return await ctx.send("That suggestion does not exist yet.")

        sender = ctx.guild.get_member(user_id)

        embed = discord.Embed(color=0xFF0000, title="Suggestion Denied")
        if reason is not None:
            embed.add_field(name="Suggestion:",
                            value=f"\n{suggestion}\n\n**Denied by {ctx.author.mention}**\n**{reason}**")
        else:
            embed.add_field(name="Suggestion:",
                            value=f"\n{suggestion}\n\n**Denied by {ctx.author.mention}**")
        embed.set_footer(text=f"ID: {flake} | PloxHost community bot suggestions")
        embed.set_author(name=sender.name, icon_url=sender.avatar_url)

        channel = ctx.guild.get_channel(suggestions_channel)
        message = await channel.fetch_message(message_id)

        await message.edit(embed=embed)
        if denied_channel != 0 and denied_channel != channel.id:
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
        posts.update_one({"guild_id": ctx.guild.id, "message_id": message_id},
                         {"$set": {"status": "denied", "sent_messages": sent_messages}})

    # noinspection PyBroadException
    @suggestions.command(name="setup", alias=["channels"], usage="suggestions setup")
    @tools.has_perm(manage_guild=True)
    async def setup(self, ctx):
        db = self.database.bot
        posts = db.serversettings

        def check(msg):
            return msg.channel == ctx.message.channel and msg.author == ctx.author

        embed = discord.Embed(color=0xFF0000, description="Where should suggestions be sent?")
        embed.set_footer(text=f"PloxHost community bot | Suggestions Setup")
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
        embed = discord.Embed(color=0xFF0000,
                              description="Where should suggestions be accepted?\n This can left as 0 to use the same channel as before")
        embed.add_field(name="Suggestions channel", value=f"{intake_channel}")
        embed.set_footer(text=f"PloxHost community bot | Suggestions Setup")
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

        embed = discord.Embed(color=0xFF0000,
                              description="Where should suggestions be denied?\n This can left as 0 to use the same channel as before")
        embed.add_field(name="Suggestions channel", value=f"{intake_channel}")
        embed.add_field(name="Accepted suggestions channel", value=f"{accepted_channel}")
        embed.set_footer(text=f"PloxHost community bot | Suggestions Setup")
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

        embed = discord.Embed(color=0xFF0000,
                              description="Suggestions setup!")
        embed.add_field(name="Suggestions channel", value=f"{intake_channel}")
        embed.add_field(name="Accepted suggestions channel", value=f"{accepted_channel}")
        embed.add_field(name="Denied suggestions channel", value=f"{denied_channel}")
        embed.set_footer(text=f"PloxHost community bot | Suggestions Setup")
        await first_message.edit(embed=embed)

        posts.update_one({"guild_id": ctx.guild.id}, {"$set": {
            "suggestions": {"intake_channel": intake_channel, "approved_channel": accepted_channel,
                            "denied_channel": denied_channel}}})


def setup(bot):
    bot.add_cog(Suggestions(bot))
