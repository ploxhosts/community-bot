#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os

from discord.ext import commands
from bs4 import BeautifulSoup
import pytesseract
import aiohttp
import discord
import cv2

import tools


if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


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

    def check_trigger_message(self, trigger_check, message_raw):
        for trigger in trigger_check:
            if trigger.lower() in message_raw.lower():
                return trigger

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

    @commands.Cog.listener()
    async def on_message(self, message):
        attachments = message.attachments
        loop = asyncio.get_event_loop()
        support_message_needed = message.content
        if message.author.bot:
            return

        for attachment in attachments:
            if any(attachment.filename.lower().endswith(image) for image in ["jpeg", "png", "gif", "jpg"]):
                try:
                    await attachment.save(attachment.filename)
                    img = cv2.imread(attachment.filename)
                    result = await loop.run_in_executor(None, pytesseract.image_to_string, img)
                    support_message_needed += f"\n {result}"
                    os.remove(attachment.filename)
                except:
                    os.remove(attachment.filename)
            elif any(attachment.filename.lower().endswith(image) for image in ["txt", "log"]):
                content = await attachment.read()
                support_message_needed += f"\n {content}"

        support_messages = {
            "modulenotfound": {
                "triggers": ["modulenotfoundrror: no module named", "modulenotfoundrror", "no module named",
                             "cannot be found"],
                "prevents": ["you get this", "get this", "-s"],
                "response": "Oh no, sorry to hear that you are having issues with your discord bot hosting.\nThis is quite easy to fix with a `requirements.txt` file. Make sure your file is in the main folder/directory.\n\nYou will need to insert the module/thing you normally install with pip. For example discord.py you could use a `requirements.txt` file with the content of \n```\ndiscord.py\ndnspython\nmotor\n```\nDo note some modules are installed into python by default such as `random` and `os` so if it says `No matching distribution found for...` then likely this is preinstalled into python.\n**Hope this helps you!**"
            },
            "requirements.txt": {
                "triggers": ["no such file or directory", "requirements.txt",
                             "defaulting to user installation because normal site-packages is not writeable"],
                "prevents": ["make sure", "include", "put", "keep", "-s"],
                "response": "Oh no, sorry to hear that you are having issues with your discord bot hosting.\nThis is quite easy to fix with a `requirements.txt` file. Make sure your file is in the main folder/directory.\n\nYou will need to insert the module/thing you normally install with pip. For example discord.py you could use a `requirements.txt` file with the content of \n```\ndiscord.py\ndnspython\nmotor\n```\nDo note some modules are installed into python by default such as `random` and `os` so if it says `No matching distribution found for...` then likely this is preinstalled into python.\n**Hope this helps you!**"
            },
            "ipbanned": {
                "triggers": ["ip has been banned", "ip banned",
                             "banned from support", "i got ip banned"],
                "prevents": ["how to", "minecraft", "-s"],
                "response": "You have been banned by the looks of it. This usually happens when you input the wrong email/password multiple times. You can try to login from https://billing.plox.host and login with your billing account details(the ones you used to purchase the service/server). You can create a ticket there or access the support panel from there.\n**Hope this helps you!**"
            },
            "jarfileaccess": {
                "triggers": ["Unable to access jarfile"],
                "prevents": ["how to", "-s"],
                "response": "Ah yes the famous jarfile issues, make sure the file jar file is in the main/root folder and execute it. It won't work otherwise. \n If using minecraft hosting, if you are using a custom jar then refer to this guide: https://support.plox.host/en/knowledgebase/article/how-to-use-a-custom-jar.\n**Hope this helps!**"
            },
            "npminstall": {
                "triggers": ["npm package", "packages", "install an npm package", "npm's", "npms", "npm install"],
                "prevents": ["minecraft", "python", "pip", "-s"],
                "response": "Pst, pst. You. The solution is within this article https://support.plox.host/en/knowledgebase/article/how-to-setup-your-nodejs-discord-bot. It may be recommended to install this on your own computer using `npm install` then transfer the `package.json` over."
            },
            "lagfix": {
                "triggers": ["lagging alot", "laggin alot", "vanilla"],
                "prevents": ["vps", "-s"],
                "response": "The time has come, for you to learn. You should be using Paper or a fork of it such as Purpur.\nYes this does enable you to use plugins but comes with performance benefits.\n\nYou can select this by using the jar selection on the main multicraft panel of your server.Make sure you click save at the bottom and restart. **Make sure you install the correction version**, Minecraft will only let you install a version higher or the same version to avoid world corruption unless you want your world to be deleted.\n\nFor optimised configuration files please visit: https://discord.com/channels/346715007469355009/476634353808441344/831237483278237707"
            }
        }

        trigger = None
        prevent = None
        response = None
        category = None

        for category_s, main_value in support_messages.items():
            for sub_category_s, value in main_value.items():
                category = category_s

                data_trigger = self.check_trigger_message(main_value["triggers"], support_message_needed)
                data_prevents = self.check_trigger_message(main_value["prevents"], support_message_needed)
                if data_trigger and data_prevents is None:
                    response = main_value["response"]
                    await message.channel.send(response)
                    break

        if message.guild.id == 346715007469355009 and (
                trigger or prevent):  # Log the output to a channel if in the main server
            fluxed_logs = message.guild.get_channel(346715007469355009)
            await fluxed_logs.send(
                f"**Category**: {category}\n**Trigger:** {trigger}\n**Message that prevented it:** {prevent}\nMessage that generated it: \n```\n{message.content}\n```\n**Output:**\n{response}\n**Attachments:** {message.attachments}")

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
