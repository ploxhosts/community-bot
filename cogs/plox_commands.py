import asyncio
import logging
import os
import re

import aiohttp
import cv2
import discord
import pytesseract
import yaml
from bs4 import BeautifulSoup
from discord.ext import commands

import tools

if os.name == 'nt':
    # noinspection SpellCheckingInspection
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# botflop code to provide timing report analysis

VERSION_REGEX = re.compile(r"\d+\.\d+\.\d+")

TIMINGS_CHECK = None
YAML_ERROR = None
with open("timings_check.yml", 'r', encoding="utf8") as stream:
    try:
        TIMINGS_CHECK = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        logging.info(exc)
        YAML_ERROR = exc


def create_field(option):
    field = {"name": option["name"],
             "value": option["value"]}
    if "prefix" in option:
        field["name"] = option["prefix"] + " " + field["name"]
    if "suffix" in option:
        field["name"] = field["name"] + option["suffix"]
    if "inline" in option:
        field["inline"] = option["inline"]
    return field


# Returns -1 if version A is older than version B
# Returns 0 if version A and B are equivalent
# Returns 1 if version A is newer than version B
def compare_versions(version_a, version_b):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]

    return (normalize(version_a) > normalize(version_b)) - (normalize(version_a) < normalize(version_b))


def eval_field(embed_var, option, option_name, plugins, server_properties, bukkit, spigot, paper, tuinity, purpur):
    dict_of_vars = {"plugins": plugins, "server_properties": server_properties, "bukkit": bukkit, "spigot": spigot,
                    "paper": paper, "tuinity": tuinity, "purpur": purpur}
    try:
        for option_data in option:
            add_to_field = True
            for expression in option_data["expressions"]:
                for config_name, value_ in dict_of_vars.items():
                    if config_name in expression and not value_:
                        add_to_field = False
                        break
                if not add_to_field:
                    break
                try:
                    if not eval(expression):
                        add_to_field = False
                        break
                except ValueError as value_error:
                    add_to_field = False
                    logging.info(value_error)
                    embed_var.add_field(name="❗ Value Error",
                                        value=f'`{value_error}`\nexpression:\n`{expression}`\noption:\n`{option_name}`')
                except TypeError as type_error:
                    add_to_field = False
                    logging.info(type_error)
                    embed_var.add_field(name="❗ Type Error",
                                        value=f'`{type_error}`\nexpression:\n`{expression}`\noption:\n`{option_name}`')
            for config_name, value in dict_of_vars.items():
                if config_name in option_data["value"] and not value:
                    add_to_field = False
                    break
            if add_to_field:
                """ f strings don't like newlines so we replace the newlines with placeholder text before we eval """
                option_data["value"] = eval('f"""' + option_data["value"].replace("\n", "\\|n\\") + '"""').replace(
                    "\\|n\\", "\n")
                embed_var.add_field(**create_field({**{"name": option_name}, **option_data}))
                break

    except KeyError as key:
        logging.info("Missing: " + str(key))


def check_trigger_message(trigger_check, message_raw):
    for trigger in trigger_check:
        if trigger.lower() in message_raw.lower():
            return trigger


class Support(commands.Cog):
    """Commands that are designed to be used in the main PloxHost server."""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    async def analyze_timings(self, message):
        timings_url = ""
        spigot = False
        for word in message.content.replace("\n", " ").split(" "):
            if word.startswith("https://timin") and "/d=" in word:
                word.replace("/d=", "/?id=")
            if word.startswith("https://timin") and "/?id=" in word:
                timings_url = word
                break
            if word.startswith("https://www.spigotmc.org/go/timings?url=") or word.startswith(
                    "https://timings.spigotmc.org/?url="):
                spigot = True

        embed_var = discord.Embed(title="Timings Analysis",
                                  url=timings_url,
                                  description="These are not magic values. Many of these settings have real consequences on your server's mechanics. See [YouHaveTrouble's guide](https://github.com/YouHaveTrouble/minecraft-optimization/blob/main/README.md) for detailed information on the functionality of each setting. Many of these settings require the use of an ftp client, you can look at setting one up [here](https://support.plox.host/en/knowledgebase/article/how-to-use-ftp).")
        embed_var.set_footer(text=f"Requested by {message.author.name}#{message.author.discriminator}",
                             icon_url=message.author.avatar_url)
        if spigot:
            embed_var.add_field(name="❌ Spigot",
                                value="Spigot timings have limited information. Switch to [Purpur](https://purpur.pl3x.net/downloads) for better timings analysis. All your plugins will be compatible, and if you don't like it, you can easily switch back. Refer to [this article](https://support.plox.host/en/knowledgebase/article/choosing-a-server-version) if you need help adding the plugin.")
            return await message.reply(embed=embed_var)
        if "?id=" not in timings_url and timings_url == "":
            return

        if "#" in timings_url:
            timings_url = timings_url.split("#")[0]

        timings_host, timings_id = timings_url.split("?id=")
        timings_json = timings_host + "data.php?id=" + timings_id
        timings_url_raw = timings_url + "&raw=1"

        async with aiohttp.ClientSession() as session:
            async with session.get(timings_url_raw) as response:
                request_raw = await response.json(content_type=None)
            async with session.get(timings_json) as response:
                request = await response.json(content_type=None)
        if request is None or request_raw is None:
            embed_var.add_field(name="❌ Invalid report",
                                value="Create a new timings report.")
            await message.reply(embed=embed_var)
            return

        try:
            try:
                version = request["timingsMaster"]["version"] if "version" in request["timingsMaster"] else None
                if "version" in TIMINGS_CHECK and version:
                    version_result = VERSION_REGEX.search(version)
                    version_result = version_result.group() if version_result else None
                    if version_result:
                        if compare_versions(version_result, TIMINGS_CHECK["version"]) == -1:
                            version = version.replace("git-", "").replace("MC: ", "")
                            embed_var.add_field(name="❌ Outdated",
                                                value=f'You are using `{version}`. Update to `{TIMINGS_CHECK["version"]}`.')
                    else:
                        embed_var.add_field(name="❗ Value Error",
                                            value=f'Could not locate version from `{version}`')
                if "servers" in TIMINGS_CHECK:
                    for server in TIMINGS_CHECK["servers"]:
                        if server["name"] in version:
                            embed_var.add_field(**create_field(server))
                            break
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                timing_cost = int(request["timingsMaster"]["system"]["timingcost"])
                if timing_cost > 300:
                    embed_var.add_field(name="❌ Timingcost",
                                        value=f"Your timingcost is {timing_cost}. Your cpu is overloaded and/or slow. Try an [extreme plan](https://plox.host/extreme-hosting).")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                jvm_version = request["timingsMaster"]["system"]["jvmversion"]
                if jvm_version.startswith("1.8.") or jvm_version.startswith("9.") or jvm_version.startswith("10."):
                    embed_var.add_field(name="❌ Java Version",
                                        value=f"You are using Java {jvm_version}. Update to [Java 11](https://support.plox.host/en/knowledgebase/article/change-java-version).")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                flags = request["timingsMaster"]["system"]["flags"]
                if "-XX:+UseZGC" in flags:
                    jvm_version = request["timingsMaster"]["system"]["jvmversion"]
                    java_version = jvm_version.split(".")[0]
                    if int(java_version) < 14:
                        embed_var.add_field(name="❌ Java " + java_version,
                                            value="ZGC should only be used on Java 15.")
                    if "-Xmx" in flags:
                        max_mem = 0
                        flag_list = flags.split(" ")
                        for flag in flag_list:
                            if flag.startswith("-Xmx"):
                                max_mem = flag.split("-Xmx")[1]
                                max_mem = max_mem.replace("G", "000")
                                max_mem = max_mem.replace("M", "")
                                max_mem = max_mem.replace("g", "000")
                                max_mem = max_mem.replace("m", "")
                                if int(max_mem) < 10000:
                                    embed_var.add_field(name="❌ Low Memory",
                                                        value="ZGC is only good with a lot of memory.")
                elif "-Daikars.new.flags=true" in flags:
                    if "-XX:+PerfDisableSharedMem" not in flags:
                        embed_var.add_field(name="❌ Outdated Flags",
                                            value="Add `-XX:+PerfDisableSharedMem` to flags.")
                    if "XX:G1MixedGCCountTarget=4" not in flags:
                        embed_var.add_field(name="❌ Outdated Flags",
                                            value="Add `-XX:G1MixedGCCountTarget=4` to flags.")
                    jvm_version = request["timingsMaster"]["system"]["jvmversion"]
                    if "-XX:+UseG1GC" not in flags and jvm_version.startswith("1.8."):
                        embed_var.add_field(name="❌ Aikar's Flags",
                                            value="You must use G1GC when using Aikar's flags.")
                    if "-Xmx" in flags:
                        max_mem = 0
                        flag_list = flags.split(" ")
                        for flag in flag_list:
                            if flag.startswith("-Xmx"):
                                max_mem = flag.split("-Xmx")[1]
                                max_mem = max_mem.replace("G", "000")
                                max_mem = max_mem.replace("M", "")
                                max_mem = max_mem.replace("g", "000")
                                max_mem = max_mem.replace("m", "")
                        if int(max_mem) < 5400:
                            embed_var.add_field(name="❌ Low Memory",
                                                value="Allocate at least 6-10GB of ram to your server if you can "
                                                      "afford it. Use the code `MEGAMC` to save 33%.")
                        max_online_players = 0
                        for index in range(len(request["timingsMaster"]["data"])):
                            timed_ticks = request["timingsMaster"]["data"][index]["minuteReports"][0]["ticks"][
                                "timedTicks"]
                            player_ticks = request["timingsMaster"]["data"][index]["minuteReports"][0]["ticks"][
                                "playerTicks"]
                            players = (player_ticks / timed_ticks)
                            max_online_players = max(players, max_online_players)
                        if 1000 * max_online_players / int(max_mem) > 6 and int(max_mem) < 10000:
                            embed_var.add_field(name="❌ Low memory",
                                                value="You should be using more RAM with this many players.")
                elif "-Dusing.aikars.flags=mcflags.emc.gs" in flags:
                    embed_var.add_field(name="❌ Outdated Flags",
                                        value="Update [Aikar's flags](https://support.plox.host/en/knowledgebase"
                                              "/article/enabling-aikars-flagsjvm-modifications).")
                else:
                    embed_var.add_field(name="❌ Aikar's Flags",
                                        value="Use [Aikar's flags](https://support.plox.host/en/knowledgebase/article"
                                              "/enabling-aikars-flagsjvm-modifications).")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                cpu = int(request["timingsMaster"]["system"]["cpu"])
                if cpu == 1:
                    embed_var.add_field(name="❌ Threads",
                                        value=f"You have only {cpu} thread. Try an [extreme plan]("
                                              f"https://plox.host/extreme-hosting).")
                elif cpu == 2:
                    embed_var.add_field(name="❌ Threads",
                                        value=f"You have only {cpu} threads. Try an [extreme plan]("
                                              f"https://plox.host/extreme-hosting).")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                handlers = request_raw["idmap"]["handlers"]
                for handler in handlers:
                    handler_name = request_raw["idmap"]["handlers"][handler][1]
                    if handler_name.startswith("Command Function - ") and handler_name.endswith(":tick"):
                        handler_name = handler_name.split("Command Function - ")[1].split(":tick")[0]
                        embed_var.add_field(name=f"❌ {handler_name}",
                                            value=f"This datapack uses command functions which are laggy.")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            plugins = request["timingsMaster"]["plugins"] if "plugins" in request["timingsMaster"] else None
            server_properties = request["timingsMaster"]["config"]["server.properties"] if "server.properties" in \
                                                                                           request["timingsMaster"][
                                                                                               "config"] else None
            bukkit = request["timingsMaster"]["config"]["bukkit"] if "bukkit" in request["timingsMaster"][
                "config"] else None
            spigot = request["timingsMaster"]["config"]["spigot"] if "spigot" in request["timingsMaster"][
                "config"] else None
            paper = request["timingsMaster"]["config"]["paper"] if "paper" in request["timingsMaster"][
                "config"] else None
            tuinity = request["timingsMaster"]["config"]["tuinity"] if "tuinity" in request["timingsMaster"][
                "config"] else None
            purpur = request["timingsMaster"]["config"]["purpur"] if "purpur" in request["timingsMaster"][
                "config"] else None
            if not YAML_ERROR:
                if "plugins" in TIMINGS_CHECK:
                    for server_name in TIMINGS_CHECK["plugins"]:
                        if server_name in request["timingsMaster"]["config"]:
                            for plugin in plugins:
                                for plugin_name in TIMINGS_CHECK["plugins"][server_name]:
                                    if plugin == plugin_name:
                                        stored_plugin = TIMINGS_CHECK["plugins"][server_name][plugin_name]
                                        if isinstance(stored_plugin, dict):
                                            stored_plugin["name"] = plugin_name
                                            embed_var.add_field(**create_field(stored_plugin))
                                        else:
                                            eval_field(embed_var, stored_plugin, plugin_name, plugins,
                                                       server_properties, bukkit, spigot, paper, tuinity, purpur)
                if "config" in TIMINGS_CHECK:
                    for config_name in TIMINGS_CHECK["config"]:
                        config = TIMINGS_CHECK["config"][config_name]
                        for option_name in config:
                            option = config[option_name]
                            eval_field(embed_var, option, option_name, plugins, server_properties, bukkit,
                                       spigot, paper, tuinity, purpur)
            else:
                embed_var.add_field(name="Error loading YAML file",
                                    value=str(YAML_ERROR))

            try:
                for plugin in plugins:
                    authors = request["timingsMaster"]["plugins"][plugin]["authors"]
                    if authors is not None and "songoda" in request["timingsMaster"]["plugins"][plugin][
                        "authors"].casefold():
                        if plugin == "EpicHeads":
                            embed_var.add_field(name="❌ EpicHeads",
                                                value="This plugin was made by Songoda. Songoda is sketchy. You "
                                                      "should find an alternative such as [HeadsPlus]("
                                                      "https://spigotmc.org/resources/headsplus-»-1-8-1-16-4.40265/) "
                                                      "or [HeadDatabase]("
                                                      "https://www.spigotmc.org/resources/head-database.14280/).")
                        elif plugin == "UltimateStacker":
                            embed_var.add_field(name="❌ UltimateStacker",
                                                value="Stacking plugins actually causes more lag. "
                                                      "Remove UltimateStacker.")
                        else:
                            embed_var.add_field(name="❌ " + plugin,
                                                value="This plugin was made by Songoda. Songoda is sketchy. You "
                                                      "should find an alternative.")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                using_tweaks = "ViewDistanceTweaks" in plugins
                if not using_tweaks:
                    worlds = request_raw["worlds"]
                    for world in worlds:
                        tvd = int(request_raw["worlds"][world]["ticking-distance"])
                        ntvd = int(request_raw["worlds"][world]["notick-viewdistance"])
                        if ntvd <= tvd and tvd >= 5:
                            if spigot["world-settings"]["default"]["view-distance"] == "default":
                                embed_var.add_field(name="❌ no-tick-view-distance",
                                                    value=f"Set in paper.yml. Recommended: {tvd}. "
                                                          f"And reduce view-distance from default ({tvd}) in "
                                                          f"spigot.yml. Recommended: 4.")
                            else:
                                embed_var.add_field(name="❌ no-tick-view-distance",
                                                    value=f"Set in paper.yml. Recommended: {tvd}. "
                                                          f"And reduce view-distance from {tvd} in spigot.yml. "
                                                          f"Recommended: 4.")
                            break
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                worlds = request_raw["worlds"]
                high_mec = False
                for world in worlds:
                    max_entity_cramming = int(request_raw["worlds"][world]["gamerules"]["maxEntityCramming"])
                    if max_entity_cramming >= 24:
                        high_mec = True
                if high_mec:
                    embed_var.add_field(name="❌ maxEntityCramming",
                                        value=f"Decrease this by running the /gamerule command in each world. "
                                              f"Recommended: 8. ")
            except KeyError as key:
                logging.info("Missing: " + str(key))

            try:
                normal_ticks = request["timingsMaster"]["data"][0]["totalTicks"]
                worst_tps = 20
                for index in range(len(request["timingsMaster"]["data"])):
                    total_ticks = request["timingsMaster"]["data"][index]["totalTicks"]
                    if total_ticks == normal_ticks:
                        end_time = request["timingsMaster"]["data"][index]["end"]
                        start_time = request["timingsMaster"]["data"][index]["start"]
                        tps = total_ticks / (end_time - start_time)
                        if tps < worst_tps:
                            worst_tps = tps
                if worst_tps < 10:
                    red = 255
                    green = int(255 * (0.1 * worst_tps))
                else:
                    red = int(255 * (-0.1 * worst_tps + 2))
                    green = 255
                color = int(red * 256 * 256 + green * 256)
                # noinspection PyDunderSlots,PyUnresolvedReferences
                embed_var.color = color
            except KeyError as key:
                logging.info("Missing: " + str(key))

        except ValueError as value_error:
            logging.info(value_error)
            embed_var.add_field(name="❗ Value Error",
                                value=str(value_error))

        if len(embed_var.fields) == 0:
            embed_var.add_field(name="✅ All good",
                                value="Analyzed with no recommendations")
            await message.reply(embed=embed_var)
            return

        issue_count = len(embed_var.fields)
        field_at_index = 24
        if issue_count >= 25:
            embed_var.insert_field_at(index=24, name=f"Plus {issue_count - 24} more recommendations",
                                      value="Create a new timings report after resolving some of the above issues to "
                                            "see more.")
        while len(embed_var) > 6000:
            embed_var.insert_field_at(index=field_at_index,
                                      name=f"Plus {issue_count - field_at_index} more recommendations",
                                      value="Create a new timings report after resolving some of the above issues to "
                                            "see more.")
            del embed_var._fields[(field_at_index + 1):]
            field_at_index -= 1
        await message.reply(embed=embed_var)

    @commands.group(name='support', aliases=["spprt"], usage="support",
                    description="Access the support settings")
    @tools.has_perm()
    async def support(self, ctx):
        pass

    @support.command(name='allow', aliases=["enable"], usage="support allow",
                     description="Allows the use of support commands and features such as auto support and knowledge "
                                 "base search")
    @tools.has_perm(manage_messages=True)
    async def allow(self, ctx):
        db = self.database
        posts = db.serversettings
        await posts.update_one({"guild_id": ctx.guild.id},
                               {"$set": {"support": True}})
        await ctx.send("Allowed the use of support services in this server.")

    @support.command(name='deny', aliases=["disable"], usage="support deny",
                     description="Denies the use of support commands and features such as auto support and knowledge "
                                 "base search")
    @tools.has_perm(manage_messages=True)
    async def deny(self, ctx):
        db = self.database
        posts = db.serversettings
        await posts.update_one({"guild_id": ctx.guild.id},
                               {"$set": {"support": False}})
        await ctx.send("Allowed the use of support services in this server.")

    @commands.Cog.listener()
    async def on_message(self, message):
        attachments = message.attachments
        loop = asyncio.get_event_loop()
        support_message_needed = message.content
        if message.author.bot:
            return
        if message.guild.id not in [346715007469355009, 742055439088353341]:
            return

        for attachment in attachments:
            if any(attachment.filename.lower().endswith(image) for image in ["jpeg", "png", "gif", "jpg"]):
                try:
                    await attachment.save(attachment.filename)
                    img = cv2.imread(attachment.filename)
                    result = await loop.run_in_executor(None, pytesseract.image_to_string, img)
                    support_message_needed += f"\n {result}"
                    os.remove(attachment.filename)
                except:
                    os.remove(attachment.filename)
            elif any(attachment.filename.lower().endswith(image) for image in ["txt", "log"]):
                content = await attachment.read()
                support_message_needed += f"\n {content}"

        support_messages = {
            "modulenotfound": {
                "triggers": ["modulenotfoundrror: no module named", "modulenotfoundrror", "no module named",
                             "cannot be found"],
                "prevents": ["you get this", "get this", "-s"],
                "response": "Oh no, sorry to hear that you are having issues with your discord bot hosting.\nThis is "
                            "quite easy to fix with a `requirements.txt` file. Make sure your file is in the main "
                            "folder/directory.\n\nYou will need to insert the module/thing you normally install with "
                            "pip. For example discord.py you could use a `requirements.txt` file with the content of "
                            "\n```\ndiscord.py\ndnspython\nmotor\n```\nDo note some modules are installed into python "
                            "by default such as `random` and `os` so if it says `No matching distribution found "
                            "for...` then likely this is preinstalled into python.\n**Hope this helps you!** "
            },
            "requirements.txt": {
                "triggers": ["no such file or directory", "requirements.txt",
                             "defaulting to user installation because normal site-packages is not writeable"],
                "prevents": ["make sure", "include", "put", "keep", "-s"],
                "response": "Oh no, sorry to hear that you are having issues with your discord bot hosting.\nThis is "
                            "quite easy to fix with a `requirements.txt` file. Make sure your file is in the main "
                            "folder/directory.\n\nYou will need to insert the module/thing you normally install with "
                            "pip. For example discord.py you could use a `requirements.txt` file with the content of "
                            "\n```\ndiscord.py\ndnspython\nmotor\n```\nDo note some modules are installed into python "
                            "by default such as `random` and `os` so if it says `No matching distribution found "
                            "for...` then likely this is preinstalled into python.\n**Hope this helps you!** "
            },
            "ipbanned": {
                "triggers": ["ip has been banned", "ip banned",
                             "banned from support", "i got ip banned"],
                "prevents": ["how to", "minecraft", "-s"],
                "response": "You have been banned by the looks of it. This usually happens when you input the wrong "
                            "email/password multiple times. You can try to login from https://billing.plox.host and "
                            "login with your billing account details(the ones you used to purchase the "
                            "service/server). You can create a ticket there or access the support panel from "
                            "there.\n**Hope this helps you!** "
            },
            "jarfileaccess": {
                "triggers": ["Unable to access jarfile"],
                "prevents": ["how to", "-s"],
                "response": "Ah yes the famous jarfile issues, make sure the file jar file is in the main/root folder "
                            "and execute it. It won't work otherwise. \n If using minecraft hosting, if you are using "
                            "a custom jar then refer to this guide: "
                            "https://support.plox.host/en/knowledgebase/article/how-to-use-a-custom-jar.\n**Hope this "
                            "helps!** "
            },
            "npminstall": {
                "triggers": ["npm package", "packages", "install an npm package", "npm's", "npms", "npm install"],
                "prevents": ["minecraft", "python", "pip", "-s"],
                "response": "Pst, pst. You. The solution is within this article "
                            "https://support.plox.host/en/knowledgebase/article/how-to-setup-your-nodejs-discord-bot. "
                            "It may be recommended to install this on your own computer using `npm install` then "
                            "transfer the `package.json` over. "
            },
            "lagfix": {
                "triggers": ["lagging alot", "laggin alot", "lags alot"],
                "prevents": ["vps", "js", "css", "-s"],
                "response": "The time has come, for you to learn. You should be using Paper or a fork of it such as "
                            "Purpur.\nYes this does enable you to use plugins but comes with performance "
                            "benefits.\n\nYou can select this by using the jar selection on the main multicraft panel "
                            "of your server.Make sure you click save at the bottom and restart. **Make sure you "
                            "install the correction version**, Minecraft will only let you install a version higher "
                            "or the same version to avoid world corruption unless you want your world to be "
                            "deleted.\n\nFor optimised configuration files please visit: "
                            "https://discord.com/channels/346715007469355009/476634353808441344/831237483278237707 "
            },
            "needticket": {
                "triggers": ["how to create a ticket", "the ticket link", "ticket link", "create a ticket"],
                "prevents": ["you can", "support.plox.host", "-s"],
                "response": "You can create a ticket at https://support.plox.host/"
            },
            "nodecmds": {
                "triggers": ["command terminal", "run npm commands", "npm audit"],
                "prevents": ["you can", "you should", "-s"],
                "response": "You can create a ticket at https://support.plox.host/ to have commands ran on your "
                            "discord bot hosting service.\nThis is because Pterodactyl does not support the use of "
                            "such commands in the terminal. "
            }
        }

        trigger = None
        prevent = None
        response = None
        category = None

        for category_s, main_value in support_messages.items():
            for sub_category_s, value in main_value.items():
                category = category_s

                data_trigger = check_trigger_message(main_value["triggers"], support_message_needed)
                data_prevents = check_trigger_message(main_value["prevents"], support_message_needed)
                if data_trigger and data_prevents is None:
                    response = main_value["response"]
                    await message.channel.send(response)
                    break

        await self.analyze_timings(message)

        if message.guild.id == 346715007469355009:  # Log the output to a channel if in the main server
            if trigger or prevent:
                fluxed_logs = message.guild.get_channel(824417561735200838)
                await fluxed_logs.send(
                    f"**Category**: {category}\n**Trigger:** {trigger}\n**Message that prevented it:** {prevent}\nMessage that generated it: \n```\n{message.content}\n```\n**Output:**\n{response}\n**Attachments:** {message.attachments}")


    @commands.command(name='book', aliases=["rtfm"], usage="book How to delete server files",
                      description="search the knowledge base")
    @tools.has_perm()
    async def book(self, ctx, *, search):
        csrf_token = None
        async with aiohttp.ClientSession() as session:
            async with session.get("https://support.plox.host/en") as resp:
                text = await resp.read()
                page = text.decode("utf-8")
                soup = BeautifulSoup(page, 'lxml')

                for tag in soup.find_all("meta"):
                    if tag.get("name", None) == "csrf_token":
                        csrf_token = tag.get("content", None)

            async with session.post("https://support.plox.host/en/search", data={'_token': csrf_token, "query": search},
                                    cookies=resp.cookies) as resp:
                text = await resp.read()
                soup = BeautifulSoup(text.decode("utf-8"), 'lxml')

                record_count = soup.text.replace("\n", "").strip().split("Found")[1].split("'.")[0].split("records")[
                    0].strip()
                records = [f"Found {record_count} articles\n"]
                count = 0
                for ul_tag in soup.find_all("ul", class_="sp-article-list"):
                    for li_tag in ul_tag.find_all("li"):
                        for url in li_tag.find_all("a"):
                            if "article" in url['href'].split("/"):
                                for heading in li_tag.find_all("h4"):
                                    count += 1
                                    text_content = heading.text.replace("\n", "").replace("  ", "").strip()
                                    text_url = url["href"]
                                    records.append(f"[`{count}. {text_content}`]({text_url})")

                embed = discord.Embed(color=0x36a39f, description="\n".join(records))
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Support(bot))
