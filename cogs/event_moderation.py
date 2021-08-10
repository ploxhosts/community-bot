import discord
from discord.ext import commands, tasks
import datetime
import json
import os


class EventsMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database
        self.batch_delete.start()

    @tasks.loop(hours=4.0)
    async def batch_delete(self):
        db = self.database.bot
        posts = db.message_logs
        async for x in posts.find({}):
            deleted = x["deleted"]
            if "deleted_time" in x:
                deleted_time = x["deleted_time"]
                if deleted and not x["reported"]:
                    seconds_diff = (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(deleted_time)).total_seconds()
                    if seconds_diff - 2628000 >= 1: # 2628000 = 1 month
                        await posts.delete_one({"message_id": x["message_id"]})


    async def delete_message(self, message):
        try:
            message = self.bot.fetch_message(message.message_id)
            await message.delete()
            return "Deleted"
        except discord.NotFound:  # Deleted already
            return "None"

    async def check_contents_once(self, message):
        BANNED_WORDS = []

        db = self.database.bot
        posts = db.serversettings

        async for x in posts.find({"guild_id": message.data["guild_id"]}):
            BANNED_WORDS = x["banned_words"]

        for bad_word in BANNED_WORDS:
            if (
                    bad_word in message.data.content.lower()
                    and await self.delete_message(message) == "Deleted"
            ):
                guild = self.bot.get_guild(message.guild["id"])
                channel = guild.get_channel(message.channel["id"])
                await channel.send("A Message was deleted as it contained a banned word.")

    async def send_delete_embed(self, channel, user, author_id, content, mid):
        if channel == 0:
            return
        try:
            embed = discord.Embed(colour=0x36a39f, title=f"Message by {user} deleted")
        except:
            embed = discord.Embed(colour=0x36a39f, title=f"Message deleted")
        embed.add_field(name="Message id:", value=f"\n{mid}", inline=False)
        embed.add_field(name="Author id:", value=f"\n{author_id}", inline=False)
        embed.add_field(name="Message:", value=f"\n{content}", inline=False)
        embed.set_footer(text="Ploxy | Logging and monitoring")
        log_channel = self.bot.get_channel(channel)

        await log_channel.send(embed=embed)

    async def send_edit_embed(self, channel, message, edits):
        if channel == 0:
            return

        history = [f"{count}. " + edit for count, edit in enumerate(edits, start=1)]
        history = '\n'.join(history)

        embed = discord.Embed(colour=0x36a39f,
                              title=f"Message sent by {message.data['author']['username']}#{message.data['author']['discriminator']} was edited")
        embed.add_field(name="Message id:", value=f"\n{message.message_id}", inline=False)
        embed.add_field(name="Author id:", value=f"\n{message.data['author']['id']}", inline=False)
        embed.add_field(name="Message:", value=f"\n{message.data['content']}", inline=False)
        embed.add_field(name="Edit history:", value=f"\n{history}", inline=False)
        embed.set_footer(text="Ploxy | Logging and monitoring")

        log_channel = self.bot.get_channel(channel)

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        if message.author.bot is True:
            return

        JSON = None

        if len(message.embeds) != 0:  # Self bot detection
            JSON = json.dumps((message.embeds[0]).to_dict(), sort_keys=True)
            JSON = json.loads(JSON)

        db = self.database.bot
        posts = db.message_logs
        try:
            await posts.insert_one({
                "message": message.content,  # See the message content
                "json": JSON,  # Get contents of a self bot message
                "edits": [],  # See a nice summary of total changes
                "author_id": message.author.id,  # Identify the author
                "message_id": message.id,  # Identify the message
                "guild_id": message.guild.id,  # Used to delete an entire server/guild from database when removed
                "deleted_time": 0,  # Time message was deleted
                "deleted": False,  # Used for checking if a message has been deleted after it's been reported
                "reported": False,  # Be able to report specific messages
                "mentions": [x.id for x in message.mentions],
                "time_sent": datetime.datetime.utcnow()  # Get a date of time sent was: int(round(time.time() * 1000))
            })
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, message):
        db = self.database.bot
        posts = db.serversettings
        log_channel = 0
        async for x in posts.find({"guild_id": message.guild_id}):
            log_channel = x['log_channel']
        posts = db.message_logs
        reported = False
        JSON = False
        message_content = ""
        author_id = 0
        mentions = []
        async for x in posts.find({"message_id": message.message_id}):
            reported = x["reported"]
            JSON = x["json"]
            message_content = x["message"]
            author_id = x["author_id"]
            try:
                mentions = x["mentions"]
            except:
                pass
        if message_content != "":
            if reported is True or JSON is not None:  # Not if reported or a self bot
                await posts.update_one({"message_id": message.message_id},
                                       {"$set": {"deleted": True, "reported": True,
                                                 "deleted_time": datetime.datetime.utcnow().timestamp()}})
            else:
                await posts.update_one({"message_id": message.message_id},
                                       {"$set": {"deleted": True, "deleted_time": datetime.datetime.utcnow().timestamp()}})
            user = await self.bot.fetch_user(author_id)
            if message.message_id not in self.bot.delete_message_cache:
                if log_channel != 0:
                    await self.send_delete_embed(log_channel, user.name, author_id, message_content, message.message_id)
            else:
                self.bot.delete_message_cache.remove(message.message_id)
            guild = self.bot.get_guild(message.guild_id)
            save_msg = any(
                guild.get_member(member).guild_permissions.manage_messages
                for member in mentions
            )
            if save_msg:
                channel = self.bot.get_channel(message.channel_id)
                embed = discord.Embed(colour=0xac6f8f,
                                      description=f"{user.mention} deleted a message containing a mention!")
                embed.add_field(name="Message content: ", value=f"{message_content}", inline=False)
                embed.set_footer(text="Ploxy | Logging and monitoring")
                await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, message):
        try:
            if "author" in message.data:
                if "bot" in message.data["author"]:
                    return
            else:
                return
        except KeyError:
            return
        if "content" in message.data:
            db = self.database.bot
            posts = db.serversettings

            log_channel = 0

            async for x in posts.find({"guild_id": int(message.data["guild_id"])}):
                log_channel = x['log_channel']

            if log_channel == 0:
                return

            posts = db.message_logs
            edits = []
            async for data in posts.find({"message_id": message.message_id}):
                org_msg = data["message"]
                edits = data["edits"]
                if len(edits) == 0:
                    edits.append(org_msg)
            edits.append(message.data["content"])

            if edits.count(message.data["content"]) == 1:
                await self.check_contents_once(message)
                await posts.update_one({"message_id": message.message_id},
                                       {"$set": {"edits": edits}})

                await self.send_edit_embed(log_channel, message, edits)
        else:
            pass  # Message was pinned/Received embed/Removed embed

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, message):
        db = self.database.bot
        posts = db.serversettings

        log_channel = 0

        async for x in posts.find({"guild_id": message.guild_id}):
            log_channel = x['log_channel']

        posts = db.message_logs
        file_name = str(message.guild_id) + "-" + str(message.channel_id)
        channel_ex = self.bot.get_channel(message.channel_id)
        channel_ex: discord.TextChannel

        use_file = False
        with open(file_name, "w") as file:
            file.write(f"{len(message.message_ids)} messages deleted in #{channel_ex.name}\n")
            for ids in message.message_ids:
                message_content = ""
                reported = False
                JSON = None
                author_id = 0
                async for x in posts.find({"message_id": ids}):
                    reported = x["reported"]
                    JSON = x["json"]
                    message_content = x["message"]
                    author_id = x["author_id"]
                if reported is False and JSON is None:  # Not if reported or a self bot
                    try:
                        await posts.delete_one({"message_id", ids})
                    except:
                        pass
                else:
                    if message_content != "":
                        await posts.update_one({"message_id": ids},
                                               {"$set": {"deleted": True}})
                if message_content != "":
                    user = await self.bot.fetch_user(author_id)
                    user: discord.User
                    file.write(
                        f"{user.name}#{user.discriminator} ({user.id}) said {message_content} ({ids})\n\n")
                    use_file = True
                    # Do something with deleted message
                    # await self.send_delete_embed(log_channel, user.name, author_id, message_content, ids)
        embed = discord.Embed(colour=0x36a39f, title=f"Bulk Message delete")
        embed.add_field(name="Messages purged:", value=f"\n{len(message.message_ids)}", inline=False)
        embed.add_field(name="Channel:", value=f"\n{channel_ex.mention}", inline=False)
        embed.set_footer(text="Ploxy | Logging and monitoring")
        if log_channel == 0:
            return
        log_channel = self.bot.get_channel(log_channel)
        if use_file:
            await log_channel.send(embed=embed, file=discord.File(file_name, filename="log.txt"))
        else:
            await log_channel.send(embed=embed)
        os.remove(file_name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = self.database.bot
        posts = db.serversettings

        log_channel = 0

        async for x in posts.find({"guild_id": member.guild.id}):
            log_channel = x['log_channel']

        embed = discord.Embed(colour=0x36a39f, title=f"{member.name}#{member.discriminator} joined")
        embed.add_field(name="User id:", value=f"\n{member.id}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text="Ploxy | Logging and monitoring")
        if log_channel == 0:
            return
        log_channel = self.bot.get_channel(log_channel)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        db = self.database.bot
        posts = db.serversettings

        log_channel = 0

        async for x in posts.find({"guild_id": member.guild.id}):
            log_channel = x['log_channel']

        embed = discord.Embed(colour=0x36a39f, title=f"{member.name}#{member.discriminator} left")
        embed.add_field(name="User id:", value=f"\n{member.id}", inline=False)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text="Ploxy | Logging and monitoring")

        if log_channel == 0:
            return

        log_channel = self.bot.get_channel(log_channel)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        db = self.database.bot
        posts = db.serversettings

        log_channel = 0

        async for x in posts.find({"guild_id": before.guild.id}):
            log_channel = x['log_channel']

        if before.roles != after.roles:  # role got changed
            diff_roles = ""
            role_changes = list(set(before.roles) - set(after.roles))
            if not role_changes:
                role_changes = list(set(after.roles) - set(before.roles))
            for role in role_changes:
                if role in before.roles:
                    diff_roles += f"\n[**-**] {role.name}"
                else:
                    diff_roles += f"\n[**+**] {role.name}"
            embed = discord.Embed(colour=0x36a39f, title=f"{after.name}#{after.discriminator}'s roles updated")
            embed.add_field(name="User id:", value=f"\n{after.id}", inline=False)
            embed.add_field(name="Role changes:", value=f"\n{diff_roles}", inline=False)

        elif before.display_name != after.display_name:  # nickname got changed
            embed = discord.Embed(colour=0x36a39f, title=f"{after.name}#{after.discriminator} nickname changed")
            embed.add_field(name="User id:", value=f"\n{after.id}", inline=False)
            embed.add_field(name="Nickname changes:",
                            value=f"\n`{before.display_name}` changed to `{after.display_name}`", inline=False)
        else:
            return
        embed.set_footer(text="Ploxy | Logging and monitoring")
        embed.set_thumbnail(url=after.avatar_url)

        if log_channel == 0:
            return

        log_channel = self.bot.get_channel(log_channel)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        db = self.database.bot

        main_posts = db.player_data
        async for guild in main_posts.find({"user_id": before.id}):
            posts = db.serversettings
            log_channel = 0

            async for x in posts.find({"guild_id": guild["guild_id"]}):
                log_channel = x['log_channel']

            if before.avatar_url != after.avatar_url:  # role got changed
                embed = discord.Embed(colour=0x36a39f, title=f"{after.name}#{after.discriminator}'s avatar updated")
                embed.add_field(name="User id:", value=f"\n{after.id}", inline=False)
                embed.add_field(name="Before:", value=f"\n{before.avatar_url}", inline=True)
                embed.add_field(name="After:", value=f"\n{after.avatar_url}", inline=True)
                embed.set_thumbnail(url=after.avatar_url)

            elif before.name != after.name:  # nickname got changed
                embed = discord.Embed(colour=0x36a39f, title=f"{after.name}#{after.discriminator} username changed")
                embed.add_field(name="User id:", value=f"\n{after.id}", inline=False)
                embed.add_field(name="Nickname changes:",
                                value=f"\n`{before.name}` changed to `{after.name}`", inline=False)
            elif before.discriminator != after.discriminator:  # nickname got changed
                embed = discord.Embed(colour=0x36a39f,
                                      title=f"{after.name}#{after.discriminator} discriminator changed")
                embed.add_field(name="User id:", value=f"\n{after.id}", inline=False)
                embed.add_field(name="Nickname changes:",
                                value=f"\n`{after.name}#{before.discriminator}` changed to `{after.name}#{after.discriminator}`",
                                inline=False)
            else:
                return
            embed.set_footer(text="Ploxy | Logging and monitoring")

            if log_channel == 0:
                return
            log_channel = self.bot.get_channel(log_channel)
            await log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(EventsMod(bot))
