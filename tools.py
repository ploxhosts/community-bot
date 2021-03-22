import random
import time
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from typing import Iterator
from prepare import database
import discord
import datetime


def generate_flake():
    flake = (int((time.time() - 946702800) * 1000) << 23) + random.SystemRandom().getrandbits(23)
    return flake


async def check_if_update(find, main_document, collection):
    if await collection.count_documents(find) > 0:
        fields = {}
        async for x in collection.find(find):
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
                    await collection.update_one(find, {"$set": {key: value}})
                else:
                    try:
                        sub_dict = dict(value)
                        for key2, value2 in sub_dict.items():
                            if key2 not in fields[key].keys():
                                new_value = value
                                new_value[key2] = value2
                                await collection.update_one(find,
                                                            {"$set": {key: new_value}})
                        for key2, value2 in fields[key].items():
                            if key2 not in sub_dict.keys():
                                new_dict = {}
                                for item in sub_dict:
                                    if item != key2:
                                        new_dict[item] = sub_dict.get(item)
                                await collection.update_one(find, {"$set": {key: new_dict}})
                    except:
                        pass
            for key2, value2 in fields.items():
                if key2 not in db_dict:
                    await collection.update_one(find, {"$unset": {key2: 1}})
    else:
        await collection.insert_one(main_document)


def get_time(word):
    res = None
    if "perm" == word.lower():
        pass
    elif "s" in word:
        res = int(word.split("s")[0]) / 60
    elif "m" in word:
        formatted_word = word.split("m")
        res = int(formatted_word[0])
    elif "h" in word:
        formatted_word = word.split("h")
        res = int(formatted_word[0]) * 60
    elif "d" in word:
        formatted_word = word.split("d")
        res = int(formatted_word[0]) * 60 * 24
    elif "w" in word:
        formatted_word = word.split("w")
        res = int(formatted_word[0]) * 60 * 24 * 7
    return res


class MissingAddedPerms(commands.CommandError):
    def __init__(self, perm_node, cog_perm_node, role_name):
        self.perm_node = perm_node
        self.cog_perm_node = cog_perm_node
        self.role_name = role_name
        super().__init__(
            f'You require permissions for command: **{perm_node}** or cog: **{cog_perm_node}**. Try enabling it with the `perms grant` command.')


class RevokedAddedPerms(commands.CommandError):
    def __init__(self, perm_node, cog_perm_node, role_name):
        self.perm_node = perm_node
        self.cog_perm_node = cog_perm_node
        self.role_name = role_name
        super().__init__(
            f'Role `{role_name}` cannot run the command: **{perm_node}** or the cog: **{cog_perm_node}**. Try enabling it with the `perms grant` command.')


def has_perm(**perms):
    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    db = database.bot
    collection = db.permissions

    async def predicate(ctx):
        def has_default_perms():
            ch = ctx.channel
            permissions = ch.permissions_for(ctx.author)

            missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

            if not missing:
                return True

            raise MissingPermissions(missing)

        db_obj = await collection.find_one({"guild_id": ctx.guild.id})
        await check_command(ctx.command, perms)
        perm_nodes = db_obj["perm_nodes"]
        bad_perm_nodes = db_obj["bad_perm_nodes"]
        for role in ctx.author.roles:
            role: discord.Role
            # Negate perms, used if you want to stop a rank from executing a command but allow others too
            if str(role.id) in bad_perm_nodes:
                for bad_perm in bad_perm_nodes[f"{role.id}"]:
                    cog = ctx.cog
                    cog: discord.ext.commands.Cog

                    if bad_perm == "*":
                        raise RevokedAddedPerms(ctx.command.name, cog.qualified_name, role.name)
                    if "command" in bad_perm:
                        if ctx.command.name.lower() == bad_perm.replace("command:", "").strip().lower():
                            raise RevokedAddedPerms(ctx.command.name, cog.qualified_name, role.name)
                    else:
                        if ctx.cog.qualified_name.lower() == bad_perm.lower():
                            raise RevokedAddedPerms(ctx.command.name, cog.qualified_name, role.name)
            if str(role.id) in perm_nodes:
                for good_perm in perm_nodes[f"{role.id}"]:
                    if good_perm == "*":
                        return True
                    if "command" not in good_perm:
                        if ctx.cog.qualified_name.lower() == good_perm.lower():
                            return True
                    else:
                        if ctx.command.name.lower() == good_perm.replace("command:", "").strip().lower():
                            return True
        if has_default_perms():
            return True

        raise MissingAddedPerms(ctx.command.name.lower(), cog.qualified_name)

    return commands.check(predicate)


def get_command_model(command: discord.ext.commands.Command, perms):
    return {
        "name": command.name.lower(),
        "cog": command.cog.qualified_name.lower(),
        "perms": perms,
        "hidden": False,
        "admin": False
    }


async def check_command(command, perms):
    db = database.bot
    collection = db.commands
    await check_if_update({"name": command.name.lower(), "cog": command.cog.qualified_name.lower()},
                          get_command_model(command, perms), collection)


async def get_all_commands(bot) -> Iterator[commands.Command]:
    """Yield all commands for all cogs in all extensions."""
    for module in bot.walk_modules():
        for cog in bot.walk_cogs(module):
            for cmd in bot.walk_commands(cog):
                yield cmd
