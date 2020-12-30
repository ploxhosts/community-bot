import os
import random
import discord
from discord.ext import commands, tasks
import logging

# Runs database connections and env
from prepare import database

token = os.getenv('bot_token')

#logger = logging.getLogger('discord')
#logger.setLevel(logging.DEBUG)
#handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
#handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
#logger.addHandler(handler)

def get_prefix(bot, message):
    prefix = os.getenv("prefix") or "?"  # Default prefix specified in the env file or ? as default

    if not message.guild:
        return commands.when_mentioned_or(prefix)(bot, message)
    db = database.client.bot
    collection = db.serversettings

    result = collection.find_one({"guild_id": message.guild.id})
    if result is None:
        pass
    else:
        prefix = result["prefix"]
    return commands.when_mentioned_or(prefix)(bot, message)


intents = discord.Intents.all()  # Allow the use of custom intents

bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)

bot.remove_command('help')  # Get rid of the default help command as there is no use for it

bot.database = database  # for use else where


# What gets executed when bot connects to discord's api

@bot.event
async def on_ready():
    members = len(set(bot.get_all_members()))
    print('-----------------')
    print(f"Logged in as {bot.user.id} \nin {len(bot.guilds)} servers with {members} members")
    print('-----------------')
    change_status.start()


@bot.event
async def on_message(message):
    # Maybe some logic here
    await bot.process_commands(message)


# Runs when bot joins a guild

@bot.event
async def on_guild_join(g):
    success = False
    i = 0
    while not success:
        try:
            await g.channels[i].send(
                f"Hello! Thanks for inviting me to your server.\n To set a custom prefix, use `?prefix <prefix>`.\n For more help, use `?help`")
        except (discord.Forbidden, AttributeError):
            i += 1
        except IndexError:
            # if the server has no channels, doesn't let the bot talk, or all vc/categories.
            pass
        else:
            success = True


# Allow /cog/ restart command for the bot owner

async def is_owner(self, ctx):
    return ctx.author.id in [553614184735047712]  # Replace list with people who you trust


@bot.command()
@commands.check(is_owner)
async def shutdown(self, ctx):
    try:
        await self.bot.logout()
    except EnvironmentError as e:
        print(e)
        self.bot.clear()


@bot.command()
@commands.check(is_owner)
async def reload(ctx, cog_name):
    try:
        bot.unload_extension(f"cogs.{cog_name}")
        bot.load_extension(f"cogs.{cog_name}")
        ctx.send(f"{cog_name} reloaded")
    except Exception as exception:
        print(f"{cog_name} can not be loaded:")
        raise exception


# Used for the automatic change of status messages

@tasks.loop(minutes=5.0, count=None, reconnect=True)
async def change_status():
    statuses = ["?help | My dms are open ;)",
                "?help | Open-Source on github",
                "?help | $1 per gb Plox.Host",
                f"Managing {len(set(bot.get_all_members()))} members!",
                "Plox.Host", "Management to be looking sus",
                "Should you be cheating on your test?",
                "Management to node 15, Management to node 15, meme incoming, thank you. ",
                "Do I have friends?",
                f"Some random joke failed to be rendered",
                "HTML is a programming language no cap"]
    status = random.choice(statuses)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(status))


# Adding sub commands from folder /cogs/ to clean up main.py
# All commands should be added to the cogs and not touch main.py unless needed to
for cog in os.listdir("cogs"):
    if cog.endswith(".py"):
        try:
            cog = f"cogs.{cog.replace('.py', '')}"
            bot.load_extension(cog)
        except Exception as e:
            print(f"{cog} can not be loaded:")
            raise e

# Start up the bot

bot.run(token)
