#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from discord_slash.utils.manage_commands import create_option
from discord_slash import cog_ext, SlashContext
from discord.ext import commands
from bs4 import BeautifulSoup
import aiohttp
import discord


class SlashCommands(commands.Cog):
    """Slash commands"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @cog_ext.cog_slash(name="book", description="Searches the PloxHost knowledge base",
                       options=[create_option(name="query", description="What do you want to search up?",
                                              option_type=3, required=True)])
    async def _book(self, ctx: SlashContext, search):
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
    bot.add_cog(SlashCommands(bot))
