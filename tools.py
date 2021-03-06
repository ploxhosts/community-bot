import random
import time
from discord.ext import commands
from discord.ext.commands import MissingPermissions

from prepare import database
import discord


def generate_flake():
    flake = (int((time.time() - 946702800) * 1000) << 23) + random.SystemRandom().getrandbits(23)
    return flake


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
        super().__init__(f'You require permissions for command: **{perm_node}** or cog: **{cog_perm_node}**. Try enabling it with the `perms grant` command.')


class RevokedAddedPerms(commands.CommandError):
    def __init__(self, perm_node, cog_perm_node, role_name):
        self.perm_node = perm_node
        self.cog_perm_node = cog_perm_node
        self.role_name = role_name
        super().__init__(f'Role `{role_name}` cannot run the command: **{perm_node}** or the cog: **{cog_perm_node}**. Try enabling it with the `perms grant` command.')


def has_perm(**perms):
    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError('Invalid permission(s): %s' % (', '.join(invalid)))

    db = database.bot
    collection = db.permissions

    def predicate(ctx):
        def has_default_perms():
            ch = ctx.channel
            permissions = ch.permissions_for(ctx.author)

            missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

            if not missing:
                return True

            raise MissingPermissions(missing)

        db_obj = collection.find_one({"guild_id": ctx.guild.id})

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
