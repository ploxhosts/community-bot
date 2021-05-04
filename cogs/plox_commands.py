from discord.ext import commands
import discord
import tools
from bs4 import BeautifulSoup
import aiohttp


class Support(commands.Cog):
    """Commands that exclusive to the ploxhost server"""

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    async def cog_check(self, ctx):
        db = self.database
        posts = db.serversettings
        data = await posts.find_one({"guild_id": ctx.guild.id})

        return bool(
            data["support"] is True
            or ctx.guild.id in [346715007469355009, 742055439088353341]
        )

    @commands.group(name='support', aliases=["spprt"], usage="support",
                    description="Access the support settings")
    @tools.has_perm()
    async def support(self, ctx):
        pass

    @support.command(name='allow', aliases=["enable"], usage="support allow",
                     description="Allows the use of support commands and features such as auto support and knowledge base search")
    @tools.has_perm(manage_messages=True)
    async def allow(self, ctx):
        db = self.database
        posts = db.serversettings
        await posts.update_one({"guild_id": ctx.guild.id},
                               {"$set": {"support": True}})
        await ctx.send("Allowed the use of support services in this server.")

    @support.command(name='deny', aliases=["disable"], usage="support deny",
                     description="Denies the use of support commands and features such as auto support and knowledge base search")
    @tools.has_perm(manage_messages=True)
    async def deny(self, ctx):
        db = self.database
        posts = db.serversettings
        await posts.update_one({"guild_id": ctx.guild.id},
                               {"$set": {"support": False}})
        await ctx.send("Allowed the use of support services in this server.")

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
