import random
import re
from urllib.parse import urlparse
import datetime
import discord
from discord.ext import commands


class Chat(commands.Cog):
    """Chat moderation features"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    async def delete_message(self, message):
        try:
            await message.delete()
            return "Deleted"
        except discord.NotFound:  # Deleted already
            return "None"

    async def send_log_embed(self, channel, title, message):
        if channel == 0:
            return

        embed = discord.Embed(colour=0xac6f8f, title=title)
        embed.add_field(name="Message:", value=f"\n{message}", inline=False)
        embed.set_footer(text="PloxHost community bot | Chat Moderation")
        log_channel = self.bot.get_channel(channel)

        await log_channel.send(embed=embed)

    async def check_contents_once(self, message):
        BANNED_WORDS = []

        db = self.database.bot
        posts = db.serversettings

        for x in posts.find({"guild_id": message.guild.id}):
            BANNED_WORDS = x["banned_words"]

        for bad_word in BANNED_WORDS:
            if bad_word in message.content.lower():
                if await self.delete_message(message) == "Deleted":
                    guild = self.bot.get_guild(message.guild.id)
                    channel = guild.get_channel(message.channel.id)
                    await channel.send("A Message was deleted as it contained a banned word.")
        # <(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>

    async def check_contents_both(self, message1, message2):
        message1_date = message1.created_at
        message2_date = message2.created_at

        db = self.database.bot
        posts = db.serversettings
        prefix = "?"
        for x in posts.find({"guild_id": message1.guild.id}):
            prefix = x["prefix"]

        if message2 is None:  # Only message 1 exists so chat filter
            return await self.check_contents_once(message1)
        else:
            await self.check_contents_once(message2)
        if message1.content == message2.content:  # Exactly the same content
            if message1.content.lower() in ["lmao", "lol", "rofl", "rip", "xd",
                                            "lmfao"]:  # Ignore any words like LOL or LMAO as spam as it's normally repeated
                pass
            elif message1.content[0] == prefix:  # ignore anything in a bot channel
                pass
            else:
                if message1_date.second + random.randint(4, 15) >= message2_date.second:
                    if await self.delete_message(message2) == "Deleted":
                        await message2.channel.send("We do not allow duplicate messages")

        if message1.attachments is not None and message2.attachments is not None:  # Could be multiple image
            if len(message1.attachments) == len(message2.attachments) and len(
                    message1.attachments):  # Same amount it is about 2 images
                await self.delete_message(message2)

                # Attachments/images/files
                for attachment1, attachment2 in zip(message1.attachments,
                                                    message2.attachments):  # Loop through each attachment
                    if attachment1.size == attachment2.size or attachment1.filename == attachment2.filename:  # The bytes are the same so the image is 99% the same
                        try:
                            if await self.delete_message(message2) == "Deleted":
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
        for x in posts.find({"guild_id": message.guild.id}):
            chat_moderation = x["chat_moderation"]
            blacklisted_domains = x["blacklisted_domains"]
            anti_invite = x["anti_invite"]
            allowed_invites = x["allowed_invites"]
            log_channel = x["log_channel"]
            ignore_roles = x["ignore_roles"]
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
                    embed = discord.Embed(colour=0xac6f8f, title="Chat moderation")
                    embed.add_field(name="Author:", value=f"\n{message.author}", inline=False)
                    embed.add_field(name="Author ID:", value=f"\n{message.author.id}", inline=False)
                    embed.add_field(name="Message:", value=f"\n{message.content}", inline=False)
                    embed.add_field(name="Message ID:", value=f"\n{message.id}", inline=False)
                    embed.add_field(name="Links:", value=f"\n{','.join(bad_links)}", inline=False)
                    embed.set_footer(text="PloxHost community bot | Chat filter")
                    log_channel = self.bot.get_channel(log_channel)
                    await log_channel.send(embed=embed)
        if chat_moderation == 1:
            await self.check_contents_once(message)

            def check(message2):
                return message2.author == message.author and message2.channel == message.channel

            timeout_time = random.randint(10, 30)
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=timeout_time)
            except Exception:
                return
            await self.check_contents_once(msg)
            await self.check_contents_both(message, msg)

    @commands.group(invoke_without_command=True, case_sensitive=False, name="chat", aliases=["chatsettings"], usage="chat")
    async def chat(self, ctx):
        db = self.database.bot
        posts = db.serversettings
        prefix = "?"
        for x in posts.find({"guild_id": ctx.guild.id}):
            prefix = x['prefix']
        embed = discord.Embed(
            title="Chat moderation help",
            description="This helps you config the chat moderation system",
            color=0xeee657)
        embed.add_field(
            name="Disable/Enable chat mod",
            value=f"{prefix}chat mod <enable|disable>",
            inline=False)
        embed.add_field(
            name="Disable/Enable chat mod",
            value=f"{prefix}chat words  <add|remove|list>",
            inline=False)
        embed.add_field(
            name="Disable/Enable chat mod",
            value=f"{prefix}chat link <add|remove|list>",
            inline=False)
        embed.add_field(
            name="Disable/Enable chat mod",
            value=f"{prefix}chat role <add|remove|list>",
            inline=False)
        embed.add_field(
            name="Disable/Enable chat mod",
            value=f"{prefix}chat invites <add|remove|list>",
            inline=False)
        await ctx.send(embed=embed)

    @chat.command(name="words", aliases=["word", "text"], usage="chat words <add|remove|list>")
    @commands.has_permissions(manage_messages=True)
    async def words(self, ctx, option, *, text=None):
        db = self.database.bot
        posts = db.serversettings
        BANNED_WORDS = []
        for x in posts.find({"guild_id": ctx.guild.id}):
            BANNED_WORDS = x["banned_words"]

        def has_text():
            return text is None

        if option.lower() in ["add", "addition", "insert"]:
            if has_text():
                return await ctx.send("You must specify some word to add to the blacklist!")

            if text.lower() in BANNED_WORDS:
                return await ctx.send("This word already exists!")

            BANNED_WORDS.append(text.lower())

            posts.update_one({"guild_id": ctx.guild.id},
                             {"$set": {"banned_words": BANNED_WORDS}})
            await ctx.send(f"Added {text} to filter!")
        elif option.lower() in ["remove", "delete", "del", "take"]:
            if has_text():
                return await ctx.send("You must specify some word to remove from the blacklist!")

            if text.lower() not in BANNED_WORDS:
                return await ctx.send("You can't remove something that doesn't exist!")

            if text.lower() in BANNED_WORDS:
                BANNED_WORDS.remove(text.lower())

                posts.update_one({"guild_id": ctx.guild.id},
                                 {"$set": {"banned_words": BANNED_WORDS}})

                await ctx.send(f"Removed {text} from filter!")
            else:
                await ctx.send("That phrase doesn't exist!")

        elif option.lower() in ["list", "total"]:
            description_string = ""

            for keyword in BANNED_WORDS:
                description_string = description_string + f"\n{keyword}"

            em = discord.Embed(title="Banned words list", description=description_string, color=855330)
            em.set_footer(text="PloxHost community bot | Chat filter")

            await ctx.send(embed=em)

    @chat.command(name="links", aliases=["link"], usage="chat link <add|remove|list>")
    @commands.has_permissions(manage_messages=True)
    async def links(self, ctx, option, *, text=None):
        db = self.database.bot
        posts = db.serversettings
        BANNED_LINKS = []
        for x in posts.find({"guild_id": ctx.guild.id}):
            BANNED_LINKS = x["blacklisted_domains"]
            log_channel = x["log_channel"]

        if option.lower() in ["add", "addition", "insert"]:
            if text.lower() in BANNED_LINKS:
                return await ctx.send("This domain already exists!")

            BANNED_LINKS.append(text.lower())

            posts.update_one({"guild_id": ctx.guild.id},
                             {"$set": {"blacklisted_domains": BANNED_LINKS}})
            await self.send_log_embed(log_channel, f"{ctx.author.name} Added a link to blacklist",
                                      f"{text} was added to the blacklist for chat moderation. Any text containing this phrase will be deleted.")
            await ctx.send(f"Added {text} to filter!")
        elif option.lower() in ["remove", "delete", "del", "take"]:
            if text.lower() not in BANNED_LINKS:
                return await ctx.send("You can't remove something that doesn't exist!")

            if text.lower() in BANNED_LINKS:
                BANNED_LINKS.remove(text.lower())

                posts.update_one({"guild_id": ctx.guild.id},
                                 {"$set": {"blacklisted_domains": BANNED_LINKS}})
                await self.send_log_embed(log_channel, f"{ctx.author.name} Removed a link from blacklist",
                                          f"{text} was removed from the blacklist for chat moderation. Any text containing this phrase will not be deleted.")
                await ctx.send(f"Removed {text} from filter!")
            else:
                return await ctx.send("That link isn't added!")
        elif option.lower() in ["list", "total"]:
            description_string = ""

            for keyword in BANNED_LINKS:
                description_string = description_string + f"\n{keyword}"

            em = discord.Embed(title="Banned links list", description=description_string, color=855330)
            em.set_footer(text="PloxHost community bot | Chat filter")

            await ctx.send(embed=em)

    @chat.command(name="role", aliases=["roles"], usage="chat role <add|remove|list>")
    @commands.has_permissions(manage_guild=True)
    async def role(self, ctx, option, role: discord.Role = None):
        db = self.database.bot
        posts = db.serversettings
        ignore_roles = []
        log_channel = 0

        def has_role():
            return role is None

        for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            ignore_roles = x["ignore_roles"]

        if option.lower() in ["add", "ignore"]:
            if has_role():
                return await ctx.send("You must specify a role!")
            ignore_roles.append(role.id)
            posts.update_one({"guild_id": ctx.guild.id},
                             {"$set": {"ignore_roles": ignore_roles}})
            await self.send_log_embed(log_channel, f"{ctx.author.name} Added role to whitelist",
                                      f"{role.mention} was added to the whitelist for chat moderation. They are now able to bypass the auto chat mod.")
            return await ctx.send(f"Added role with id {role.id} to allowed roles!")

        elif option.lower() in ["remove", "del", "delete"]:
            if has_role():
                return await ctx.send("You must specify a role!")
            if role.id in ignore_roles:
                ignore_roles.remove(role.id)
                posts.update_one({"guild_id": ctx.guild.id},
                                 {"$set": {"ignore_roles": ignore_roles}})
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
            em.set_footer(text="PloxHost community bot | Chat filter")

            await ctx.send(embed=em)

    @chat.command(name="invites", aliases=["invite"], usage="chat invites <add|remove|list>")
    @commands.has_permissions(manage_guild=True)
    async def invites(self, ctx, option, *, setting=None):
        db = self.database.bot
        posts = db.serversettings
        allowed_invites = []
        log_channel = 0

        def has_invite():
            return setting is None

        for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            allowed_invites = x["allowed_invites"]

        if option.lower() in ["add", "ignore", "allow"]:
            if has_invite():
                return await ctx.send("You must specify an invite!")

            allowed_invites.append(setting.lower())

            posts.update_one({"guild_id": ctx.guild.id},
                             {"$set": {"allowed_invites": allowed_invites}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Added invite to whitelist",
                                      f"{setting} was added to the whitelist for chat moderation. Messages containing this invite will not be deleted!")
            return await ctx.send(f"Added invite with {setting.lower()} to allowed invites!")

        elif option.lower() in ["remove", "del", "delete"]:
            if has_invite():
                return await ctx.send("You must specify an invite!")

            if setting.lower() in allowed_invites:

                allowed_invites.remove(setting.lower())

                posts.update_one({"guild_id": ctx.guild.id},
                                 {"$set": {"allowed_invites": allowed_invites}})

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
            em.set_footer(text="PloxHost community bot | Chat filter")

            await ctx.send(embed=em)
        elif option.lower() in ["enable", "on"]:
            posts.update_one({"guild_id": ctx.guild.id},
                             {"$set": {"anti_invite": 1}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Enabled invite detection and removal",
                                      f"Messages containing invites will be deleted!")

            return await ctx.send(f"Allowed invite detection and removal!")
        elif option.lower() in ["disable", "off"]:
            posts.update_one({"guild_id": ctx.guild.id},
                             {"$set": {"anti_invite": 0}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Disabled invite detection and removal",
                                      f"Messages containing invites will  not be deleted!")

            return await ctx.send(f"Turned off invite detection and removal!")

    @chat.command(name="mod", aliases=["moderation"], usage="chat mod <enable|disable>")
    @commands.has_permissions(manage_guild=True)
    async def mod(self, ctx, option="else"):
        db = self.database.bot
        posts = db.serversettings
        log_channel = 0
        chat_moderation = 0

        for x in posts.find({"guild_id": ctx.guild.id}):
            log_channel = x["log_channel"]
            chat_moderation = x["chat_moderation"]
        if option.lower() in ["on", "enable", "allow", "engage"]:
            posts.update_one({"guild_id": ctx.guild.id},
                             {"$set": {"chat_moderation": 1}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Enabled chat moderation and anti raid",
                                      f"Messages containing banned words, links, excessive emojis and spam will be deleted!")

            await ctx.send(f"Allowed chat moderation and anti raid!")
        elif option.lower() in ["off", "disable", "disengage"]:
            posts.update_one({"guild_id": ctx.guild.id},
                             {"$set": {"chat_moderation": 0}})

            await self.send_log_embed(log_channel, f"{ctx.author.name} Disabled chat moderation and anti raid",
                                      f"Messages containing banned words, links, excessive emojis and spam will not be deleted!")

            await ctx.send(f"Disallowed chat moderation and anti raid!")
        else:
            if chat_moderation:
                await ctx.send("Chat moderation is on!")
            else:
                await ctx.send("Chat moderation is off!")


def setup(bot):
    bot.add_cog(Chat(bot))
