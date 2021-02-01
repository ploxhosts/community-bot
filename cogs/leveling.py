import discord
from discord.ext import commands
import math
import datetime
import random
import asyncio


class Levels(commands.Cog):
    """Level related commands"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None:
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        if message.author.bot is True:
            return
        try:
            exp = 0
            level = 0

            # Check if it's allowed
            db = self.database.bot
            posts = db.serversettings
            for x in posts.find({"guild_id": message.guild.id}):
                status = x['levels']["enabled"]
                if status == 0 or status is None:
                    return

            posts = db.player_data

            # Now use a tiny bit of ram

            up = random.randint(1, 4)
            if len(message.content) >= 30:
                up = random.randint(6, 10)

            message_time = datetime.datetime(2019, 8, 20, 11, 14, 22, 453209)
            for x in posts.find({"user_id": message.author.id, "guild_id": message.guild.id}):
                level = x["level"]
                exp = x["exp"]
                message_time = x["message_time"]

            new_message_time = datetime.datetime.utcnow()
            time_difference = round((new_message_time - message_time).total_seconds() / 60)

            if time_difference < 1:  # if it's a minute or less
                return

            exp = exp + up
            posts.update_one({"user_id": message.author.id, "guild_id": message.guild.id},
                             {"$set": {"exp": exp, "message_time": new_message_time}})

            # Do I increase the level?

            xp_start = exp
            lvl_start = level

            xp_end = math.floor(5 * (lvl_start ^ 2) + 50 * lvl_start + 100)

            if xp_end <= xp_start:
                level += 1
                embed = discord.Embed(color=0xffffff)
                embed.add_field(name=f"{message.author}", value=f"Has leveled up to level {level}", inline=True)
                delete_me = await message.channel.send(embed=embed)

                exp = 0
                posts.update_one({"user_id": message.author.id, "guild_id": message.guild.id},
                                 {"$set": {"exp": exp, "level": level}})
                await asyncio.sleep(5)
                await delete_me.delete()
        except Exception:
            pass

    @commands.command(name="level", description="Get the level of yourself or someone else",
                      aliases=["levels"], usage="level")
    async def level(self, ctx, user: discord.User = None):
        exp = 0
        level = 0

        db = self.database.bot
        posts = db.player_data

        if user is None:
            for x in posts.find({"user_id": ctx.author.id, "guild_id": ctx.guild.id}):
                level = x["level"]
                exp = x["exp"]
            embed = discord.Embed(color=0xffffff)
            embed.add_field(name=f"{ctx.author}", value=f"You have {exp} xp and are on level {level}", inline=True)
            return await ctx.send(embed=embed)

        for x in posts.find({"user_id": user.id, "guild_id": ctx.guild.id}):
            level = x["level"]
            exp = x["exp"]
        embed = discord.Embed(color=0xffffff)
        embed.add_field(name=f"{user.name}", value=f"Has {exp} xp and are on level {level}", inline=True)
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True, case_sensitive=False,
                    description="Enable/Disable leveling on your server",
                    aliases=["levelling"], usage="leveling")
    async def leveling(self, ctx):
        embed = discord.Embed(
            title="Leveling help",
            description="This helps you config the leveling system",
            color=0xeee657)
        embed.add_field(
            name="Disable/Enable leveling",
            value="leveling <voice | text> <enable|disable>",
            inline=False)
        await ctx.send(embed=embed)

    @leveling.command(name="text", description="Disable/Enable leveling", usage="leveling text <enable|disable>")
    async def text(self, ctx, choice):
        db = self.database.bot
        posts = db.serversettings
        if choice == "enable":
            posts.update_one({"guild_id": ctx.guild.id}, {"$set": {"levels.enabled": 1}})
            await ctx.send(f"Leveling has been enabled")
        elif choice == "disable":
            posts.update_one({"guild_id": ctx.guild.id}, {"$set": {"levels.enabled": 0}})
            await ctx.send(f"Leveling has been disabled")

    @leveling.command(name="voice", description="Disable/Enable voice chat leveling",
                      usage="leveling voice <enable|disable>")
    async def voice(self, ctx, choice):
        db = self.database.bot
        posts = db.serversettings
        if choice == "enable":
            posts.update_one({"guild_id": ctx.guild.id}, {"$set": {"levels.voice_enabled": 1}})
            await ctx.send(f"Voice leveling has been enabled")
        elif choice == "disable":
            posts.update_one({"guild_id": ctx.guild.id}, {"$set": {"levels.voice_enabled": 0}})
            await ctx.send(f"Voice leveling has been disabled")


def setup(bot):
    bot.add_cog(Levels(bot))
