import asyncio
import datetime

import discord
from discord.ext import commands, tasks

import tools


# noinspection SpellCheckingInspection
class Mod(commands.Cog):
    """Moderation commands like ban/kick"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database
        self.un_ban.start()
        self.un_mute.start()

    @tasks.loop(seconds=30.0)
    async def un_mute(self):
        db = self.database.bot
        posts = db.pending_mutes
        for user in posts.find({}):
            try:
                user_id = user["user_id"]
                guild_id = user["guild_id"]
                ban_time = user["time"]
                if ban_time is not None:
                    iat = user["issued"]
                    roles = user["roles"]
                    current_time_utc = datetime.datetime.now()
                    change = current_time_utc - iat
                    minutes_change = change.total_seconds() / 60
                    if ban_time - minutes_change <= 0:
                        posts2 = db.serversettings
                        role = posts2.find_one({"guild_id": guild_id})['muted_role_id']
                        guild = self.bot.get_guild(guild_id)
                        role = guild.get_role(role)
                        member = guild.get_member(user_id)
                        await member.remove_roles(role, reason="Muted expired")
                        posts.delete_one({"user_id": user_id, "guild_id": guild_id})
                        for role in roles:
                            try:
                                role_f = guild.get_role(role)
                                await member.add_roles(role_f)
                            except AttributeError:
                                pass
            except AttributeError:
                pass

    @tasks.loop(seconds=30.0)
    async def un_ban(self):
        db = self.database.bot
        posts = db.pending_bans
        for user in posts.find({}):
            user_id = user["user_id"]
            guild_id = user["guild_id"]
            ban_time = user["time"]
            iat = user["issued"]
            current_time_utc = datetime.datetime.now()
            change = current_time_utc - iat
            minutes_change = change.seconds / 60
            if ban_time - minutes_change <= 0:
                guild = self.bot.get_guild(guild_id)
                user = await self.bot.fetch_user(user_id)
                await guild.unban(user, reason="Temp ban expiry")
                posts.delete_one({"user_id": user_id, "guild_id": guild_id})

    @un_ban.before_loop
    async def before_un_ban(self):
        await self.bot.wait_until_ready()

    @un_mute.before_loop
    async def before_un_mute(self):
        await self.bot.wait_until_ready()

    async def send_log_embed(self, channel, title, message):
        if channel == 0:
            return

        embed = discord.Embed(colour=0xac6f8f, title=title)
        embed.add_field(name="Message:", value=f"\n{message}", inline=False)
        embed.set_footer(text="PloxHost community bot | Chat Moderation")
        log_channel = self.bot.get_channel(channel)

        await log_channel.send(embed=embed)

    async def create_muted_role(self, guild):
        db = self.database.bot
        posts = db.serversettings
        role = posts.find_one({"guild_id": guild.id})['muted_role_id']
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
            posts.update_one({"guild_id": guild.id},
                             {"$set": {"muted_role_id": role.id}})
        else:
            role = guild.get_role(role)
        return role

    async def give_muted_role(self, guild, member, user_id, role, duration):
        if role not in member.roles:
            await member.add_roles(role, reason="Muted")
            db = self.database.bot
            posts = db.serversettings
            channel = posts.find_one({"guild_id": guild.id})['log_channel']
            await self.send_log_embed(channel, f"Muted {member.name}#{member.discriminator} for {duration}",
                                      f"Muted {member.display_name} with id of: {user_id}")
            return True
        else:
            return False

    @commands.command(name="mute", description="Mute someone", usage="mute @user <time> <reason>")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, duration="perm"):
        role = await self.create_muted_role(ctx.guild)
        role_list = member.roles
        # noinspection PyTypeChecker
        res = await self.give_muted_role(ctx.guild, member, member.id, role, duration)
        if res:
            await ctx.send(f"Successfully muted {member.name} for {duration}")
            duration_formatted = tools.get_time(duration)
            db = self.database.bot
            posts = db.pending_mutes
            role_list2 = []
            for role_it in role_list:
                if role_it.name != "@everyone":
                    await member.remove_roles(role_it, reason="Muted")
                    role_list2.append(role_it.id)
            posts.insert_one(
                {"guild_id": ctx.guild.id, "user_id": member.id, "time": duration_formatted,
                 "issued": datetime.datetime.now(), "roles": role_list2})
            if duration_formatted is not None and (duration_formatted * 60) < 800:
                await asyncio.sleep(duration_formatted * 60)
                posts.delete_many({"guild_id": ctx.guild.id, "user_id": member.id})
                await member.remove_roles(role, reason="Mute expired")
                for role_it in role_list:
                    if role_it.name != "@everyone":
                        await member.add_roles(role_it, reason="Mute expired")
        else:
            await ctx.send(
                f"Could not mute {member.name}, they may already have the role.\n Try removing their role or resetting the channel permissions.")

    @commands.command(name="unmute", description="Remove a mute from someone", usage="unmute @user")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        role = await self.create_muted_role(ctx.guild)
        db = self.database.bot
        posts = db.pending_mutes
        for user in posts.find({"user_id": member.id, "guild_id": ctx.guild.id}):
            roles = user["roles"]
            await member.remove_roles(role, reason="Muted expired")
            posts.delete_one({"user_id": member.id, "guild_id": ctx.guild.id})
            for role in roles:
                try:
                    role_f = ctx.guild.get_role(role)
                    await member.add_roles(role_f)
                except AttributeError:
                    pass
        await ctx.send(f"Unmuted {member.name}!")

    @commands.command(name="warn", description="Warn someone", usage="warn @user <reason>")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str = None):
        db = self.database.bot
        posts = db.player_data
        logs = []
        if reason is None:
            await ctx.send("Please provide a reason!")
            return
        time_warned = datetime.datetime.now()
        for x in posts.find({"guild_id": ctx.guild.id, "user_id": user.id}):
            logs = x["mod_logs"]

        a = len(logs)
        if not a:
            a = 0
        a += 1
        warn_id = tools.generate_flake()
        logs.append({"type": "WARNED", "warn_id": warn_id, "reason": reason, "issuer": ctx.author.id,
                     "time": time_warned.strftime('%c')})

        posts.update_one({"user_id": user.id, "guild_id": ctx.guild.id},
                         {"$set": {"mod_logs": logs}})
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
    async def unwarn(self, ctx, user: discord.Member, warn_id, *, reason="No reason provided."):
        db = self.database.bot
        posts = db.player_data
        logs = []
        for x in posts.find({"guild_id": ctx.guild.id, "user_id": user.id}):
            logs = x["mod_logs"]
        a = len(logs) - 1

        found = False
        for i, o in enumerate(logs):
            if o.attr == int(warn_id):
                del logs[i]
                found = True
                break
        if found:
            embed = discord.Embed(colour=0xac6f8f, description=f"Warning with id {warn_id} has been removed!",
                                  icon_url=f"{user.avatar_url}")
            embed.add_field(name="Reason", value=f"{reason}", inline=False)
            embed.add_field(name="You now have:", value=f"{a} warnings", inline=True)
            embed.set_footer(text="PloxHost community bot | Moderation")
            await user.send(embed=embed)
            await ctx.send(f"{user.mention}'s warning {warn_id} has been removed!")
            await ctx.message.delete()
        else:
            await ctx.send("That warning could not be found!")

    @commands.command(name="warnings", description="View someone's warnings", usage="warnings @user")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, user: discord.Member):
        db = self.database.bot
        posts = db.player_data
        lista = []
        a = 0
        message = "No warnings found!"
        for x in posts.find({"guild_id": ctx.guild.id, "user_id": user.id}):
            for log in x["mod_logs"]:
                a += 1
                issuer = log['issuer']
                reason = log['reason']
                warn_id = log["warn_id"]
                if issuer != "SYSTEM":
                    warner = self.bot.get_user(issuer)
                    lista.append(
                        f"{a}. Warned by **{warner.name}#{warner.discriminator}** for {reason}\n ID: {warn_id}\n")
                else:
                    lista.append(f"{a}. Warned by **SYSTEM** for {reason}\n ID: {warn_id}\n")
        if lista:
            print("here")
            message = "\n".join(lista)

        embed = discord.Embed(colour=0xac6f8f, description=f"{user}'s Warning's",
                              icon_url=f"{user.avatar_url}")
        embed.add_field(name="Warnings", value=f"{message}", inline=False)
        embed.set_footer(text="PloxHost community bot | Moderation")
        await ctx.send(embed=embed)

    @commands.command(name="kick", description="Kick someone", usage="kick @user <reason>")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason"):
        db = self.database.bot
        posts = db.warnings
        await member.send(f"You were kicked from {ctx.guild} for {reason}")
        await member.kick(reason=reason)
        await ctx.message.delete()
        warn_id = tools.generate_flake()
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
        warn_id = tools.generate_flake()
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
