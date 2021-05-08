#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List
import urllib.request
import urllib.error
import datetime
import logging
import random
import shutil
import json
import time
import os

from discord_slash.utils import manage_commands
from discord.ext import commands, tasks
from discord_slash import SlashCommand
from dotenv import load_dotenv
import discord

# init env before local imports
load_dotenv()

# Runs database connections and env
from config import Global, Ids, Prod
from prepare import database


# Setup logger
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


fileHandler = logging.FileHandler(f"logs/{fileName}.log")
rootLogger = logging.getLogger()

logFormatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

intents = discord.Intents.all()  # Allow the use of custom intents

# noinspection PyShadowingNames
async def get_prefix(bot, message):
    prefix = Global.prefix

    if not message.guild:
        return commands.when_mentioned_or(prefix)(bot, message)

    db = database.bot
    collection = db.serversettings

    result = await collection.find_one({"guild_id": message.guild.id})

    if result is not None:
        prefix = result["prefix"]

    return commands.when_mentioned_or(prefix)(bot, message)

bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    intents=intents
)

@bot.event
async def on_message(message):
    # Maybe some logic here
    await bot.process_commands(message)


# Allow /cog/ restart command for the bot owner

async def is_owner(ctx):
    return ctx.author.id in Ids.owners


def overwrite_files():
    if Global.prod == 1:
        start_path = "new_code/community-bot-main"
    elif Global.prod == 2:
        start_path = "new_code/community-bot-test"
    else:
        return
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
        file = f"/cogs/{new_code_file}"
        item = os.path.join(file)
        if os.path.isfile(item):
            try:
                Path(file).rename(existing_file)
            except FileExistsError:
                Path(file).replace(existing_file)


def get_new_files() -> None:
    if prod == 0:
        return

    urllib.request.urlretrieve(prod, "code.zip")

    zip_file = 'code.zip'
    os.makedirs("new_code", exist_ok=True)
    new_code = 'new_code'

    shutil.unpack_archive(zip_file, new_code)

    overwrite_files()


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
        files = [x for x in os.listdir("logs") if x.endswith(".log")]
        await ctx.author.send("\n".join(files))

    else:
        try:
            await ctx.author.send(file=discord.File(os.path.join("logs", file)))
        except Exception as e:
            await ctx.send("An error occurred!")
            rootLogger.critical(e)


# Used for the automatic change of status messages
@tasks.loop(minutes=3.0, count=None, reconnect=True)
async def change_status():
    unique_joke = random.choice(jokes).replace("|", "").strip()

    statuses = [
        f"{os.getenv('prefix')}help | My dms are open ;)",
        f"{os.getenv('prefix')}help | Open-Source on github",
        f"{os.getenv('prefix')}help | $1 per gb Plox.Host",
        f"Managing {len(set(bot.get_all_members()))} members!",
        "Plox.Host", "Management to be looking sus",
        "Should you be cheating on your test?",
        "Do I have friends?",
        f"{unique_joke}",
        "Some random joke failed to be rendered",
        "HTML is a programming language no cap"
    ]
    status = random.choice(statuses)

    await bot.change_presence(status=discord.Status.online, activity=discord.Game(status))


@bot.event
async def on_ready():
    members = len(set(bot.get_all_members()))
    channel: discord.TextChannel = bot.get_channel(
        809129113985876020
    )  # type: ignore
    msg = f"Logged in as {bot.user.id} \nin {len(bot.guilds)} servers with {members} members"

    if channel is not None:
        await channel.send(msg)

    rootLogger.debug('-' * 17)
    rootLogger.debug(msg)
    rootLogger.debug('-' * 17)

    print('-' * 17)
    print(msg)
    print('-' * 17)

    change_status.start()

    if bot.user.id in Ids.ploxy.values():
        await manage_commands.remove_all_commands(bot.user.id, Global.token, None)

if __name__ == '__main__':
    slash = SlashCommand(bot, sync_commands=True, override_type=True)

    # Get rid of the default help command as there is no use for it
    bot.remove_command('help')

    # for use elsewhere
    bot.database = database  # type: ignore
    bot.delete_message_cache = []  # type: ignore

    if Global.prod is not None:
        prod: str = Prod.urls[Global.prod]

        if not prod:
            rootLogger.critical("No production URL set")

    else:
        prod = Prod.urls[1]

    with open('jokes.json', 'r+') as f:
        jokes: List[str] = json.load(f)['jokes']

    # Adding sub commands from folder /cogs/ to clean up main.py
    # All commands should be added to the cogs and not touch main.py unless needed to
    for cog_new in os.listdir("cogs"):
        if cog_new.endswith(".py"):
            try:
                cog = f"cogs.{cog_new.replace('.py', '')}"
                bot.load_extension(cog)
            except Exception as e:
                rootLogger.critical(f"{cog_new} can not be loaded: {e}")

    if Global.prod != 0:
        try:
            get_new_files()
            rootLogger.info("Pulled new updates")
        except urllib.error.HTTPError as e:
            rootLogger.critical(f"CANNOT UPDATE CODE: {e}")
    else:
        rootLogger.info("Not pulling new updates")
    
    # Start up the bot
    bot.run(Global.token)
