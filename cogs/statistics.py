import sqlite3

import discord
from discord.ext import commands

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Attributes

    @commands.Cog.listener()
    async def on_message(self, message):
        i = 1
            
def setup(bot):
    bot.add_cog(Statistics(bot))