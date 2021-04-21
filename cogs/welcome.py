from discord.ext import commands
import discord
import tools
import aiohttp


class Welcome(commands.Cog):
    """Commands that relate to users"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    async def cog_check(self, ctx):
        return ctx.guild.id in [346715007469355009, 742055439088353341]  # Replace list with people who you trust

    @commands.command(name='welcomechannel', aliases=["wchannel", "welcomchannel", "channelwelcome"], usage="Set the welcome channel",  description="Allow the use of welcome messages")
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



def setup(bot):
    bot.add_cog(Welcome(bot))
