import asyncio

from discord.ext import commands
import discord
import tools


class ReactionRoles(commands.Cog):
    """Commands for setting up roles on a reaction to a message"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.group(name='reactionroles', aliases=["rr", "reactsroles", "reactionrole"], usage="rr")
    @tools.has_perm()
    async def reactionroles(self, ctx):
        pass

    @reactionroles.command(name="create", aliases=["setup"], usage="rr create")
    @tools.has_perm(manage_roles=True)
    async def create(self, ctx):
        embed = discord.Embed(colour=0x36a39f, title="Reaction Role Setup",
                              description="Please send the message link or ID. If you need help refer to [here](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-).")
        embed.set_footer(text="Ploxy | Reaction Roles")
        message = await ctx.send(embed=embed)

        role_dict = {}

        def check(m):
            return m.author == ctx.author and m.channel == message.channel

        message_end = None
        try:
            url_msg = await self.bot.wait_for('message', check=check, timeout=60)
            url_raw = url_msg.content.split("/")

            if len(url_raw) != 7 and not len(url_raw) == 1:
                embed = discord.Embed(colour=0xff0000, title="❌ Reaction Role Setup Failed due to invalid URL!")
                embed.set_footer(text="Ploxy | Reaction Roles")
                return await message.edit(embed=embed)
            if len(url_raw) > 1:
                message_id = int(url_raw[6])
                channel_id = int(url_raw[5])
                channel = ctx.guild.get_channel(channel_id)
                message_end = await channel.fetch_message(id=message_id)
                guild_id = message_end.guild.id
            else:
                message_id = int(url_raw[0])
                for channel in ctx.guild.channels:
                    try:
                        message_end = await channel.fetch_message(id=message_id)
                        break
                    except discord.NotFound:
                        pass
                    except AttributeError:
                        pass
                guild_id = message_end.guild.id
            if guild_id != ctx.guild.id:
                embed = discord.Embed(colour=0xff0000, title="❌ Reaction Role Setup Failed due to invalid URL!")
                embed.set_footer(text="Ploxy | Reaction Roles")
                return await message.edit(embed=embed)
            await url_msg.delete()
            while True:
                embed.description = "Please send an emoji you want people to react to.\nTo finish reaction roles choice type `end`."
                embed.set_footer(text="Ploxy | Reaction Roles")
                await message.edit(embed=embed)
                emoji_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                await emoji_msg.delete()
                if emoji_msg.content.lower() in ["end", "quit", "finish"]:
                    break
                embed.description = f"Please either mention or send the ID of the role you want people to get given for {emoji_msg.content}"
                await message.edit(embed=embed)
                role_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                await role_msg.delete()
                role = role_msg.content.replace("<", "").replace("@", "").replace(">", "").replace("&", "")
                role_dict[emoji_msg.content] = role
            formatted_roles = "\n".join(role_dict)
            embed.description = f"Confirm your choices: ```\n{formatted_roles}```\nIs this what you want?"
            await message.edit(embed=embed)
            await message.add_reaction("✅")
            await message.add_reaction("❌")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["❌", "✅"]

            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

            if str(reaction.emoji) == "❌":
                embed.title = "❌ Reaction Role Setup Cancelled!"
                return await message.edit(embed=embed)
            await message.clear_reactions()
            embed.description = "Completed"
            await message.edit(embed=embed)

            for emoji in role_dict:
                await message_end.add_reaction(emoji)

            db = self.database.bot
            posts = db.reactionroles

            await posts.insert_one({
                "guild_id": message_end.guild.id,
                "message_id": message_end.id,
                "creator_id": ctx.author.id,
                "roles": role_dict
            })
        except asyncio.TimeoutError:
            embed = discord.Embed(colour=0xff0000, title="❌ Reaction Role Setup Failed due to Timeout!")
            embed.set_footer(text="Ploxy | Reaction Roles")
            await message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = payload.emoji
        guild_id = payload.guild_id
        message_id = payload.message_id
        channel_id = payload.channel_id
        member = payload.member
        db = self.database.bot
        posts = db.reactionroles
        data = await posts.find_one({"message_id": message_id})
        if not data:
            return
        role_dict = data["roles"]
        if str(emoji) not in role_dict:
            return
        role_id = role_dict[str(emoji)]
        guild = self.bot.get_guild(guild_id)
        role = guild.get_role(int(role_id))
        await member.add_roles(role, reason="Reaction role")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        emoji = payload.emoji
        guild_id = payload.guild_id
        message_id = payload.message_id
        channel_id = payload.channel_id
        user_id = payload.user_id
        db = self.database.bot
        posts = db.reactionroles
        data = await posts.find_one({"message_id": message_id})
        if not data:
            return
        role_dict = data["roles"]
        if str(emoji) not in role_dict:
            return
        role_id = role_dict[str(emoji)]
        guild = self.bot.get_guild(guild_id)
        member = guild.get_member(user_id)
        role = guild.get_role(int(role_id))
        await member.remove_roles(role, reason="Reaction role")

    @reactionroles.command(name="delete", usage="rr delete <message id>")
    @tools.has_perm(manage_roles=True)
    async def delete(self, ctx, message_id):
        db = self.database.bot
        posts = db.reactionroles
        try:
            message_id = int(message_id)
        except:
            return await ctx.send(f"Get the message_id from `{ctx.prefix}rr list!`")
        await posts.delete_many({"message_id": message_id})
        await ctx.send(f"Deleted reaction roles from {message_id}")

    @reactionroles.command(name="list", usage="rr list")
    @tools.has_perm(manage_roles=True)
    async def list(self, ctx):
        db = self.database.bot
        posts = db.reactionroles
        messages = ""
        async for doc in posts.find({"guild_id": ctx.guild.id}):
            messages += f"\n{doc['message_id']}"
        if messages == "":
            messages = "No reaction roles were setup!"

        embed = discord.Embed(colour=0x36a39f, title="Reaction Role List", description=messages)
        embed.set_footer(text="Ploxy | Reaction Roles")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ReactionRoles(bot))
