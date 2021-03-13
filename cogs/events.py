import datetime

import discord
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    def get_permissions_info(self, guild):
        return {
            "guild_id": guild.id,
            "perm_nodes": {},
            "bad_perm_nodes": {},
            "channel_perms": {}
        }

    def get_economy_user(self, member_id, guild_id):
        return {
            "user_id": member_id,
            "balance": 100,
            "balances": {str(guild_id): 0},
            "cash": {str(guild_id): 10},
            "stocks": {},
            "guilds": [],
            "multiplier": 0,
            "d_lottery_tickets": 0,
            "w_lottery_tickets": 0,
            "m_lottery_tickets": 0,
            "latest_update": datetime.datetime.utcnow()
        }

    def get_server_economy(self, guild):
        return {
            "guild_id": guild.id,
            "level": 0,  # Upgrade a guild for higher taxes
            "balance": 1000,  # Balance can be used for advertisement or buy things for the economy using it
            "tax_rate": 5,  # 5 % by default
            "computer": {
                "firewall": 1,  # How secure it is to attack, higher the more secure
                "antivirus": 1,  # Stops viruses, higher the more secure
                "sdk": 1,  # Breach a firewall, higher the more powerful
                "malware": 1,  # make viruses, the higher the more powerful

            },
            "weapons": {
                # Here goes any weapons they have and the multiplier. For example having "nukes": 100 will mean 100 * damage of a nuke and a nuke aims to destroy level ups of a guild and so on by reducing money, messing up taxes, lowering levels of power and such.
                "sns": 10  # default sticks and stones for weapons
            },
            "worth": guild.member_count / 100,
            "latest_update": datetime.datetime.utcnow()

        }

    def get_user_stats(self, member_id, guild_id):
        return {
            "user_id": member_id,
            "guild_id": guild_id,
            "level": 0,
            "exp": 0,
            "total_exp": 0,
            "multiplier": 1,  # For any boost they buy from the economy system
            "seconds_in_vc": 0,  # Total time spent in vc
            "time_since_join_vc": 0,  # Temporary value for saving vc time
            "latest_vc_channel": 0,  # Check their last channel they were in normally temp
            "message_time": datetime.datetime.utcnow(),
            "mod_logs": [],
            "latest_update": datetime.datetime.utcnow()
        }

    def global_user_profile(self, member_id):
        return {
            "user_id": member_id,
            "email": "",  # Alert if something happens/changes <- not marketing related
            "notify_settings": {
                "on_ban": False,
                "on_kick": False,
                "on_modify_settings": False,
                "on_bot_major_update": True,
                "on_admin_abuse": True
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
            "latest_update": datetime.datetime.utcnow()

        }

    def get_server_settings(self, guild_id):
        return {
            "guild_id": guild_id,
            "prefix": "?",  # Default prefix
            "users": {},
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

    async def check_if_update(self, find, main_document, collection):
        if collection.count_documents(find) > 0:
            fields = {}
            for x in collection.find(find):
                fields = x
            if "latest_update" in fields:
                last_time = fields["latest_update"]
                time_diff = datetime.datetime.utcnow() - last_time
                if time_diff.total_seconds() < 3600:
                    return
            db_dict = main_document
            db_dict["_id"] = 0
            if db_dict.keys() != fields:
                for key, value in db_dict.items():
                    if key not in fields.keys():
                        collection.update_one(find, {"$set": {key: value}})
                    else:
                        try:
                            sub_dict = dict(value)
                            for key2, value2 in sub_dict.items():
                                if key2 not in fields[key].keys():
                                    new_value = value
                                    new_value[key2] = value2
                                    collection.update_one(find,
                                                                {"$set": {key: new_value}})
                            for key2, value2 in fields[key].items():
                                if key2 not in sub_dict.keys():
                                    new_dict = {}
                                    for item in sub_dict:
                                        if item != key2:
                                            new_dict[item] = sub_dict.get(item)
                                    collection.update_one(find, {"$set": {key: new_dict}})
                        except:
                            pass
                for key2, value2 in fields.items():
                    if key2 not in db_dict:
                        collection.update_one(find, {"$unset": {key2: 1}})
        else:
            collection.insert_one(main_document)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):  # Update here to remove documents on a guild leave
        query = {"guild_id": guild.id}

        # specify the bot database
        db = self.database.bot

        # get server settings that include prefix and toggles
        posts = db.serversettings
        posts.delete_one(query)

        posts = db.warnings
        posts.delete_many({"guild_id": guild.id})

        posts = db.message_logs
        posts.delete_many({"guild_id": guild.id})

        posts = db.customcommand
        posts.delete_many({"guild_id": guild.id})

        posts = db.player_data
        posts.delete_many({"guild_id": guild.id})

    @commands.Cog.listener()
    async def on_member_remove(self, member):  # What happens when a member leaves
        db = self.database.bot
        posts = db.economy
        guilds = []
        for user in posts.find({"user_id": member.id}):
            guilds = user["guilds"]
        guilds.remove(member.guild.id)
        posts.update_one({"user_id": member.id},
                         {"$set": {"guilds": guilds}})

    @commands.Cog.listener()
    async def on_member_join(self, member):  # What happens when a member joins
        db = self.database.bot
        posts = db.player_data
        try:
            if posts.find({"user_id": member.id}).count() == 0:
                posts.insert_one(self.get_user_stats(member.id, member.guild.id))
        except IndexError:
            posts.insert_one(self.get_user_stats(member.id, member.guild.id))
        posts = db.economy

        if posts.find({"user_id": member.id}).count() > 0:  # Adds a user to the database in case of any downtime
            cash = {}
            guilds = []
            for user in posts.find({"user_id": member.id}):
                cash = user["cash"]
                guilds = user["guilds"]
            cash[str(member.guild.id)] = 10
            guilds.append(member.guild.id)
            posts.update_one({"user_id": member.id},
                             {"$set": {"cash": cash, "guilds": guilds}})
            await self.check_if_update({"user_id": member.id}, self.get_economy_user(member.id, member.guild.id), posts)
        else:
            posts.insert_one(self.get_economy_user(member.id, member.guild.id))

        posts = db.pending_mutes
        if posts.find_one({"guild_id": member.guild.id, "user_id": member.id}):
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

        await self.check_if_update({"guild_id": message.guild.id}, self.get_server_settings(message.guild.id), posts)

        posts = db.servereconomy
        await self.check_if_update({"guild_id": message.guild.id}, self.get_server_economy(message.guild), posts)

        posts = db.globalusers
        await self.check_if_update({"user_id": message.author.id}, self.global_user_profile(message.author.id), posts)

        posts = db.permissions
        await self.check_if_update({"guild_id": message.guild.id}, self.get_permissions_info(message.guild), posts)

        # PLAYER LEVELING

        posts = db.player_data
        await self.check_if_update({"user_id": message.author.id, "guild_id": message.guild.id},
                                   self.get_user_stats(message.author.id, message.guild.id), posts)

        # ECONOMY

        posts1 = db.economy
        if posts1.find(
                {"user_id": message.author.id}).count() > 0:  # Adds a user to the database in case of any downtime
            cash = {}
            guilds = []
            for user in posts1.find({"user_id": message.author.id}):
                cash = user["cash"]
                guilds = user["guilds"]
            if cash:
                if str(message.guild.id) not in cash.keys():
                    cash[message.guild.id] = 10
                    posts1.update_one({"user_id": message.author.id},
                                      {"$set": {"cash": cash}})
            else:
                posts1.update_one({"user_id": message.author.id},
                                  {"$set": {"cash": {str(message.guild.id): 10}}})
            if message.guild.id not in guilds:
                guilds.append(message.guild.id)
                posts1.update_one({"user_id": message.author.id},
                                  {"$set": {"guilds": guilds}})

            await self.check_if_update({"guild_id": message.guild.id}, self.get_economy_user(message.author.id, message.guild.id),
                                       posts)

        else:
            posts1.insert_one(self.get_economy_user(message.author.id, message.guild.id))


def setup(bot):
    bot.add_cog(Events(bot))
