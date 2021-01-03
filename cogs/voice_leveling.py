import discord
import datetime
import math
from discord.ext import commands, tasks


class VLevels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot is True:
            return

        exp = 0
        level = 0
        time_since_join_vc = 0
        seconds_in_vc = 0
        multiplier = 1

        # Check if it's allowed
        db = self.database.bot
        posts = db.serversettings

        for x in posts.find({"guild_id": member.guild.id}):
            status = x['leveling_code']
            if status == 0 or status is None:
                return

        posts = db.stats

        for x in posts.find({"user_id": member.id, "guild_id": member.guild.id}):
            level = x["level"]
            exp = x["exp"]
            time_since_join_vc = x["time_since_join_vc"]
            seconds_in_vc = x["seconds_in_vc"]
            multiplier = x["multiplier"]

        if exp == 0:  # Requires at least a message to prevent abuse
            return

        if before.channel is None:  # When a user is joining a vc
            posts.update_one({"user_id": member.id, "guild_id": member.guild.id},
                             {"$set": {
                                 "exp": exp,
                                 "latest_vc_channel": after.channel.id,
                                 "time_since_join_vc": datetime.datetime.now()
                             }})

        elif after.channel is None:  # When a user is leaving a vc

            # Calculate the time difference between now and then
            new_seconds_in_vc = datetime.datetime.now().timestamp() - time_since_join_vc.timestamp()

            exp += int((new_seconds_in_vc / 60 * 10) * multiplier)  # Multiplier may be a float

            seconds_in_vc += new_seconds_in_vc

            # formula for level up

            xp_end = math.floor(5 * (level ^ 2) + 50 * level + 100)

            if xp_end <= exp:
                level += 1
                exp = 0

            posts.update_one({"user_id": member.id, "guild_id": member.guild.id},
                             {"$set": {
                                 "exp": exp,
                                 "level": level,
                                 "latest_vc_channel": before.channel.id,
                                 "time_since_join_vc": 0,
                                 "seconds_in_vc": seconds_in_vc
                             }})

        else:
            posts.update_one({"user_id": member.id, "guild_id": member.guild.id},
                             {"$set": {
                                 "latest_vc_channel": after.channel.id
                             }})


def setup(bot):
    bot.add_cog(VLevels(bot))
