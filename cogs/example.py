from discord.ext import commands
import random


class Example(commands.Cog):
    """This is an example command"""  # Make sure to have a description of what it does up here

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

    @commands.command(name="example", aliases=["examples"],
                      usage="example <text>")  # You can run it as ?example or ?examples and make sure to have the full usage of how the command gets executed. Do not include the prefix!
    async def example_cmd(self, ctx, *, text):
        ctx.send(f"`{text}`")  # Send the text back

    # Need to use a database to store information?
    # Store it in a separate collection

    def save_db(self):
        db = self.database.bot  # Must be set to this as only database is being used is bot
        collection = db.exampleCollection  # Set the collection
        collection.insert_one({"id": random.randint(1, 1000000), "text": "Hello world!"})  # How to insert a new data

    def update_db(self, postid):
        db = self.database.bot  # Must be set to this as only database is being used is bot
        collection = db.exampleCollection  # Set the collection
        collection.update_one({"id": postid},
                              {"$set": {
                                  "text": "Goodbye world..."}})  # Search by the field of id by the variable postid and set teh text to Goodbye world

    def get_db(self, postid):
        db = self.database.bot  # Must be set to this as only database is being used is bot
        collection = db.exampleCollection  # Set the collection
        data = collection.find_one({"id": postid})  # Search by the field of id by the variable postid
        print(data)  # Get the document returned

    def delete_db(self, postid):
        db = self.database.bot  # Must be set to this as only database is being used is bot
        collection = db.exampleCollection  # Set the collection
        collection.delete_one({"id": postid})  # Search by the field of id by the variable postid and delete it


def setup(bot):
    bot.add_cog(Example(bot))
