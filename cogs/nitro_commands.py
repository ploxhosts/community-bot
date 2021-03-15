from discord.ext import commands
import discord
import asyncio
import datetime
import time
import random
import tools


# noinspection PyBroadException
class Nitro(commands.Cog):
    """Commands about nitro users"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.group(invoke_without_command=True, name='nitro', usage="nitro")
    async def nitro(self, ctx):
        pass

    @nitro.command(name='list', aliases=["viewlist", "total", "users"],
                   usage="nitro list")
    @tools.has_perm()
    async def list(self, ctx):
        boosters = list(ctx.guild.premium_subscribers)
        user: discord.Member
        users = ["Unfortunately, you don't have any nitro boosters."]
        for user in boosters:
            try:
                if users[0] == "Unfortunately, you don't have any nitro boosters.":
                    users.clear()
            except:
                pass
            seconds = (user.premium_since - datetime.datetime.utcnow()).total_seconds()
            if seconds:
                minutes = round(seconds / 60)
                hours = round(minutes / 60)
                days = round(hours / 24)
                weeks = round(days / 7)
                months = round(weeks / 4.345)
                years = round(months / 12)
                if years > 1:  # years
                    users.append(f"{user.name}#{user.discriminator} boosted for {years} years")
                elif months > 1:  # months
                    users.append(f"{user.name}#{user.discriminator} boosted for {months} months")
                elif weeks > 1:  # weeks
                    users.append(f"{user.name}#{user.discriminator} boosted for {weeks} weeks")
                elif days > 1:  # days
                    users.append(f"{user.name}#{user.discriminator} boosted for {days} days")
                elif hours > 1:  # hours
                    users.append(f"{user.name}#{user.discriminator} boosted for {hours} hours")
                elif minutes > 1:  # minutes
                    users.append(f"{user.name}#{user.discriminator} boosted for {minutes} minutes.")

        embed = discord.Embed(color=0x36a39f, title=f"{len(boosters)} members are boosting the server!", description="\n".join(users))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Nitro(bot))
