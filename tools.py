#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Iterator, Union, List
import datetime
import random
import time

from motor.motor_asyncio import AsyncIOMotorDatabase
from discord.ext.commands import MissingPermissions
from discord.ext import commands
import discord

from motorsqlite.src import MotorSqlite
from config import Global


def init(_database: Union[AsyncIOMotorDatabase, MotorSqlite]) -> None:
    global database

    Global.database = _database
    database = _database


def generate_flake() -> int:
    return (
        (int((time.time() - 946702800) * 1000) << 23)
        + random.SystemRandom().getrandbits(23)
    )


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


def get_time(word: str) -> Union[float, int, None]:
    res = None

    if "s" in word:
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
    def __init__(self, perm_node, cog_perm_node):
        self.perm_node = perm_node
        self.cog_perm_node = cog_perm_node
        super().__init__(
            f'You require permissions for command: **{perm_node}** or cog: **{cog_perm_node}**. Try enabling it with the `perms grant` command.')


class RevokedAddedPerms(commands.CommandError):
    def __init__(self, perm_node, cog_perm_node, role_name):
        self.perm_node = perm_node
        self.cog_perm_node = cog_perm_node
        self.role_name = role_name
        super().__init__(
            f'Role `{role_name}` cannot run the command: **{perm_node}** '
            f'or the cog: **{cog_perm_node}**. Try enabling it with the `perms grant` command.'
        )


def has_perm(**perms):
    default_perms = discord.Permissions.VALID_FLAGS
    default_perms["required"] = 9999999
    invalid = set(perms) - set(default_perms)
    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    db = database.bot
    collection = db.permissions

    async def predicate(ctx):
        def has_default_perms():
            ch = ctx.channel
            permissions = ch.permissions_for(ctx.author)

            missing = []
            for perm, value in perms.items():
                if perm == "required":
                    raise MissingAddedPerms(
                        ctx.command.name.lower(), ctx.command.cog.qualified_name)
                if getattr(permissions, perm) != value:
                    missing.append(perm)

            if not missing:
                return True

            raise MissingPermissions(missing)

        db_obj = await collection.find_one({"guild_id": ctx.guild.id})
        await check_command(ctx.command, perms)
        if not perms or len(perms) == 0:
            return True
        if "required" in perms:
            if not perms["required"]:
                return True
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
                        raise RevokedAddedPerms(
                            ctx.command.name, cog.qualified_name, role.name)
                    if "command" in bad_perm:
                        if ctx.command.name.lower() == bad_perm.replace("command:", "").strip().lower():
                            raise RevokedAddedPerms(
                                ctx.command.name, cog.qualified_name, role.name)
                    else:
                        if ctx.cog.qualified_name.lower() == bad_perm.lower():
                            raise RevokedAddedPerms(
                                ctx.command.name, cog.qualified_name, role.name)
            # If the perm is allowed to that role
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

        for role in ctx.author.roles:  # Get each role
            if role.id == 476614251096571920:  # Only works in the main PloxHost server so other servers are not affected basically allowing management to use everything
                return True

        raise MissingAddedPerms(ctx.command.name.lower(),
                                ctx.command.cog.qualified_name)

    return commands.check(predicate)


def get_command_model(command: commands.Command, perms):
    return {
        "name": command.name.lower(),
        "usage": command.usage,
        "description": command.description,
        "aliases": command.aliases,
        "brief": command.brief,
        "cog": command.cog.qualified_name.lower(),
        "perms": perms,
        "hidden": command.hidden,
        "admin": False
    }


def get_cog_model(command: discord.ext.commands.Command):
    return {
        "name": command.cog.qualified_name.lower(),
        "description": command.cog.description,
        "hidden": False,
        "admin": False
    }


async def check_command(command, perms):
    db = database.bot
    collection = db.commands
    await check_if_update({"name": command.name.lower(), "cog": command.cog.qualified_name.lower()},
                          get_command_model(command, perms), collection)

    collection = db.cogs

    await check_if_update({"name": command.cog.qualified_name.lower()},
                          get_cog_model(command), collection)


async def get_all_commands(bot) -> Iterator[commands.Command]:
    """Yield all commands for all cogs in all extensions."""
    for module in bot.walk_modules():
        for cog in bot.walk_cogs(module):
            for cmd in bot.walk_commands(cog):
                yield cmd


async def create_tables() -> Union[bool, None]:
    """
    Function which should be run to create tables + schemas required for the
    bot in the sqlite3 databases. Will return None when sqlite3 is not enabled
    in the config file, or a boolean dependant on the success of the creation(s)
    """

    if not Global.useSqlite or not isinstance(database, MotorSqlite):
        return None

    # DATATYPES:
        # NULL
        # INTEGER (signed number)
        # REAL (floating point value)
        # TEXT (text string)
        # BLOB (stored exactly as given)
    # TODO(blaze): maybe create these schemas dynamically instead of hardcoding?
    schemas = {
        'economy': {
            'user_id': 'INTEGER',
            'balance': 'REAL',
            'balances': {'TEXT': 'INTEGER'},
            'cash': {'TEXT': 'INTEGER'},
            'stocks': {
                'TEXT': {
                    'TEXT': 'INTEGER',
                    'TEXT': 'INTEGER',
                },
            },
            'guilds': ['INTEGER'],
            'multiplier': 'REAL',
            'd_lottery_tickets': 'INTEGER',
            'w_lottery_tickets': 'INTEGER',
            'm_lottery_tickets': 'INTEGER',
            'latest_update': 'TEXT',
        },
        'servereconomy': {
            'guild_id': 'INTEGER',
            'level': 'INTEGER',
            'balance': 'REAL',
            'tax_rate': 'REAL',
            'computer': {
                'firewall': 'INTEGER',
                'antivirus': 'INTEGER',
                'sdk': 'INTEGER',
                'malware': 'INTEGER',
            },
            'weapons': {
                'sns': 'INTEGER',
            },
            'worth': 'REAL',
            'latest_update': 'TEXT',
        },
        'player_data': {
            'user_id': 'INTEGER',
            'guild_id': 'INTEGER',
            'level': 'INTEGER',
            'exp': 'INTEGER',
            'total_exp': 'INTEGER',
            'multiplier': 'REAL',
            'seconds_in_vc': 'INTEGER',
            'time_since_join_vc': 'INTEGER',
            'latest_vc_channel': 'INTEGER',
            'message_time': 'TEXT',
            'mod_logs': [],
            'latest_update': 'TEXT',
        },
        'globalusers': {
            'user_id': 'INTEGER',
            'email': 'TEXT',
            'notify_settings': {
                'on_ban': 'INTEGER',  # bool
                'on_kick': 'INTEGER',  # bool
                'on_modify_settings': 'INTEGER',  # bool
                'on_bot_major_update': 'INTEGER',  # bool
                'on_admin_abuse': 'INTEGER',  # bool
            },
            'guilds': {},
            'user_rank': 'INTEGER',
            'coins': 'INTEGER',
            'verified': 'INTEGER',  # bool
            'last_seen': 'TEXT',
            'on_website': 'INTEGER',  # bool
            'github': 'TEXT',
            'additions': 'INTEGER',
            'negations': 'INTEGER',
            'ranks': {
                'dev': 'INTEGER',  # bool
                'staff': 'INTEGER',  # bool
                'admin': 'INTEGER',  # bool
                'contributor': 'INTEGER',  # bool
            },
            'latest_update': 'TEXT',
        },
        'serversettings': {
            'guild_id': 'INTEGER',
            'prefix': 'TEXT',
            'users': {},
            'level': 'INTEGER',
            'levels': {
                'enbaled': 'INTEGER',  # bool
                'voice_enabled': 'INTEGER',  # bool
                'level_ignore_channels': [],
                'level_ignore_roles': [],
            },
            'welcome': {
                'channel': 'INTEGER',
                'code': 'INTEGER',  # bool
                'message': 'TEXT',
            },
            'suggestions': {
                'intake_channel': 'INTEGER',
                'approved_channel': 'INTEGER',
                'denied_channel': 'INTEGER',
            },
            'auto_mod': {
                'chat_moderation': 'INTEGER',  # bool
                'blacklisted_domains': [],
                'anti_invite': 'INTEGER',  # bool
                'allowed_invites': [],
                'banned_words': [],
                'ignore_roles': [],
                'mod_ignore_channels': [],
                'max_mentions': 'INTEGER',
                'on_mass_mention': 'INTEGER',  # enum 0, 1, 2, 3, 4
                'auto_temp_ban_time': 'INTEGER',
                'max_caps': 'REAL',
                'spam_prevention': 'INTEGER',  # bool
                'auto_mute': 'INTEGER',  # bool
                'auto_mute_time': 'INTEGER',
            },
            'log_channel': 'INTEGER',
            'muted_role_id': 'INTEGER',
            'extra_settings': {},
            'latest_update': 'TEXT',
            'linked_guilds': {},
            'support': 'INTEGER',  # bool
        }
    }

    # a small hackish parser for the schemas to create an sql query
    for table, schema in schemas.items():
        query: List[str] = []
        isFirst = True

        query.append(f'CREATE TABLE IF NOT EXISTS {table} (')

        for key, value in schema.items():
            if not isFirst:
                query.append(',')
            else:
                isFirst = not isFirst

            query.append(key)

            if isinstance(value, dict) or isinstance(value, list):
                # blob, since sqlite does not support these types
                query.append('BLOB')
            else:
                query.append(value)

        query.append(');')

        await database.bot.__getattr__(key).execute_raw(' '.join(query))
