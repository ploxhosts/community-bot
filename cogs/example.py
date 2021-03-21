from discord.ext import commands
import random
import tools


class Example(commands.Cog):
    """This is an example command"""  # Make sure to have a description of what it does up here

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.command(name="example", aliases=["examples"],
                      usage="example <text>")  # You can run it as ?example or ?examples and make sure to have the full usage of how the command gets executed. Do not include the prefix!
    @tools.has_perm(manage_messages=True)
    async def example_cmd(self, ctx, *, text):
        await ctx.send(f"`{text}` - Sent by {ctx.author.name}")  # Send the text back

    # Need to use a database to store information?
    # Store it in a separate collection

    async def save_db(self):
        db = self.database.bot  # Must be set to this as only database is being used is bot
        collection = db.exampleCollection  # Set the collection
        await collection.insert_one({"id": random.randint(1, 1000000), "text": "Hello world!"})  # How to insert a new data

    async def update_db(self, postid):
        db = self.database.bot  # Must be set to this as only database is being used is bot
        collection = db.exampleCollection  # Set the collection
        await collection.update_one({"id": postid},
                              {"$set": {
                                  "text": "Goodbye world..."}})  # Search by the field of id by the variable postid and set teh text to Goodbye world

    async def get_db(self, postid):
        db = self.database.bot  # Must be set to this as only database is being used is bot
        collection = db.exampleCollection  # Set the collection
        data = await collection.find_one({"id": postid})  # Search by the field of id by the variable postid
        print(data)  # Get the document returned

    async def delete_db(self, postid):
        db = self.database.bot  # Must be set to this as only database is being used is bot
        collection = db.exampleCollection  # Set the collection
        await collection.delete_one({"id": postid})  # Search by the field of id by the variable postid and delete it


def setup(bot):
    bot.add_cog(Example(bot))
