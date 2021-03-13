from discord.ext import commands
import discord
import tools
import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp


class Support(commands.Cog):
    """Commands that exclusive to the ploxhost server"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    async def cog_check(self, ctx):
        return ctx.guild.id in [346715007469355009, 742055439088353341]  # Replace list with people who you trust

    @commands.command(name='book', aliases=["rtfm"], usage="book How to delete server files",  description="search the knowledge base")
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
                for ul_tag in soup.find_all("ul", class_="sp-article-list"):
                    for li_tag in ul_tag.find_all("li"):
                        for url in li_tag.find_all("a"):
                            if "article" in url['href'].split("/"):
                                for heading in li_tag.find_all("h4"):
                                    text_content = heading.text.replace("\n", "").replace("  ", "").strip()
                                    text_url = url["href"]
                                    records.append(f"[`{text_content}`]({text_url})")

                embed = discord.Embed(color=0x36a39f, description="\n".join(records))
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Support(bot))
