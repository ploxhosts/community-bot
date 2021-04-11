import datetime
import json
import logging
import os
import random
import time
import discord
from discord.ext import commands, tasks
import urllib.request
import urllib.error
import shutil
from pathlib import Path
from discord_slash import SlashCommand

# Runs database connections and env
from prepare import database

token = os.getenv('bot_token')

# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)


with open('jokes.json') as json_file:
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

    result = await collection.find_one({"guild_id": message.guild.id})
    if result is None:
        pass
    else:
        prefix = result["prefix"]
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


@bot.event
async def on_message(message):
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


def overwrite_files():
    # Normal files
    for new_code_file in os.listdir("new_code/community-bot-main"):
        if new_code_file not in ["main.py", "prepare.py", ".env"]:
            file = f"new_code/community-bot-main/{new_code_file}"
            item = os.path.join(file)
            if os.path.isfile(item):
                try:
                    Path(file).rename(new_code_file)
                except FileExistsError:
                    Path(file).replace(new_code_file)

    # Cogs
    for new_code_file in os.listdir("new_code/community-bot-main/cogs"):
        existing_file = Path("cogs/" + new_code_file)
        file = f"new_code/community-bot-main/cogs/{new_code_file}"
        item = os.path.join(file)
        if os.path.isfile(item):
            try:
                Path(file).rename(existing_file)
            except FileExistsError:
                Path(file).replace(existing_file)


def get_new_files():
    urllib.request.urlretrieve("https://github.com/PloxHost-LLC/community-bot/archive/refs/heads/main.zip", "code.zip")

    zip_file = Path('code.zip')
    os.makedirs("new_code", exist_ok=True)
    new_code = Path('new_code')

    shutil.unpack_archive(zip_file, new_code)

    overwrite_files()


@bot.command()
@commands.check(is_owner)
async def update(ctx):
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
    await ctx.send("Updated!")
    try:
        get_new_files()
    except urllib.error.HTTPError as e:
        return await ctx.send("Cannot load files!")
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
    await ctx.send("Updated!")


@bot.command()
@commands.check(is_owner)
async def getserverfile(ctx, file=None):
    if file is None:
        files = []
        for file_name in os.listdir("logs"):
            if file_name.endswith(".log"):
                files.append(file_name)
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
    statuses = ["?help | My dms are open ;)",
                "?help | Open-Source on github",
                "?help | $1 per gb Plox.Host",
                f"Managing {len(set(bot.get_all_members()))} members!",
                "Plox.Host", "Management to be looking sus",
                "Should you be cheating on your test?",
                "Do I have friends?",
                f"{unique_joke}",
                "Some random joke failed to be rendered",
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

try:
    get_new_files()
except urllib.error.HTTPError as e:
    rootLogger.critical(f"CANNOT UPDATE CODE: {e}")
    rootLogger.critical(f"CANNOT UPDATE CODE: {e}")
    print("--------------------------------------------------------------------------------")
    print(f"CANNOT UPDATE CODE: {e}")
    print("--------------------------------------------------------------------------------")

# Start up the bot

bot.run(token)
