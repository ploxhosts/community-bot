#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.parse import urlparse
from collections import Counter
import datetime
import asyncio
import random
import os
import re

from discord.ext import commands
import discord

import tools


class Chat(commands.Cog):
    """Chat moderation features"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database
        self.message_cache = {}
        self.muted_users = []
        self.spam_warned_users = []

    async def create_muted_role(self, guild):
        db = self.database.bot
        posts = db.serversettings
        role = await posts.find_one({"guild_id": guild.id})['muted_role_id']
        if not role:
            role = await guild.create_role(name="Muted", reason="Muted role is needed")
            for category in guild.categories:
                perms = category.overwrites_for(role)
                perms.send_messages = False
                await category.set_permissions(role, overwrite=perms, reason="Muted!")
            for channel in guild.channels:
                if not channel.permissions_synced:
                    perms = channel.overwrites_for(role)
                    perms.send_messages = False
                    await channel.set_permissions(role, overwrite=perms, reason="Muted!")
            await posts.update_one({"guild_id": guild.id},
                                   {"$set": {"muted_role_id": role.id}})
        else:
            role = guild.get_role(role)
        return role

    async def give_muted_role(self, guild, member, user_id, role, duration):
        if role not in member.roles:
            await member.add_roles(role, reason="Muted")
            db = self.database.bot
            posts = db.serversettings
            channel = await posts.find_one({"guild_id": guild.id})['log_channel']
            await self.send_log_embed(channel, f"Muted {member.name}#{member.discriminator} for {duration}",
                                      f"Muted {member.display_name} with id of: {user_id}")
            return True
        else:
            return False

    # noinspection PyMethodMayBeStatic
    async def delete_message(self, message):
        try:
            await message.delete()
            return "Deleted"
        except discord.NotFound:  # Deleted already
            return "None"

    async def send_log_embed(self, channel, title, message):
        if channel == 0:
            return

        embed = discord.Embed(colour=0x36a39f, title=title)
        embed.add_field(name="Message:", value=f"\n{message}", inline=False)
        embed.set_footer(text="Ploxy | Chat Moderation")
        log_channel = self.bot.get_channel(channel)

        await log_channel.send(embed=embed)

    async def check_contents_once(self, message):
        if message.author.bot:
            return
        spam_msg = None
        time_warned = datetime.datetime.now()
        c = Counter()
        BANNED_WORDS = []
        log_channel = 0
        prefix = os.getenv('prefix')
        MAX_MENTIONS = 0
        ban_on_mass_mention = 0
        auto_temp_ban_time = 1440
        auto_mute_time = 30
        db = self.database.bot
        posts = db.serversettings
        async for x in posts.find({"guild_id": message.guild.id}):
            log_channel = x["log_channel"]
            prefix = x["prefix"]
            BANNED_WORDS = x["auto_mod"]["banned_words"]
            MAX_MENTIONS = x["auto_mod"]["max_mentions"]
            ban_on_mass_mention = x["auto_mod"]["on_mass_mention"]
            auto_temp_ban_time = x["auto_mod"]["auto_temp_ban_time"]
            auto_mute_time = x["auto_mod"]["auto_mute_time"]

        posts = db.player_data
        logs = await posts.find_one({"user_id": message.author.id, "guild_id": message.guild.id})
        if logs is not None:
            logs = logs["mod_logs"]
        if not logs:
            logs = []

        if not self.message_cache.get(message.author.id):
            self.message_cache[message.author.id] = [
                {"content": message.content, "id": message.id, "time_sent": datetime.datetime.now()}]
        else:
            if not str(message.content).startswith(prefix):
                content = list(self.message_cache.get(message.author.id))
                content.append({"content": message.content, "id": message.id, "time_sent": datetime.datetime.now()})
                self.message_cache.update({message.author.id: content})
        message_list = list(self.message_cache.get(message.author.id))
        if len(message_list) > 3:
            duplicate_items = []

            for item in message_list:  # Count the occurrence
                c[item["content"]] += 1

            for x in message_list:
                if c.get(x["content"]) > 1:  # If more than once add it to duplicate items
                    if x not in duplicate_items:
                        duplicate_items.append(x)
            if duplicate_items:
                time_diff = duplicate_items[0]["time_sent"] - duplicate_items[-1]["time_sent"]
                if time_diff.total_seconds() <= 12:
                    for x in duplicate_items:
                        if c.get(x["content"]) > 6:  # Mute
                            goThrough = True
                            try:
                                for muted_user in self.muted_users:  # If in cache
                                    if muted_user["id"] == message.author.id:
                                        goThrough = False
                            except KeyError:
                                pass
                            if goThrough:
                                self.muted_users.append(
                                    {"id": message.author.id, "guild": message.guild.id, "time": auto_mute_time * 60})
                                posts = db.pending_mutes
                                role_list = []
                                for role_it in message.author.roles:
                                    if role_it.name != "@everyone":
                                        await message.author.remove_roles(role_it, reason="Muted")
                                        role_list.append(role_it.id)
                                await posts.insert_one(
                                    {"guild_id": message.guild.id, "user_id": message.author.id,
                                     "time": auto_mute_time * 60,
                                     "issued": time_warned, "roles": role_list})
                                posts = db.player_data

                                logs.append(
                                    {"type": "MUTED", "warn_id": tools.generate_flake(), "reason": "spam",
                                     "issuer": "SYSTEM",
                                     "time": time_warned.strftime('%c')})

                                await posts.update_one({"user_id": message.author.id, "guild_id": message.guild.id},
                                                       {"$set": {"mod_logs": logs}})

                                await self.give_muted_role(message.guild, message.author, message.author.id,
                                                           await self.create_muted_role(message.guild),
                                                           auto_mute_time * 60)
                                await message.author.send(
                                    f"You have been muted in {message.guild} for {auto_mute_time * 60} minutes for spam!")
                        elif c.get(x["content"]) > 3:
                            done = True
                            found_user = False
                            for warned_users in self.spam_warned_users:
                                if warned_users["user"] == message.author.id:
                                    found_user = True
                                    diff = datetime.datetime.now() - warned_users["time"]
                                    if diff.total_seconds() > 60:
                                        done = False
                                        self.spam_warned_users.remove(warned_users)
                            if not found_user:
                                done = False
                            if not done:
                                spam_msg = await message.channel.send("Please do not send duplicate messages!")
                                self.spam_warned_users.append(
                                    {"user": message.author.id, "guild": message.guild.id, "time": time_warned})
                                if message.guild == 346715007469355009:
                                    fluxed_channel = message.guild.get_channel(824417561735200838)
                                    await fluxed_channel.send(
                                        f"USER CHAT WARNING!\n**User ID:** {message.author.id}\n**USER name:** {message.author.name}\n**self.spam_warned_users**: ```\n{self.spam_warned_users}\n```\n**Message list**:\n```\n{message_list}\n```"
                                    )
                if (len(message_list)) > 10:
                    time_diff = duplicate_items[-1]["time_sent"] - duplicate_items[0]["time_sent"]
                    if time_diff.total_seconds() > 13:
                        self.message_cache.pop(message.author.id)
        for bad_word in BANNED_WORDS:
            if bad_word in message.content.lower():
                if await self.delete_message(message) == "Deleted":
                    self.bot.delete_message_cache.append(message.id)
                    guild = self.bot.get_guild(message.guild.id)
                    channel = guild.get_channel(message.channel.id)
                    messages = await channel.history(limit=5).flatten()
                    done = False
                    for message2 in messages:
                        if message2.content == "A message was deleted as it contained a banned word.":
                            done = True
                    if not done:
                        await channel.send("A message was deleted as it contained a banned word.")
                    embed = discord.Embed(colour=0x36a39f, title="Blacklisted word has been deleted in a message!")
                    embed.add_field(name="Message", value=f"{message.content}", inline=True)
                    embed.add_field(name="Word", value=f"`{bad_word}`", inline=False)
                    embed.add_field(name="Author",
                                    value=f"{message.author.name}#{message.author.discriminator} ({message.author.id})",
                                    inline=True)
                    embed.add_field(name="Channel", value=f"{message.channel.mention}", inline=True)
                    embed.set_footer(text="Ploxy | Chat Moderation")
                    log_channel_obj = self.bot.get_channel(log_channel)

                    await log_channel_obj.send(embed=embed)

        if len(message.mentions) > MAX_MENTIONS != 0:
            guild = self.bot.get_guild(message.guild.id)
            channel = guild.get_channel(message.channel.id)
            if await self.delete_message(message) == "Deleted":
                self.bot.delete_message_cache.append(message.id)
                await channel.send("A message was deleted as it contained too many mentions.")

                embed = discord.Embed(colour=0x36a39f, title="Message exceeded mention limit!")
                embed.add_field(name="Message", value=f"{message.content}", inline=True)
                embed.add_field(name="Mentions", value=f"`{len(message.mentions)}`", inline=False)
                embed.add_field(name="Author",
                                value=f"{message.author.name}#{message.author.discriminator} ({message.author.id})",
                                inline=True)
                embed.add_field(name="Channel", value=f"{message.channel.mention}", inline=True)
                embed.set_footer(text="Ploxy | Chat Moderation")
                log_channel_obj = self.bot.get_channel(log_channel)

                await log_channel_obj.send(embed=embed)
            if ban_on_mass_mention == 1:  # Mute
                posts = db.pending_mutes
                if await posts.find_one({"guild_id": message.guild.id, "user_id": message.author.id}):
                    pass
                else:
                    role_list = []
                    for role_it in message.author.roles:
                        if role_it.name != "@everyone":
                            await message.author.remove_roles(role_it, reason="Muted")
                            role_list.append(role_it.id)
                    await posts.insert_one(
                        {"guild_id": message.guild.id, "user_id": message.author.id, "time": auto_mute_time,
                         "issued": time_warned, "roles": role_list})
                    posts = db.player_data

                    logs.append(
                        {"type": "MUTED", "warn_id": tools.generate_flake(), "reason": "Mass mention",
                         "issuer": "SYSTEM",
                         "time": time_warned.strftime('%c')})

                    await posts.update_one({"user_id": message.author.id, "guild_id": message.guild.id},
                                           {"$set": {"mod_logs": logs}})

                    await self.give_muted_role(message.guild, message.author, message.author.id,
                                               await self.create_muted_role(message.guild), auto_mute_time)
            elif ban_on_mass_mention == 2:  # Kick
                posts = db.player_data

                logs.append(
                    {"type": "KICKED", "warn_id": tools.generate_flake(), "reason": "Mass mention", "issuer": "SYSTEM",
                     "time": time_warned.strftime('%c')})

                await posts.update_one({"user_id": message.author.id, "guild_id": message.guild.id},
                                       {"$set": {"mod_logs": logs}})
                await guild.kick(user=message.author.id, reason="Mass mention - auto moderation")
                await channel.send(
                    f"{message.author.id} | {message.author.name} has been kicked for mentioning too many people!")
            elif ban_on_mass_mention == 3:  # Temp ban
                posts = db.pending_bans
                await posts.insert_one(
                    {"guild_id": message.guild.id, "user_id": message.author.id, "time": auto_temp_ban_time,
                     "issued": time_warned})
                posts = db.player_data

                warn_id = tools.generate_flake()
                logs.append(
                    {"type": "TEMP-BANNED", "warn_id": warn_id, "reason": "Mass mention",
                     "issuer": "SYSTEM",
                     "time": time_warned.strftime('%c')})

                await posts.update_one({"user_id": message.author.id, "guild_id": message.guild.id},
                                       {"$set": {"mod_logs": logs}})
                await guild.ban(user=message.author,
                                reason=f"Mass mention - auto moderation(TEMP BAN) with warn id id of {warn_id}",
                                delete_message_days=0)
            elif ban_on_mass_mention == 4:  # Perm ban
                posts = db.player_data

                logs.append(
                    {"type": "BANNED", "warn_id": tools.generate_flake(), "reason": "Mass mention",
                     "issuer": "SYSTEM",
                     "time": time_warned.strftime('%c')})

                await posts.update_one({"user_id": message.author.id, "guild_id": message.guild.id},
                                       {"$set": {"mod_logs": logs}})
                await guild.ban(user=message.author.id, reason="Mass mention - auto moderation", delete_message_days=0)
                await channel.send(
                    f"{message.author.id} | {message.author.name} has been banned from the server for mentioning too many people!")
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|%[0-9a-fA-F][0-9a-fA-F])+',
                          message.content)
        spam_links = []
        for url in urls:
            if urls.count(url) > 2:
                spam_links.append(url)

        if spam_links:
            posts = db.player_data
            await message.delete()
            role_list = []
            for role_it in message.author.roles:
                if role_it.name != "@everyone":
                    await message.author.remove_roles(role_it, reason="Muted")
                    role_list.append(role_it.id)
            await posts.insert_one(
                {"guild_id": message.guild.id, "user_id": message.author.id, "time": auto_mute_time,
                 "issued": time_warned, "roles": role_list})
            posts = db.player_data

            logs.append(
                {"type": "MUTED", "warn_id": tools.generate_flake(), "reason": ":Link spam",
                 "issuer": "SYSTEM",
                 "time": time_warned.strftime('%c')})

            await posts.update_one({"user_id": message.author.id, "guild_id": message.guild.id},
                                   {"$set": {"mod_logs": logs}})

            await self.give_muted_role(message.guild, message.author, message.author.id,
                                       await self.create_muted_role(message.guild), auto_mute_time)

        if spam_msg:
            await asyncio.sleep(10)
            await spam_msg.delete()
        # <(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>

    async def check_contents_both(self, message1, message2):
        if message1.attachments is None or message2.attachments is None:  # Could be multiple image
            return
        if len(message1.attachments) == len(message2.attachments) and len(
                message1.attachments):  # Same amount it is about 2 images
            # Attachments/images/files
            for attachment1, attachment2 in zip(message1.attachments,
                                                message2.attachments):  # Loop through each attachment
                if attachment1.size == attachment2.size:  # The bytes are the same so the image is 99% the same
                    try:
                        if await self.delete_message(message2) == "Deleted":
                            messages = await message2.channel.history(limit=5).flatten()
                            done = any(
                                message3.content
                                in [
                                    "We do not allow duplicate messages",
                                    "We do not allow duplicate images/files being posted!",
                                ]
                                for message3 in messages
                            )

                            if not done:
                                await message2.channel.send("We do not allow duplicate images/files being posted!")
                    except discord.NotFound:  # Deleted
                        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        if message.author.bot:
            return
        db = self.database.bot
        posts = db.serversettings
        chat_moderation = 1
        anti_invite = 1
        blacklisted_domains = []
        allowed_invites = []
        log_channel = 0
        ignore_roles = []
        ignore_channels_mod = []
        async for x in posts.find({"guild_id": message.guild.id}):
            chat_moderation = x["auto_mod"]["chat_moderation"]
            blacklisted_domains = x["auto_mod"]["blacklisted_domains"]
            anti_invite = x["auto_mod"]["anti_invite"]
            allowed_invites = x["auto_mod"]["allowed_invites"]
            log_channel = x["log_channel"]
            ignore_roles = x["auto_mod"]["ignore_roles"]
            ignore_channels_mod = x["auto_mod"]["mod_ignore_channels"]
        if message.channel.id in ignore_channels_mod:
            return
        for x in ignore_roles:
            role = message.guild.get_role(x)
            if role in message.author.roles:
                return
        if anti_invite == 1:
            def find_url(message_content):
                regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
                url2 = re.findall(regex, message_content)
                return [url2m[0] for url2m in url2]

            if len(find_url(message.content)) == 0:
                pass
            else:
                felony_message = False
                bad_links = []
                for url in find_url(message.content):
                    if "discord.gg" in url.lower() and url in allowed_invites:
                        pass
                    elif "discord.gg" in url.lower():
                        bad_links.append(url)
                        felony_message = True
                    parsed_url = urlparse(url)
                    if parsed_url.hostname in blacklisted_domains:
                        bad_links.append(url)
                        felony_message = True
                if felony_message:
                    await self.delete_message(message)
                    if log_channel == 0:
                        return
                    embed = discord.Embed(colour=0x36a39f, title="Chat moderation")
                    embed.add_field(name="Author:", value=f"\n{message.author}", inline=False)
                    embed.add_field(name="Author ID:", value=f"\n{message.author.id}", inline=False)
                    embed.add_field(name="Message:", value=f"\n{message.content}", inline=False)
                    embed.add_field(name="Message ID:", value=f"\n{message.id}", inline=False)
                    embed.add_field(name="Links:", value=f"\n{','.join(bad_links)}", inline=False)
                    embed.set_footer(text="Ploxy | Chat filter")
                    log_channel = self.bot.get_channel(log_channel)
                    await log_channel.send(embed=embed)
                    await message.author.send("Dm advertisement isn't allowed!")
        if chat_moderation == 1:
            def check(message2):
                return message2.author == message.author and message2.channel == message.channel

            timeout_time = random.randint(10, 30)
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=timeout_time)
            except asyncio.TimeoutError:
                return
            await self.check_contents_once(msg)
            await self.check_contents_both(message, msg)

    @commands.group(invoke_without_command=True, case_sensitive=False, name="chat", aliases=["chatsettings"],
                    usage="chat")
    async def chat(self, ctx):
        db = self.database.bot
        posts = db.serversettings
        prefix = os.getenv('prefix')
        async for x in posts.find({"guild_id": ctx.guild.id}):
            prefix = x['prefix']
        embed = discord.Embed(
            title="Chat moderation help",
            description="This helps you config the chat moderation system",
            color=0xeee657)
        embed.add_field(
            name="Enable/Disable chat mod",
            value=f"{prefix}chat mod <enable|disable>",
            inline=False)
        embed.add_field(
            name="Add/Remove blacklisted words",
            value=f"{prefix}chat words <add|remove|list>",
            inline=False)
        embed.add_field(
            name="Add/Remove blacklisted links",
            value=f"{prefix}chat link <add|remove|list>",
            inline=False)
        embed.add_field(
            name="Add/Remove role bypass",
            value=f"{prefix}chat role <add|remove|list>",
            inline=False)
        embed.add_field(
            name="Add/Remove allowed invites",
            value=f"{prefix}chat invites <add|remove|list>",
            inline=False)
        embed.add_field(
            name="Set/Reset max mentions",
            value=f"{prefix}chat mentions <set|reset>",
            inline=False)
        embed.add_field(
            name="Set/Reset temp ban time",
            value=f"{prefix}chat bans <set|reset> <minutes>",
            inline=False)
        embed.add_field(
            name="Set/Reset auto mute time",
            value=f"{prefix}chat mutes <set|reset> <minutes>",
            inline=False)
        await ctx.send(embed=embed)

    @chat.command(name="words", aliases=["word", "text"], usage="chat words <add|remove|list>")
    @tools.has_perm(manage_messages=True)
    async def words(self, ctx, option, *, text=None):
        db = self.database.bot
        posts = db.serversettings
        BANNED_WORDS = []
        async for x in posts.find({"guild_id": ctx.guild.id}):
            BANNED_WORDS = x["auto_mod"]["banned_words"]

        def has_text():
            return text is None

        if option.lower() in ["add", "addition", "insert"]:
            if has_text():
                return await ctx.send("You must specify some word to add to the blacklist!")

            if text.lower() in BANNED_WORDS:
                return await ctx.send("This word already exists!")

            BANNED_WORDS.append(text.lower())

            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.banned_words": BANNED_WORDS}})
            await ctx.send(f"Added {text} to filter!")
        elif option.lower() in ["remove", "delete", "del", "take"]:
            if has_text():
                return await ctx.send("You must specify some word to remove from the blacklist!")

            if text.lower() not in BANNED_WORDS:
                return await ctx.send("You can't remove something that doesn't exist!")

            if text.lower() in BANNED_WORDS:
                BANNED_WORDS.remove(text.lower())

                await posts.update_one({"guild_id": ctx.guild.id},
                                       {"$set": {"auto_mod.banned_words": BANNED_WORDS}})

                await ctx.send(f"Removed {text} from filter!")
            else:
                await ctx.send("That phrase doesn't exist!")

        elif option.lower() in ["list", "total"]:
            description_string = ""

            for keyword in BANNED_WORDS:
                description_string = description_string + f"\n{keyword}"

            em = discord.Embed(title="Banned words list", description=description_string, color=855330)
            em.set_footer(text="Ploxy | Chat filter")

            await ctx.send(embed=em)

    @chat.command(name="links", aliases=["link"], usage="chat link <add|remove|list>")
    @tools.has_perm(manage_messages=True)
    async def links(self, ctx, option, *, text=None):
        db = self.database.bot
        posts = db.serversettings
        BANNED_LINKS = []
        log_channel = 0
        async for x in posts.find({"guild_id": ctx.guild.id}):
            BANNED_LINKS = x["auto_mod"]["blacklisted_domains"]
            log_channel = x["log_channel"]

        if option.lower() in ["add", "addition", "insert"]:
            if text.lower() in BANNED_LINKS:
                return await ctx.send("This domain already exists!")

            BANNED_LINKS.append(text.lower())

            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.blacklisted_domains": BANNED_LINKS}})
            await self.send_log_embed(log_channel, f"{ctx.author.name} Added a link to blacklist",
                                      f"{text} was added to the blacklist for chat moderation. Any text containing this phrase will be deleted.")
            await ctx.send(f"Added {text} to filter!")
        elif option.lower() in ["remove", "delete", "del", "take"]:
            if text.lower() not in BANNED_LINKS:
                return await ctx.send("You can't remove something that doesn't exist!")

            if text.lower() in BANNED_LINKS:
                BANNED_LINKS.remove(text.lower())

                await posts.update_one({"guild_id": ctx.guild.id},
                                       {"$set": {"auto_mod.blacklisted_domains": BANNED_LINKS}})
                await self.send_log_embed(log_channel, f"{ctx.author.name} Removed a link from blacklist",
                                          f"{text} was removed from the blacklist for chat moderation. Any text containing this phrase will not be deleted.")
                await ctx.send(f"Removed {text} from filter!")
            else:
                return await ctx.send("That link isn't added!")
        elif option.lower() in ["list", "total"]:
            description_string = "".join(f"\n{keyword}" for keyword in BANNED_LINKS)

            em = discord.Embed(title="Banned links list", description=description_string, color=855330)
            em.set_footer(text="Ploxy | Chat filter")

            await ctx.send(embed=em)

    @chat.command(name="role", aliases=["roles"], usage="chat role <add|remove|list>")
    @tools.has_perm(manage_guild=True)
    async def role(self, ctx, option, role: discord.Role = None):
        db = self.database.bot
        posts = db.serversettings
        ignore_roles = []
        log_channel = 0

        def has_role():
            return role is None

        async for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            ignore_roles = x["auto_mod"]["ignore_roles"]

        if option.lower() in ["add", "ignore"]:
            if has_role():
                return await ctx.send("You must specify a role!")
            ignore_roles.append(role.id)
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.ignore_roles": ignore_roles}})
            await self.send_log_embed(log_channel, f"{ctx.author.name} Added role to whitelist",
                                      f"{role.mention} was added to the whitelist for chat moderation. They are now able to bypass the auto chat mod.")
            return await ctx.send(f"Added role with id {role.id} to allowed roles!")

        elif option.lower() in ["remove", "del", "delete"]:
            if has_role():
                return await ctx.send("You must specify a role!")
            if role.id in ignore_roles:
                ignore_roles.remove(role.id)
                await posts.update_one({"guild_id": ctx.guild.id},
                                       {"$set": {"auto_mod.ignore_roles": ignore_roles}})
                await self.send_log_embed(log_channel, f"{ctx.author.name} Removed role from whitelist",
                                          f"{role.mention} was removed from the whitelist for chat moderation. Add them back to be able to bypass auto chat mod.")
                return await ctx.send(f"Removed role with id {role.id} from allowed roles!")
            else:
                return await ctx.send("That role isn't added!")
        elif option.lower() in ["list", "total"]:
            description_string = "Currently no one is allowed to bypass this feature!"
            if ignore_roles:
                description_string = ""
            for keyword in ignore_roles:
                description_string = description_string + f"\n{keyword}"

            em = discord.Embed(title="Role bypass list", description=description_string, color=855330)
            em.set_footer(text="Ploxy | Chat filter")

            await ctx.send(embed=em)

    @chat.command(name="invites", aliases=["invite"], usage="chat invites <add|remove|list>")
    @tools.has_perm(manage_messages=True)
    async def invites(self, ctx, option, *, setting=None):
        db = self.database.bot
        posts = db.serversettings
        allowed_invites = []
        log_channel = 0

        def has_invite():
            return setting is None

        async for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            allowed_invites = x["auto_mod"]["allowed_invites"]

        if option.lower() in ["add", "ignore", "allow"]:
            if has_invite():
                return await ctx.send("You must specify an invite!")

            allowed_invites.append(setting.lower())

            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.allowed_invites": allowed_invites}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Added invite to whitelist",
                                      f"{setting} was added to the whitelist for chat moderation. Messages containing this invite will not be deleted!")
            return await ctx.send(f"Added invite with {setting.lower()} to allowed invites!")

        elif option.lower() in ["remove", "del", "delete"]:
            if has_invite():
                return await ctx.send("You must specify an invite!")

            if setting.lower() in allowed_invites:

                allowed_invites.remove(setting.lower())

                await posts.update_one({"guild_id": ctx.guild.id},
                                       {"$set": {"auto_mod.allowed_invites": allowed_invites}})

                await self.send_log_embed(log_channel, f"{ctx.author.name} Removed invite from whitelist",
                                          f"{setting.lower()} was removed from the whitelist for chat moderation. Messages containing this invite will be deleted!")

                return await ctx.send(f"Removed invite {setting.lower()} from allowed invites!")
            else:
                return await ctx.send("That role isn't added!")
        elif option.lower() in ["list", "total"]:
            description_string = "Currently all invites will be deleted!"
            if allowed_invites:
                description_string = ""
            for keyword in allowed_invites:
                description_string = description_string + f"\n{keyword}"

            em = discord.Embed(title="Allowed invite list", description=description_string, color=855330)
            em.set_footer(text="Ploxy | Chat filter")

            await ctx.send(embed=em)
        elif option.lower() in ["enable", "on"]:
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.anti_invite": 1}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Enabled invite detection and removal",
                                      f"Messages containing invites will be deleted!")

            return await ctx.send(f"Allowed invite detection and removal!")
        elif option.lower() in ["disable", "off"]:
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.anti_invite": 0}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Disabled invite detection and removal",
                                      f"Messages containing invites will  not be deleted!")

            return await ctx.send(f"Turned off invite detection and removal!")

    @chat.command(name="mod", aliases=["moderation"], usage="chat mod <enable|disable>")
    @tools.has_perm(manage_messages=True)
    async def mod(self, ctx, option="else"):
        db = self.database.bot
        posts = db.serversettings
        log_channel = 0
        chat_moderation = 0

        async for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            chat_moderation = x["auto_mod"]["chat_moderation"]
        if option.lower() in ["on", "enable", "allow", "engage"]:
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.chat_moderation": 1}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Enabled chat moderation and anti raid",
                                      f"Messages containing banned words, links, excessive emojis and spam will be deleted!")

            await ctx.send(f"Allowed chat moderation and anti raid!")
        elif option.lower() in ["off", "disable", "disengage"]:
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.chat_moderation": 0}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Disabled chat moderation and anti raid",
                                      f"Messages containing banned words, links, excessive emojis and spam will not be deleted!")

            await ctx.send(f"Disallowed chat moderation and anti raid!")
        else:
            if chat_moderation:
                await ctx.send("Chat moderation is on!")
            else:
                await ctx.send("Chat moderation is off!")

    @chat.command(name="mentions", aliases=["mention"], usage="chat mentions <set|reset> <value>")
    @tools.has_perm(manage_messages=True)
    async def mentions(self, ctx, option, value: int):
        db = self.database.bot
        posts = db.serversettings
        log_channel = 0
        max_mentions = 0

        async for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            max_mentions = x["auto_mod"]["max_mentions"]

        if option.lower() in ["set", "add", "limit"]:
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            await ctx.send(
                "Please select a number from this list:\n1. Auto mute\n2. Auto kick\n3.Temp ban\n4. Perm ban")
            msg = await self.bot.wait_for('message', check=check)
            try:
                on_mass_mention = int(msg.content)

            except ValueError:
                return await ctx.send("Please choose a valid number!")
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.max_mentions": value,
                                             "auto_mod.on_mass_mention": on_mass_mention}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Set max mentions to {max_mentions}",
                                      f"Messages containing spam pings will be moderated!")

            await ctx.send(f"Allowed chat moderation and anti raid!")
        elif option.lower() in ["reset", "disable", "stop"]:
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.max_mentions": 0}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Disabled max mentions",
                                      f"Messages containing spam pings will not be moderated!")

            await ctx.send(f"Disallowed chat moderation and anti raid!")

    @chat.command(name="bans", aliases=["ban"], usage="chat bans <set|reset> <minutes>")
    @tools.has_perm(ban_members=True)
    async def bans(self, ctx, option, value: int):
        db = self.database.bot
        posts = db.serversettings
        log_channel = 0
        auto_temp_ban_time = 0

        async for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            auto_temp_ban_time = x["auto_mod"]["auto_temp_ban_time"]

        if option.lower() in ["set", "add", "limit"]:

            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.auto_temp_ban_time": value}})

            await self.send_log_embed(log_channel,
                                      f"{ctx.author.name} Set Auto temp ban time set to {value} from {auto_temp_ban_time}",
                                      f"Users who get temp banned get unbanned after {value} minutes!")

            await ctx.send(f"Set the temp ban time to {value} minutes!")
        elif option.lower() in ["reset", "disable", "stop"]:
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.auto_temp_ban_time": 0}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Disabled temp bans",
                                      f"No one will be banned if they are deemed to be raiding your server!")

            await ctx.send(f"Temp ban time disabled!")

    @chat.command(name="mutes", aliases=["mute"], usage="chat mutes <set|reset> <minutes>")
    @tools.has_perm(manage_messages=True)
    async def mutes(self, ctx, option, value: int):
        db = self.database.bot
        posts = db.serversettings
        log_channel = 0
        auto_mute_time = 0

        async for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            auto_mute_time = x["auto_mod"]["auto_mute_time"]

        if option.lower() in ["set", "add", "limit"]:

            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.auto_mute_time": value}})

            await self.send_log_embed(log_channel,
                                      f"{ctx.author.name} Set Auto mute time set to {auto_mute_time}",
                                      f"Users who get temp banned get un muted after {auto_mute_time} minutes!")

            await ctx.send(f"Allowed auto chat muting!")
        elif option.lower() in ["reset", "disable", "stop"]:
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.auto_mute_time": 0}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Disabled auto mutes",
                                      f"Members will not be muted!")

            await ctx.send(f"Disallowed auto chat muting!")

    @chat.command(name="channel", aliases=["channels"], usage="chat channel <add|remove|list> <#channel>")
    @tools.has_perm(manage_messages=True)
    async def channel(self, ctx, option, value: discord.TextChannel = "all"):
        db = self.database.bot
        posts = db.serversettings
        log_channel = 0
        mod_ignore_channels = []

        async for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            mod_ignore_channels = x["auto_mod"]["mod_ignore_channels"]

        if option.lower() in ["set", "add", "ignore"]:
            mod_ignore_channels.append(value.id)
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.mod_ignore_channels": mod_ignore_channels}})

            await self.send_log_embed(log_channel,
                                      f"{ctx.author.name} Set Auto to spam ignore {value.mention}",
                                      f"Any rule violations won't be stopped in this channel!")

            await ctx.send(f"Disallowed moderation in {value.mention}!")
        elif option.lower() in ["remove", "disable", "stop"]:
            mod_ignore_channels.remove(value.id)
            await posts.update_one({"guild_id": ctx.guild.id},
                                   {"$set": {"auto_mod.mod_ignore_channels": mod_ignore_channels}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Allowed auto moderation in {value.mention}",
                                      f"Any rule violations will be stopped in this channel!")

            await ctx.send(f"Allowed moderation in {value.mention}!")
        else:
            description_string = "You have no ignored channels."
            if mod_ignore_channels:
                description_string = ""
            for channel in mod_ignore_channels:
                f_channel = ctx.guild.get_channel(channel)
                if f_channel:
                    description_string += f"\n{f_channel.mention}"

            em = discord.Embed(title="Ignored channel list", description=description_string, color=855330)
            em.set_footer(text="Ploxy | Chat filter")
            await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Chat(bot))
