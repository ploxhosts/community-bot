import discord
from discord.ext import commands
import datetime
import asyncio


class CustomCommands(commands.Cog):
    """Here you can make commands yourself"""
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.Cog.listener()
    async def on_message(self, message):

        if isinstance(message.channel, discord.DMChannel):  # Disable usage in dms
            return

        if message.author == self.bot.user:  # stop the bot itself from being registered and want to allow other bots for other purposes
            return

        db = self.database.bot
        posts = db.customcommand
        splitted_content = message.content.split()
        response = ""
        try:
            for x in posts.find({"guild_id": message.guild.id, "command": splitted_content[0]}):
                response = x["content"]
            if response != "":
                await message.channel.send(response)
        except IndexError:
            pass

    @commands.group(invoke_without_command=True, case_sensitive=False, name="customcommand", aliases=["cc"], usage="cc")
    async def customcommand(self, ctx):
        db = self.database.bot
        posts = db.serversettings
        prefix = "?"
        for x in posts.find({"guild_id": ctx.guild.id}):
            prefix = x['prefix']
        embed = discord.Embed(
            title="Custom command help",
            description="This helps you add custom commands",
            color=0xeee657)
        embed.add_field(
            name="Add command",
            value=f"{prefix}cc create !pizza ding dong pizza has arrived",
            inline=False)
        embed.add_field(
            name="Remove command",
            value=f"{prefix}cc remove !pizza",
            inline=False)
        embed.add_field(
            name="List commands",
            value=f"{prefix}cc list",
            inline=False)
        await ctx.send(embed=embed)

    @customcommand.command(name="create", aliases=["make", "set"], usage="cc create !pizza ding dong pizza has arrived")
    @commands.has_permissions(manage_messages=True)
    async def create(self, ctx, command, *, content):
        db = self.database.bot
        posts = db.customcommand

        embed = discord.Embed(colour=0xac6f8f, title="Custom command confirmation")
        embed.add_field(name="Command:", value=f"\n{command}", inline=False)
        embed.add_field(name="Response:", value=f"\n{content}", inline=False)
        embed.set_footer(text="PloxHost community bot | Custom Commands")
        confirm_msg = await ctx.send(embed=embed)

        await confirm_msg.add_reaction("✅")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '✅' and reaction.message == confirm_msg

        try:
            reaction2, user2 = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            return await ctx.send('Cancelled custom command, you took too long!')

        posts.insert_one({"guild_id": ctx.guild.id, "made_by": ctx.author.id, "command": command, "content": content})

        await ctx.send('Added command!')
        await confirm_msg.delete()

    @customcommand.command(name="delete", aliases=["remove"], usage="cc remove !pizza")
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx, command):
        db = self.database.bot
        posts = db.customcommand

        posts.delete_one({"guild_id": ctx.guild.id, "command": command})
        await ctx.send('Deleted command!')

    @customcommand.command(name="list", usage="cc list")
    async def list(self, ctx):
        db = self.database.bot
        posts = db.customcommand

        commands = []
        for x in posts.find({"guild_id": ctx.guild.id}):
            commands.append(x["command"])

        end_list = "\n".join(commands)
        embed = discord.Embed(colour=0xac6f8f)
        embed.add_field(name="Command list", value=f"\n\n{end_list}", inline=False)
        embed.set_footer(text="PloxHost community bot | Custom Commands")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CustomCommands(bot))
