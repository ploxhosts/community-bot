import datetime
import json
import logging
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
import glob
import hashlib

import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from discord_slash.utils import manage_commands
from motor.motor_asyncio import AsyncIOMotorClient

database = None

try:
    # Runs database connections and env
    from prepare import database
except:
    # preventative measure incase of failure
    from dotenv import load_dotenv

    load_dotenv()
    connection_string = os.getenv("connection_string")

    database = AsyncIOMotorClient(connection_string)

token = os.getenv('bot_token')
prod_org = os.getenv('prod')
prod = os.getenv('prod')
try:
    if int(prod_org) == 1:  # main branch
        prod = "https://github.com/PloxHost-LLC/community-bot/archive/refs/heads/main.zip"
    elif int(prod_org) == 2:  # test branch
        prod = "https://github.com/PloxHost-LLC/community-bot/archive/refs/heads/test.zip"
    elif int(prod_org) == 3:
        prod = os.getenv('prod_string')
except Exception as e:
    print(e)
    if prod_org is None:
        prod_org = 1
        prod = "https://github.com/PloxHost-LLC/community-bot/archive/refs/heads/main.zip"
    else:
        prod_org = 0
        prod = 0

# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)


with open('jokes.json', "r+", encoding="utf-8") as json_file:
    joke_list = json.load(json_file)
    jokes = []
    for joke in joke_list:
        jokes.append(joke_list[str(joke)])


# noinspection PyShadowingNames
async def get_prefix(bot, message):
    prefix = os.getenv("prefix") or "?"  # Default prefix specified in the env file or ? as default

    if not message.guild:
        return commands.when_mentioned_or(prefix)(bot, message)
    db = database.bot
    collection = db.serversettings
    try:
        result = await collection.find_one({"guild_id": message.guild.id})
        if result is not None:
            prefix = result["prefix"]
    except Exception as e:
        print(e)
        print("DB ACCESS IS DISALLOWED")
        print("DB ACCESS IS DISALLOWED")
        print("DB ACCESS IS DISALLOWED")
        print("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
        rootLogger.critical("DB ACCESS IS DISALLOWED")
    return commands.when_mentioned_or(prefix)(bot, message)


intents = discord.Intents.all()  # Allow the use of custom intents

bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
slash = SlashCommand(bot, sync_commands=True, override_type=True)

bot.remove_command('help')  # Get rid of the default help command as there is no use for it

bot.database = database  # for use else where

bot.delete_message_cache = []

os.makedirs("logs", exist_ok=True)

fileName = time.strftime("%Y-%m-%d-%H%M")

for filename in os.listdir("logs"):

    if filename.endswith(".log"):
        f_name = filename.split("-")
        year = int(f_name[0])
        month = int(f_name[1])
        day = int(f_name[2])
        now = datetime.datetime.now()
        if now.month - month >= 1:
            os.remove(os.path.join("logs", filename))

f = open(f"logs/{fileName}.log", "w")
f.close()

fileHandler = logging.FileHandler(f"logs/{fileName}.log")

rootLogger = logging.getLogger()

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)


# What gets executed when bot connects to discord's api

@bot.event
async def on_ready():
    members = len(set(bot.get_all_members()))
    channel = bot.get_channel(809129113985876020)
    if channel:
        channel: discord.TextChannel
        await channel.send(f"Logged in as {bot.user.id} \nin {len(bot.guilds)} servers with {members} members")
    rootLogger.debug('-----------------')
    rootLogger.debug(f"Logged in as {bot.user.id} \nin {len(bot.guilds)} servers with {members} members")
    rootLogger.debug('-----------------')
    print('-----------------')
    print(f"Logged in as {bot.user.id} \nin {len(bot.guilds)} servers with {members} members")
    print('-----------------')
    change_status.start()

    if bot.user.id in [696430450142347357, 749899795782434897]:
        await manage_commands.remove_all_commands(bot.user.id, token, None)


@bot.event
async def on_message(message: discord.Message):
    # Maybe some logic here
    await bot.process_commands(message)


# Allow /cog/ restart command for the bot owner

async def is_owner(ctx):
    return ctx.author.id in [553614184735047712, 148549003544494080,
                             518854761714417664]  # Replace list with people who you trust


@bot.command()
@commands.check(is_owner)
async def shutdown(ctx):
    try:
        await ctx.bot.logout()
    except EnvironmentError as error:
        rootLogger.error(error)
        ctx.bot.clear()


@bot.command()
@commands.check(is_owner)
async def reload(ctx, cog_name):
    try:
        bot.unload_extension(f"cogs.{cog_name}")
        bot.load_extension(f"cogs.{cog_name}")
        await ctx.send(f"{cog_name} reloaded")
    except Exception as exception:
        rootLogger.critical(f"{cog_name} can not be loaded: {exception}")
        raise exception


def overwrite_files(overwrite):
    if prod_org == 1:
        start_path = "new_code/community-bot-main"
    elif prod_org == 2:
        start_path = "new_code/community-bot-test"
    else:
        if overwrite:
            start_path = "new_code/community-bot-main"
        else:
            return False
    # Normal files
    for new_code_file in os.listdir(start_path):
        if new_code_file not in ["main.py", "prepare.py", ".env"]:
            file = f"{start_path}/{new_code_file}"
            item = os.path.join(file)
            if os.path.isfile(item):
                try:
                    Path(file).rename(new_code_file)
                except FileExistsError:
                    Path(file).replace(new_code_file)
    # Cogs
    for new_code_file in os.listdir(f"{start_path}/cogs"):
        existing_file = Path("cogs/" + new_code_file)
        file = new_code_file
        item = os.path.join("cogs", file)
        if os.path.isfile(item) or not os.path.exists(item):
            try:
                shutil.move(f"{start_path}/cogs/{new_code_file}", existing_file)
            except FileExistsError:
                Path(item).replace(existing_file)
            except FileNotFoundError:
                shutil.move(f"{start_path}/cogs/{new_code_file}", existing_file)

    return start_path


def get_new_files(overwrite):
    global prod, prod_org
    if str(prod) == "0":
        return "Prod is 0"
    urllib.request.urlretrieve(prod, "code.zip")

    zip_file = 'code.zip'
    os.makedirs("new_code", exist_ok=True)
    new_code = 'new_code'

    shutil.unpack_archive(zip_file, new_code)

    return overwrite_files(overwrite)


@bot.command()
@commands.check(is_owner)
async def update(ctx, do_pip=0, overwrite=False):
    output = None
    try:
        output = get_new_files(overwrite)
    except urllib.error.HTTPError as e:
        return await ctx.send("Cannot load files!")
    if do_pip != 0:
        with open("requirements.txt", "r") as requirements_file:
            requirements = requirements_file.readlines()
        for package in requirements:
            if do_pip == 1:
                subprocess.Popen(f"pip install {package}", shell=True)
            elif do_pip == 2:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package.replace("\n", "").replace(" ", "")])

    for cog in os.listdir("cogs"):
        if cog.endswith(".py"):
            try:
                cog = f"cogs.{cog.replace('.py', '')}"
                bot.unload_extension(cog)
                bot.load_extension(cog)
            except Exception as e:
                rootLogger.critical(f"{cog} can not be loaded:")
                await ctx.send(f"{cog} can not be loaded:")
                raise e
    await ctx.send(f"Updated! {output}")


@bot.command()
@commands.check(is_owner)
async def getserverfile(ctx, file=None):
    if file is None:
        files = [
            file_name
            for file_name in os.listdir("logs")
            if file_name.endswith(".log")
        ]

        await ctx.author.send("\n".join(files))
    else:
        try:
            await ctx.author.send(file=discord.File(os.path.join("logs", file)))
        except Exception as e:
            await ctx.send("An error occurred!")
            print(e)
            rootLogger.critical(e)


# Used for the automatic change of status messages

@tasks.loop(minutes=3.0, count=None, reconnect=True)
async def change_status():
    unique_joke = str(random.choice(jokes)).replace("|", "").strip()
    statuses = [f"{os.getenv('prefix')}help | My dms are open ;)",
                f"{os.getenv('prefix')}help | Open-Source on github",
                f"{os.getenv('prefix')}help | $1 per gb Plox.Host",
                f"Managing {len(set(bot.get_all_members()))} members!",
                "Plox.Host", "Management to be looking sus",
                "Should you be cheating on your test?",
                "Do I have friends?",
                f"{unique_joke}",
                "Some random joke failed to be rendered",
                "Pineapple on pizza? Personally I like it, so does Fluxed.",
                "HTML is a programming language no cap"]
    status = random.choice(statuses)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(status))


# Adding sub commands from folder /cogs/ to clean up main.py
# All commands should be added to the cogs and not touch main.py unless needed to
for cog_new in os.listdir("cogs"):
    if cog_new.endswith(".py"):
        try:
            cog = f"cogs.{cog_new.replace('.py', '')}"
            bot.load_extension(cog)
        except Exception as e:
            rootLogger.critical(f"{cog_new} can not be loaded: {e}")
if str(prod) != "0":
    try:
        get_new_files()
        print("Pulled new updates")
    except urllib.error.HTTPError as e:
        rootLogger.critical(f"CANNOT UPDATE CODE: {e}")
        rootLogger.critical(f"CANNOT UPDATE CODE: {e}")
        print("--------------------------------------------------------------------------------")
        print(f"CANNOT UPDATE CODE: {e}")
        print("--------------------------------------------------------------------------------")
else:
    print("Not pulling new updates")
# Start up the bot

bot.run(token)
