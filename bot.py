import sqlite3

import os
import datetime as time

import database
import discord
from discord.ext import commands
# token: NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs

AUTHOR_EMBED_URL = "https://i.imgur.com/6DSv0Su.jpg"
RED = 0xFF0000
# All the USER_COLUMNS associated with users; are created on bot-ready.
USER_COLUMNS = ('id INTEGER PRIMARY KEY', 'username TEXT', 'messages_sent INTEGER')

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ts ", intents=discord.Intents.all())
        # Flag for on_ready, which can run multiple times.
        self.firstRun = True

    @commands.Cog.listener()
    async def on_ready(self):
        print('Registered as {0.user}'.format(self))
        if self.firstRun:
            self.initialize_databases()
            self.firstRun = False
    
    def initialize_databases(self):
        database.create_table('users', USER_COLUMNS)
        for member in self.get_all_members():
            database.create_entry('users', (member.id, member.name, 0))
        database.create_table('misc_vars', ('name text PRIMARY KEY', 'value text'))

    # == HELPERS == 
    def embed_skeleton(self, arg):
        embed = discord.Embed(description=arg, color=RED)
        embed.set_author(name="Taylor Swift", icon_url=AUTHOR_EMBED_URL)
        return embed
        
bot = Bot()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run('NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs')