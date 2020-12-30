import discord
from discord.ext import commands
import datetime
import time
import json


class EventsMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

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

        for x in posts.find({"guild_id": message.data["guild_id"]}):
            BANNED_WORDS = x["banned_words"]

        for bad_word in BANNED_WORDS:
            if bad_word in message.data.content.lower():
                if await self.delete_message(message) == "Deleted":
                    guild = self.bot.get_guild(message.guild["id"])
                    channel = guild.get_channel(message.channel["id"])
                    await channel.send("A Message was deleted as it contained a banned word.")

    async def send_delete_embed(self, channel, user, author_id, content, mid):
        if channel == 0:
            return
        try:
            embed = discord.Embed(colour=0xac6f8f, title=f"Message by {user} deleted")
        except:
            embed = discord.Embed(colour=0xac6f8f, title=f"Message deleted")
        embed.add_field(name="Message id:", value=f"\n{mid}", inline=False)
        embed.add_field(name="Author id:", value=f"\n{author_id}", inline=False)
        embed.add_field(name="Message:", value=f"\n{content}", inline=False)
        embed.set_footer(text="PloxHost community bot | Logging and monitoring")
        log_channel = self.bot.get_channel(channel)

        await log_channel.send(embed=embed)


    async def send_edit_embed(self, channel, message, edits):
        if channel == 0:
            return
        history = '\n'.join(edits)
        embed = discord.Embed(colour=0xac6f8f,
                              title=f"Message sent by {message.data['author']['username']}#{message.data['author']['discriminator']}  edited")
        embed.add_field(name="Message id:", value=f"\n{message.message_id}", inline=False)
        embed.add_field(name="Author id:", value=f"\n{message.data['author']['id']}", inline=False)
        embed.add_field(name="Message:", value=f"\n{message.data['content']}", inline=False)
        embed.add_field(name="Edit history:", value=f"\n{history}", inline=False)
        embed.set_footer(text="PloxHost community bot | Logging and monitoring")
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
        posts.insert_one({
            "message": message.content,  # See the message content
            "json": JSON,  # Get contents of a self bot message
            "edits": [],  # See a nice summary of total changes
            "author_id": message.author.id,  # Identify the author
            "message_id": message.id,  # Identify the message
            "guild_id": message.guild.id,  # Used to delete an entire server/guild from database when removed
            "deleted": False,  # Used for checking if a message has been deleted after it's been reported
            "reported": False,  # Be able to report specific messages
            "time_sent": int(round(time.time() * 1000))  # Get a date of time sent
        })

    @commands.Cog.listener()
    async def on_raw_message_delete(self, message):
        db = self.database.bot
        posts = db.serversettings
        log_channel = 0
        for x in posts.find({"guild_id": message.guild_id}):
            log_channel = x['log_channel']
        posts = db.message_logs
        reported = False
        JSON = False
        message_content = ""
        author_id = 0
        for x in posts.find({"message_id": message.message_id}):
            reported = x["reported"]
            JSON = x["json"]
            message_content = x["message"]
            author_id = x["author_id"]

        if message_content != "":
            if reported is False and JSON is None:  # Not if reported or a self bot
                try:
                    posts.delete_one({"message_id", message.message_id})
                except:
                    pass
            else:
                posts.update_one({"message_id": message.message_id},
                                 {"$set": {"deleted": True}})
            user = await self.bot.fetch_user(author_id)
            await self.send_delete_embed(log_channel, user.name, author_id, message_content,message.message_id)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, message):
        if "content" in message.data:
            db = self.database.bot
            posts = db.serversettings

            log_channel = 0

            for x in posts.find({"guild_id": int(message.data["guild_id"])}):
                log_channel = x['log_channel']

            posts = db.message_logs
            edits = []
            for data in posts.find({"message_id": message.message_id}):
                org_msg = data["message"]
                edits = data["edits"]
                if len(edits) == 0:
                    edits.append(org_msg)
            edits.append(message.data["content"])

            if edits.count(message.data["content"]) == 1:
                await self.check_contents_once(message)
                posts.update_one({"message_id": message.message_id},
                                 {"$set": {"edits": edits}})
                await self.send_edit_embed(log_channel, message, edits)
        else:
            pass  # Message was pinned/Received embed/Removed embed

    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, message):
        db = self.database.bot
        posts = db.serversettings

        log_channel = 0

        for x in posts.find({"guild_id": message.guild_id}):
            log_channel = x['log_channel']

        posts = db.message_logs
        for ids in message.message_ids:
            message_content = ""
            reported = False
            JSON = None
            author_id = 0
            for x in posts.find({"message_id": ids}):
                reported = x["reported"]
                JSON = x["json"]
                message_content = x["message"]
                author_id = x["author_id"]
            if reported is False and JSON is None:  # Not if reported or a self bot
                try:
                    posts.delete_one({"message_id", ids})
                except:
                    pass
            else:
                if message_content != "":
                    posts.update_one({"message_id": ids},
                                     {"$set": {"deleted": True}})
            if message_content != "":
                user = await self.bot.fetch_user(author_id)
                await self.send_delete_embed(log_channel, user.name, author_id, message_content, ids)


def setup(bot):
    bot.add_cog(EventsMod(bot))
