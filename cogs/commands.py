import discord
from discord.ext import commands
import random
from datetime import datetime
import requests

import tools


class Commands(commands.Cog):
    """Fun and misc commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="poll", aliases=["polls"], usage="poll <question>")
    @tools.has_perm()
    async def poll(self, ctx, *, text: str):
        await ctx.message.delete()
        embed = discord.Embed(color=0x36a39f)
        embed.add_field(name=f"Poll:", value=f"{text}", inline=True)
        msg = await ctx.send(embed=embed)
        emoji = '\N{THUMBS UP SIGN}'
        await msg.add_reaction(emoji)
        emoji2 = '\N{THUMBS DOWN SIGN}'
        await msg.add_reaction(emoji2)

    @commands.command(name="add", aliases=["addition"], usage="addition <num1> <num2>")
    @tools.has_perm()
    async def add(self, ctx, a: int, b: int):
        await ctx.send(a + b)

    @commands.command(name="multiply", aliases=["times"], usage="multiply <num1> <num2>")
    @tools.has_perm()
    async def multiply(self, ctx, a: int, b: int):
        await ctx.send(a * b)

    @commands.command(name="flip", usage="flip")
    @tools.has_perm()
    async def flip(self, ctx):
        choice = ["tails", "heads"]
        roll = random.choice(choice)
        await ctx.send(f"Your coin flip got a `{roll}` !")

    @commands.command(name="roll", usage="roll")
    @tools.has_perm()
    async def roll(self, ctx):
        roll = random.randint(1, 6)
        await ctx.send(f"Your rolled a `{roll}` !")

    @commands.command(name="joke", aliases=["givemejoke", "dadjoke"], usage="joke")
    @tools.has_perm()
    async def joke(self, ctx):
        res = requests.get("https://icanhazdadjoke.com/", headers={'Accept': 'text/plain',
                                                                   'User-Agent': 'Ploxy (https://github.com/PloxHost-LLC/community-bot)'})
        await ctx.send(res.text)

    @commands.command(name="greet", aliases=["sayhi"], usage="greet")
    @tools.has_perm()
    async def greet(self, ctx):
        author = ctx.message.author
        greetings = [":smiley: :wave: Hello, there!", "Hello!", f"Hello {author.mention}!"]
        choice = random.choice(greetings)
        await ctx.send(choice)

    @commands.command(name="roles", usage="roles")
    @tools.has_perm()
    async def roles(self, ctx):
        # await ctx.send(embed=discord.Embed.from_dict({'title':f'{ctx.guild.name} roles', 'fields':[{'name':r.name, 'value':str(len(r.members))} for r in ctx.guild.roles]}))
        await ctx.send(embed=discord.Embed.from_dict({'title': f'{ctx.guild.name} roles',
                                                      'fields': [{'name': r.name, 'value': str(len(r.members))} for r in
                                                                 ctx.guild.roles], 'color': 0x36a39f}))
        # for role in ctx.guild.roles:
        # await ctx.send(f"{role}: {len(role.members)}")

    @commands.command(name="ping", aliases=["rolelist"], usage="ping")
    @tools.has_perm()
    async def ping(self, ctx):
        times = random.randint(1, 10)
        if times in (1, 5, 10):
            await ctx.send(f"Ding Dong!`{round(self.bot.latency * 1000)} ms`")
        else:
            await ctx.send(f"Pong!`{round(self.bot.latency * 1000)} ms`")

    @commands.command(name="users", aliases=["userlist"], usage="users")
    @tools.has_perm()
    async def users(self, ctx):
        online_members = 0
        bots = 0
        for user in ctx.guild.members:
            if user.status != discord.Status.offline:
                online_members += 1
            if user.bot:
                bots += 1
        embed = discord.Embed(color=0x22ff18)
        embed.add_field(name=f"Total members",
                        value=f"There is currently {len(list(ctx.guild.members))} people on the server! ",
                        inline=False)
        embed.add_field(name=f"Online Members",
                        value=f"There is currently {online_members} people online on the server! ", inline=False)
        embed.add_field(name=f"Channels", value=f"There is {len(list(ctx.guild.channels))} channels on this server!",
                        inline=False)
        embed.add_field(name=f"Bots", value=f"There is {bots} bots on this server!  ", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="iq", aliases=["getiq"], usage="iq @user")
    @tools.has_perm()
    async def iq(self, ctx, user: discord.Member = ""):
        if user in ["", " "]:
            user = ctx.message.author
        IQ = random.randint(0, 250)
        await ctx.send(f"{user.mention} has got {IQ} IQ")

    @commands.command(name="love", aliases=["marrychance"], usage="love @user1 @user2")
    @tools.has_perm()
    async def love(self, ctx, man: discord.Member, girl: discord.Member):
        chance = random.randint(0, 100)
        man = man
        girl = girl
        await ctx.send(
            f"{man} and {girl} have a {chance}%  chance of dating! Your priest {ctx.author.name} wanted to see the love in play.")

    @commands.command(name="rps", aliases=["rockpaperscissors"], usage="rps <R|P|S>")
    @tools.has_perm()
    async def rps(self, ctx, *, message):
        rps = ["Rock", "Paper", "Scissors"]
        word = message.lower()
        rocks = ["rock", "roc", "rok", "r"]
        papers = ["paper", "papers", "papper", "papar", "p"]
        scissors = ["scissors", "scisors", "ssisors", "csissors", "s", "sissors", "siscors"]

        choices = ["rock", "roc", "rok", "r", "paper", "papers", "papper", "papar", "p", "scissors", "scisors",
                   "ssisors", "csissors", "s", "sissors", "siscors"]
        choice = random.choice(rps)
        if word not in choices:
            return await ctx.send("You must use Rock(r), Paper(p) or scissors(s)! Please use ?`rps rock`")

        if word in rocks and choice == "Paper":
            await ctx.send("You chose: `rock`\nBot chose: `paper`\nResult:You lose!")
        elif word in rocks and choice == "Scissors":
            await ctx.send("You chose: `rock`\nBot chose: `scissors`\nResult:You win!")
        elif word in rocks and choice == "Rock":
            await ctx.send("You chose: `rock`\nBot chose: `rock`\nResult:Draw!")
        elif word in papers and choice == "Paper":
            await ctx.send("You chose: `paper`\nBot chose: `paper`\nResult:Draw!")
        elif word in papers and choice == "Scissors":
            await ctx.send("You chose: `paper`\nBot chose: `scissors`\nResult:You lose!")
        elif word in papers and choice == "Rock":
            await ctx.send("You chose: `paper`\nBot chose: `rock`\nResult:You win!")
        elif word in scissors and choice == "Paper":
            await ctx.send("You chose: `scissors`\nBot chose `paper`\nResult:You win!")
        elif word in scissors and choice == "Scissors":
            await ctx.send("You chose `scissors`\nBot chose: `scissors`\nResult:Draw!")
        elif word in scissors and choice == "Rock":
            await ctx.send("You chose `scissors`\nBot chose: `rock`\nResult:You lose!")

    @commands.command(name="googleit", aliases=["helpmegoogle"], usage="googleit how to make cake")
    @tools.has_perm()
    async def googleit(self, ctx, *, question: str):
        query = "+".join(question.split())
        await ctx.send(f"Open this:\nhttps://lmgtfy.com/?q={query}&iie=1")

    @commands.command(name="8ball", aliases=["eightball"], usage="8ball am I smart?")
    @tools.has_perm()
    async def eightball(self, ctx, *, question):
        await ctx.message.add_reaction("☑️")
        # Random at the moment might make some complicated ai for it
        question_response = random.choice([
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Deadly serious",
            "Outlook good",
            "Most definitely",
            "Signs point to yes", "Reply hazy try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "I just experienced a short down time, ask again", "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
            "Computer says no",
            "I just googled it and it said no"
        ])

        colour_choice = [0x36393F, 0x99aab5, 0x7289da, 0x546e7a, 0x546e7a, 0x979c9f, 0x979c9f, 0x607d8b, 0x607d8b,
                         0x95a5a6, 0x95a5a6, 0x992d22, 0xe74c3c, 0xa84300, 0xe67e22, 0xc27c0e, 0xf1c40f, 0xad1457,
                         0xe91e63, 0x71368a, 0x9b59b6, 0x206694, 0x3498db, 0x1f8b4c, 0x2ecc71, 0x11806a, 0x1abc9c]
        embed = discord.Embed(colour=random.choice(colour_choice), type="rich", timestamp=datetime.now())
        embed.set_author(name=ctx.author.name,
                         icon_url=ctx.author.avatar_url)
        embed.add_field(name="**8ball**", value=f":question: {question}\n:8ball: {question_response}", inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Commands(bot))
