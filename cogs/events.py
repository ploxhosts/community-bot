import datetime
import os
import discord
from discord.ext import commands
from tools import check_if_update

default_prefix = os.getenv('prefix')


def get_economy_user(member_id, guild_id):
    return {
        "user_id": member_id,  # Get the user
        "balance": 100,  # Global balance, 1-20% tax per transaction to this, used to transfer funds to other guilds
        "balances": {str(guild_id): 0},  # Balance per guild, starts off with $0
        "cash": {str(guild_id): 10},  # Cash per guild, starts off with $10 per guild
        "stocks": {},
        # Stocks they have bought, other guilds used to buy with the normal balance and determined on activity of that guild. Larger servers have larger stock prices.
        "guilds": [],  # List of guilds they are in
        "multiplier": 0,  # If they bought a multiplier
        "d_lottery_tickets": 0,  # Daily tickets they have
        "w_lottery_tickets": 0,  # Weekly tickets they have
        "m_lottery_tickets": 0,  # Yearly tickets they have
        "latest_update": datetime.datetime.utcnow()  # When the document was last updated with this check.
    }


# Deprecated, now inserted in /cogs/permissions_handler.py
def get_permissions_info(guild):
    return {
        "guild_id": guild.id,
        "perm_nodes": {},
        "bad_perm_nodes": {},
        "channel_perms": {}
    }


def get_server_economy(guild):
    return {
        "guild_id": guild.id,  # The guild id to find the document
        "level": 0,
        # Upgrade a guild, a guild can upgrade this using the guild balance field, stocks increased, max level of upgrades and tax rate increased
        "balance": 1000,  # Balance can be used for advertisement or buy things for the economy using it
        "tax_rate": 5,
        # 5 % by default of transferring funds to their own account away from the server. For example $90 from the server gets converted to personal balance, They end up with $85.5 and the server gets the rest.

        "computer": {
            # The guild's computer system, other guilds can hack another guilds computer system to extract money or to decrease taxes or destroy some weapons
            "firewall": 1,  # How secure it is to attack, higher the more secure
            "antivirus": 1,  # Stops viruses, higher the more secure
            "sdk": 1,  # Breach a firewall, higher the more powerful
            "malware": 1,  # make viruses, the higher the more powerful

        },

        # Weapons used if a guild starts a war with another guild, for example if a country with only sticks and stones was to start a fight with a country with nukes,
        # they would lose all the attackers and some balance. However, upon winning balance from that country gets awarded.
        # A war takes 24 hours to end, the guilds have 12 hours to counter the attack either by a warning or by getting allies.
        # Guilds can ally with other guilds meaning that they can help defend/attack another country. The ally can either set an automatic protection status for all guilds or just a specific one.
        # If not set automatic they have within 24 hours hours to accept a request. Ally's can send troops/weapons to each other
        "weapons": {
            # Here goes any weapons they have and the multiplier. For example having "nukes": 100 will mean 100 * damage of a nuke and a nuke aims to destroy level ups of a guild and so on by reducing money, messing up taxes, lowering levels of power and such.
            "sns": 10  # default sticks and stones for weapons
        },
        "worth": guild.member_count / 100,  # Stock price of the server, to be made more complex in the future. Example 1000 members, would make $10 stock price.
        "latest_update": datetime.datetime.utcnow()  # When the document was last updated with this check.

    }


def get_user_stats(member_id, guild_id):
    return {
        "user_id": member_id,  # user id
        "guild_id": guild_id,  # guild id
        "level": 0,  # the main level
        "exp": 0,  # the exp
        "total_exp": 0,   # calculated based on level and exp and helps determine the level leaderboard
        "multiplier": 1,  # For any boost they buy from the economy system
        "seconds_in_vc": 0,  # Total time spent in vc
        "time_since_join_vc": 0,  # Temporary value for saving vc time
        "latest_vc_channel": 0,  # Check their last channel they were in normally temp
        "message_time": datetime.datetime.utcnow(),  # When they last sent a message, helpful for checking when they were last active and the level system.
        "mod_logs": [],  # If the user has any mod logs inside that guild
        "latest_update": datetime.datetime.utcnow()  # When the document was last updated with this check.
    }


def global_user_profile(member_id):
    return {
        "user_id": member_id,  # user id
        "email": "",  # Alert if something happens/changes <- not marketing related
        "notify_settings": {  # When they should be emailed
            "on_ban": False,  # When a member is banned from the server
            "on_kick": False,  # When a member was kicked from the server
            "on_modify_settings": False,  # When a dashboard setting was modified
            "on_bot_major_update": True,  # When the bot receives an update that requires their action such as res
            "on_admin_abuse": True  # On suspected admin abuse such as when many people get banned/kicked
        },
        "guilds": {},  # web dashboard/ custom permission for web management of a server
        "user_rank": 0,  # premium user or not
        "coins": 0,  # For using for premium
        "verified": False,  # Verification system
        "last_seen": datetime.datetime.utcnow(),  # Last seen date
        "on_website": False,  # Bonus if user is on website
        "github": "",  # Used for contributors
        "additions": 0,  # Used for contributors
        "negations": 0,  # Used for contributors
        "ranks": {"dev": False, "staff": False, "admin": False, "contributor": False},
        # Ability to view pages on the website/cool icon
        "latest_update": datetime.datetime.utcnow()  # When the document was last updated with this check.

    }


def get_server_settings(guild_id):
    return {
        "guild_id": guild_id,
        "prefix": default_prefix,  # Default prefix from env
        "users": {},  # A user_id with an object of permissions they can use
        "level": 0,
        "levels": {
            "enabled": 1,  # Boolean value to allow leveling system to work, default yes
            "voice_enabled": 1,  # Boolean value to allow voice leveling to work, default yes
            "level_ignore_channels": [],
            # Leveling doesn't happen here helpful to disable level up messages in these channels
            "level_ignore_roles": [],  # Roles to not gain exp
        },

        "welcome": {
            "channel": 0,  # Setting up a welcome channel to send embeds/images to
            "code": 0,  # If welcome messages should be sent, default no
        },

        "suggestions": {
            "intake_channel": 0,
            "approved_channel": 0,
            "denied_channel": 0,
        },

        "auto_mod": {
            "chat_moderation": 1,  # If chat moderation is enabled, default yes
            "blacklisted_domains": [],  # Domains that cannot be sent
            "anti_invite": 1,  # If anti discord.gg/invitecode should be removed
            "allowed_invites": [],  # Allowed invites such as discord.gg/python
            "banned_words": [],  # Words to be deleted
            "ignore_roles": [],  # Roles that get ignored from auto moderation
            "mod_ignore_channels": [],
            # Auto moderation and logging ignore this channel helpful for staff chats or similar
            "max_mentions": 0,  # Amount of mentions in a message before getting banned
            "on_mass_mention": 0,  # 0 = Do nothing, 1 = Mute with auto_mute, 2 = kick, 3 = temp_ban, 4 = perm_ban
            "auto_temp_ban_time": 1440,  # Minutes an auto temp ban lasts/ 24 hours

            "max_caps": 0,  # Percent of the message to reject if it has too many capitals
            "spam_prevention": 1,
            # Mutes the person for some time, warns them if they send 5 messages in less than 10 seconds.
            "auto_mute": 1,  # To auto mute on spam
            "auto_mute_time": 30,  # Minutes an auto mute lasts

        },
        "log_channel": 0,  # Where mod logs are sent
        "muted_role_id": 0,  # Muted role id
        "extra_settings": {},
        "latest_update": datetime.datetime.utcnow(),
        "linked_guilds": {},  # guild_id with a parent or child or mutual where bans get transferred
    }


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):  # Update here to remove documents on a guild leave
        query = {"guild_id": guild.id}

        # specify the bot database
        db = self.database.bot

        # get server settings that include prefix and toggles
        posts = db.serversettings
        await posts.delete_one(query)

        posts = db.warnings
        await posts.delete_many({"guild_id": guild.id})

        posts = db.message_logs
        await posts.delete_many({"guild_id": guild.id})

        posts = db.customcommand
        await posts.delete_many({"guild_id": guild.id})

        posts = db.player_data
        await posts.delete_many({"guild_id": guild.id})

    @commands.Cog.listener()
    async def on_member_remove(self, member):  # What happens when a member leaves
        db = self.database.bot
        posts = db.economy
        guilds = []
        async for user in posts.find({"user_id": member.id}):
            guilds = user["guilds"]
        guilds.remove(member.guild.id)
        await posts.update_one({"user_id": member.id},
                               {"$set": {"guilds": guilds}})

    @commands.Cog.listener()
    async def on_member_join(self, member):  # What happens when a member joins
        db = self.database.bot
        posts = db.player_data
        try:
            if await posts.count_documents({"user_id": member.id}) == 0:
                await posts.insert_one(get_user_stats(member.id, member.guild.id))
        except IndexError:
            await posts.insert_one(get_user_stats(member.id, member.guild.id))

        posts = db.economy

        if await posts.count_documents(
                {"user_id": member.id}) > 0:  # Adds a user to the database in case of any downtime
            cash = {}
            guilds = []
            async for user in posts.find({"user_id": member.id}):
                cash = user["cash"]
                guilds = user["guilds"]
            cash[str(member.guild.id)] = 10
            guilds.append(member.guild.id)
            await posts.update_one({"user_id": member.id},
                                   {"$set": {"cash": cash, "guilds": guilds}})
            await check_if_update({"user_id": member.id}, get_economy_user(member.id, member.guild.id), posts)
        else:
            await posts.insert_one(get_economy_user(member.id, member.guild.id))

        posts = db.pending_mutes
        if await posts.find_one({"guild_id": member.guild.id, "user_id": member.id}):
            role = await member.guild.get_role(db.serversettings.find({'guild_id': member.guild.id})["muted_role_id"])
            await member.add_roles(role, reason="Mute evaded")

    @commands.Cog.listener()
    async def on_message(self, message):

        if isinstance(message.channel, discord.DMChannel):  # Disable usage in dms
            return

        if message.author == self.bot.user:  # stop the bot itself from being registered and want to allow other bots for other purposes
            return

        db = self.database.bot

        # SERVER SETTINGS

        posts = db.serversettings

        await check_if_update({"guild_id": message.guild.id}, get_server_settings(message.guild.id), posts)

        posts = db.servereconomy
        await check_if_update({"guild_id": message.guild.id}, get_server_economy(message.guild), posts)

        posts = db.globalusers
        await check_if_update({"user_id": message.author.id}, global_user_profile(message.author.id), posts)

        # posts = db.permissions
        # await check_if_update({"guild_id": message.guild.id}, get_permissions_info(message.guild), posts)

        # PLAYER LEVELING

        posts = db.player_data
        await check_if_update({"user_id": message.author.id, "guild_id": message.guild.id},
                              get_user_stats(message.author.id, message.guild.id), posts)

        # ECONOMY

        posts = db.economy
        if await posts.count_documents(
                {"user_id": message.author.id}) > 0:  # Adds a user to the database in case of any downtime
            cash = {}
            guilds = []
            async for user in posts.find({"user_id": message.author.id}):
                cash = user["cash"]
                guilds = user["guilds"]
            if cash:
                if str(message.guild.id) not in cash.keys():
                    cash[str(message.guild.id)] = 10
                    await posts.update_one({"user_id": message.author.id},
                                           {"$set": {"cash": cash}})
            else:
                await posts.update_one({"user_id": message.author.id},
                                       {"$set": {"cash": {str(message.guild.id): 10}}})
            if message.guild.id not in guilds:
                guilds.append(message.guild.id)
                await posts.update_one({"user_id": message.author.id},
                                       {"$set": {"guilds": guilds}})

            await check_if_update({"user_id": message.author.id},
                                  get_economy_user(message.author.id, message.guild.id),
                                  posts)

        else:
            await posts.insert_one(get_economy_user(message.author.id, message.guild.id))


def setup(bot):
    bot.add_cog(Events(bot))
