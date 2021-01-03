import discord
from discord.ext import commands, tasks
import datetime
import asyncio
import time
import random


def generate_flake():
    flake = (int((time.time() - 946702800) * 1000) << 23) + random.SystemRandom().getrandbits(23)
    return flake


class Mod(commands.Cog):
    """Moderation commands like ban/kick"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.command(name="warn", description="Warn someone", usage="warn @user <reason>")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str = None):
        db = self.database.bot
        posts = db.warnings
        if reason is None:
            await ctx.send("Please provide a reason!")
            return
        time_warned = datetime.datetime.now()
        a = 0
        for x in posts.find({"guild_id": ctx.guild.id, "user_id": user.id}):
            a += 1
        a += 1
        warn_id = generate_flake()

        posts.insert_one({"user_id": user.id,
                          "guild_id": ctx.guild.id,
                          "reason": reason,
                          "issuer": ctx.author.id,
                          "time": time_warned.strftime('%c'),
                          "warn_id": warn_id})

        embed = discord.Embed(colour=discord.Colour(0xac6f8f), description=f"You have been warned!")
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.add_field(name="ID:", value=f"{warn_id}", inline=False)
        embed.add_field(name="You now have:", value=f"{a} warnings", inline=True)
        embed.set_footer(text="PloxHost community bot | Moderation")
        await user.send(embed=embed)

        embed = discord.Embed(colour=discord.Colour(0xac6f8f), description=f"{user.mention} has been warned!")
        embed.add_field(name="user ID:", value=f"{user.id}", inline=False)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.add_field(name="ID:", value=f"{warn_id}", inline=False)
        embed.set_footer(text="PloxHost community bot | Moderation")
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.command(name="unwarn", description="Remove a warn someone", usage="unwarn @user <warn number> <reason>")
    @commands.has_permissions(manage_messages=True)
    async def unwarn(self, ctx, user: discord.Member, warn_id, *, reason: str = None):
        db = self.database.bot
        posts = db.warnings
        if reason is None:
            await ctx.send("Please provide a reason!")
            return
        a = -1
        for x in posts.find({"guild_id": ctx.guild.id, "user_id": user.id}):
            a += 1
            warn_id = x["warn_id"]
        posts.delete_one({"warn_id": warn_id})

        embed = discord.Embed(colour=0xac6f8f, description=f"Warning with id {warn_id} has been removed!",
                              icon_url=f"{user.avatar_url}")
        embed.add_field(name="Reason", value=f"{reason}", inline=False)
        embed.add_field(name="You now have:", value=f"{a} warnings", inline=True)
        embed.set_footer(text="PloxHost community bot | Moderation")
        await user.send(embed=embed)
        await ctx.send(f"{user.mention}'s warning {warn_id} has been removed!")
        await ctx.message.delete()

    @commands.command(name="warnings", description="View someone's warnings", usage="warnings @user")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, user: discord.Member):
        db = self.database.bot
        posts = db.warnings
        lista = []
        a = 0
        for x in posts.find({"guild_id": ctx.guild.id, "user_id": user.id}):
            a += 1
            issuer = x['issuer']
            reason = x['reason']
            warn_id = x["warn_id"]
            warner = self.bot.get_user(issuer)
            lista.append(f"{a}. Warned by {warner.name}#{warner.discriminator} for {reason}\n ID: {warn_id}\n")
        x = "\n".join(lista)
        embed = discord.Embed(colour=0xac6f8f, description=f"{user}'s Warning's",
                              icon_url=f"{user.avatar_url}")
        embed.add_field(name="Warnings", value=f"{x}", inline=False)
        embed.set_footer(text="PloxHost community bot | Moderation")
        await ctx.send(embed=embed)

    @commands.command(name="kick", description="Kick someone", usage="kick @user <reason>")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member:discord.Member, *, reason="No reason"):
        db = self.database.bot
        posts = db.warnings
        await member.send(f"You were kicked from {ctx.guild} for {reason}")
        await member.kick(reason=reason)
        await ctx.message.delete()
        warn_id = generate_flake()
        time_warned = datetime.datetime.now()
        posts.insert_one({"user_id": member.id,
                          "guild_id": ctx.guild.id,
                          "reason": f"KICK: {reason}",
                          "issuer": ctx.author.id,
                          "time": time_warned.strftime('%c'),
                          "warn_id": warn_id})
        embed = discord.Embed(colour=0xac6f8f, description=f"{member.display_name} has been kicked!")
        embed.add_field(name="User ID:", value=f"{member.id}", inline=False)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.set_footer(text="PloxHost community bot | Moderation")
        await ctx.send(embed=embed)

    @commands.command(name="ban", description="Ban someone", usage="ban @user <reason>")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason="No reason was provided."):
        db = self.database.bot
        posts = db.warnings
        if ctx.guild.get_member(user.id) is not None:
            embed = discord.Embed(colour=0xac6f8f, description=f"You have been banned")
            embed.add_field(name="Reason", value=f"{reason}", inline=False)
            await user.send(embed=embed)
            await ctx.guild.ban(user=user, reason=reason)
            await ctx.send(f"{user} has been banned for {reason}")
        else:
            await ctx.guild.ban(user=user, reason=reason)
            await ctx.send(f"{user} has been banned for {reason}")
        warn_id = generate_flake()
        time_warned = datetime.datetime.now()
        posts.insert_one({"user_id": user.id,
                          "guild_id": ctx.guild.id,
                          "reason": f"BAN: {reason}",
                          "issuer": ctx.author.id,
                          "time": time_warned.strftime('%c'),
                          "warn_id": warn_id})
        embed = discord.Embed(colour=0xac6f8f, description=f"{user.display_name} has been banned!")
        embed.add_field(name="User ID:", value=f"{user.id}", inline=False)
        embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        embed.set_footer(text="PloxHost community bot | Moderation")
        await ctx.send(embed=embed)

    @commands.command(name="clear", aliases=["purge"], usage="purge <number of messages>")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        deleted_count = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"{len(deleted_count)} messages got deleted")

    @commands.command(name="role", usage="role @user <Role>")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def role(self, ctx, member: discord.Member, role_asked: discord.Role):
        if role_asked in member.roles:
            await member.remove_roles(role_asked, reason='Removed role')
            await ctx.send(f"{ctx.message.author.mention} has removed the role '{role_asked}' from {member.mention}")
        else:
            await member.add_roles(role_asked, reason='Added role')
            await ctx.send(f"{ctx.message.author.mention} has added role to {member.mention}")


def setup(bot):
    bot.add_cog(Mod(bot))
