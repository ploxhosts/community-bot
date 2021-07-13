import datetime
import math
import json
from discord.ext import commands, tasks


class VLevels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database
        self.check_vc_state.start()
        self.users_in_vc = {}

    @tasks.loop(minutes=1.0)
    async def check_vc_state(self):
        users = [sub_user for sub_user in self.users_in_vc.keys()]
        for user_id in users:
            data = self.users_in_vc[user_id]
            bad_seconds = data["bad_seconds"]
            stream_seconds = data["stream_seconds"]
            video_seconds = data["video_seconds"]
            minus_seconds = data["minus_seconds"]
            guild = self.bot.get_guild(data["guild"])
            if guild is None:
                self.users_in_vc.pop(user_id)
            else:
                member = guild.get_member(int(user_id))
                if member is None or member.voice.channel is None:
                    self.users_in_vc.pop(user_id)
                else:
                    if member.voice.deaf or member.voice.mute or member.voice.self_deaf or member.voice.afk:  # If member is server muted, deafened or deafened by their own choice or in the afk channel
                        self.users_in_vc[user_id]["bad_seconds"] = bad_seconds + 60
                    if member.voice.self_mute:
                        self.users_in_vc[user_id]["minus_seconds"] = minus_seconds + 60
                    if member.voice.self_stream:
                        self.users_in_vc[user_id]["stream_seconds"] = stream_seconds + 60
                    if member.voice.self_video:
                        self.users_in_vc[user_id]["video_seconds"] = video_seconds + 80
        with open('voice_levels.txt', 'w') as outfile:
            json.dump(self.users_in_vc, outfile, indent=4)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot is True:
            return

        exp = 0
        level = 0
        total_exp = 0
        time_since_join_vc = 0
        seconds_in_vc = 0
        multiplier = 1

        # Check if it's allowed
        db = self.database.bot
        posts = db.serversettings

        async for x in posts.find({"guild_id": member.guild.id}):
            status = x["levels"]['voice_enabled']
            if status == 0 or status is None:
                return

        posts = db.player_data

        async for x in posts.find({"user_id": member.id, "guild_id": member.guild.id}):
            level = x["level"]
            exp = x["exp"]
            total_exp = x["total_exp"]
            time_since_join_vc = x["time_since_join_vc"]
            seconds_in_vc = x["seconds_in_vc"]
            multiplier = x["multiplier"]

        if exp == 0:  # Requires at least a message to prevent abuse
            return

        if before.channel is None:  # When a user is joining a vc
            await posts.update_one({"user_id": member.id, "guild_id": member.guild.id},
                                   {"$set": {
                                       "exp": exp,
                                       "latest_vc_channel": after.channel.id,
                                       "time_since_join_vc": datetime.datetime.now()
                                   }})
            self.users_in_vc[str(member.id)] = {"guild": member.guild.id, "latest_vc_channel": after.channel.id,
                                                "time_since_join_vc": datetime.datetime.now().timestamp(),
                                                "bad_seconds": 0, "stream_seconds": 0, "video_seconds": 0,
                                                "minus_seconds": 0}

        elif after.channel is None:  # When a user is leaving a vc
            user_obj = self.users_in_vc.get(str(member.id))
            self.users_in_vc.pop(str(member.id))
            # Calculate the time difference between now and then
            new_seconds_in_vc = datetime.datetime.now().timestamp() - time_since_join_vc.timestamp()

            if new_seconds_in_vc - user_obj["bad_seconds"] > 0:
                if "minus_seconds" in user_obj:
                    exp += int(
                        ((new_seconds_in_vc -
                          (user_obj["bad_seconds"] + (user_obj["minus_seconds"] / 4)) / 60 * 5) * multiplier))  # Multiplier may be a float
                else:
                    exp += int(
                        ((new_seconds_in_vc - user_obj[
                            "bad_seconds"]) / 60 * 5) * multiplier)  # Multiplier may be a float
            if "stream_seconds" in user_obj:
                exp += int(
                    (user_obj["stream_seconds"] / 60 * 3) * multiplier)  # Multiplier may be a float
            if "video_seconds" in user_obj:
                exp += int(
                    (user_obj["stream_seconds"] / 60 * 4) * multiplier)  # Multiplier may be a float

            if total_exp == 0:
                for level_mini_start in range(int(level) + 1):
                    total_exp += math.floor(5 * (level_mini_start ^ 2) + 50 * level_mini_start + 100)

            total_exp += exp
            seconds_in_vc += new_seconds_in_vc - user_obj["bad_seconds"]
            # formula for level up

            xp_conv = exp
            while xp_conv >= 0:
                conv = math.floor(5 * (level ^ 2) + 50 * level + 100)
                if xp_conv < conv:
                    break

                xp_conv -= conv
                level += 1
            await posts.update_one({"user_id": member.id, "guild_id": member.guild.id},
                                   {"$set": {
                                       "exp": xp_conv,
                                       "level": level,
                                       "total_exp": total_exp,
                                       "latest_vc_channel": before.channel.id,
                                       "time_since_join_vc": 0,
                                       "seconds_in_vc": seconds_in_vc
                                   }})

        else:
            await posts.update_one({"user_id": member.id, "guild_id": member.guild.id},
                                   {"$set": {
                                       "latest_vc_channel": after.channel.id
                                   }})


def setup(bot):
    bot.add_cog(VLevels(bot))
