import os
import datetime as time

import database
import discord
from discord.ext import commands
# token: NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs

AUTHOR_EMBED_URL = "https://i.imgur.com/6DSv0Su.jpg"
RED = 0xFF0000

TABLENAME_USERS = 'users'
TABLENAME_MISC_VARS = 'misc_vars'
TABLENAME_WORDLE_EMOJIS = 'wordle_letter_emojis'

COLUMNS_USER = ('user_id INTEGER PRIMARY KEY',
                'username TEXT',
                'wordle_current_game TEXT'
                )
COLUMNS_WORDLE_EMOJIS = ('id INTEGER PRIMARY KEY', 'name TEXT')
EMOJI_SERVER_IDS = [582652440642584647, 994102946163871816]

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ts ", intents=discord.Intents.all())
        # Flag for on_ready, which can run multiple times.
        self.firstRun = True

    @commands.Cog.listener()
    async def on_ready(self):
        if self.firstRun:
            self.initialize_databases()
            print('Hooked onto database.')
            self.firstRun = False
    
    def initialize_databases(self):
        database.delete_entry(TABLENAME_USERS, 'user_id', 979850109955227721)
        database.create_table(TABLENAME_USERS, COLUMNS_USER)
        for member in self.get_all_members():
            if (not(member.bot)):
                database.create_entry(TABLENAME_USERS, (member.id, member.name, None))

        # Icky that this initializes here and not in wordle.py, change
        database.create_table(TABLENAME_WORDLE_EMOJIS, COLUMNS_WORDLE_EMOJIS)
        for guild_id in EMOJI_SERVER_IDS:
            for emoji in self.get_guild(guild_id).emojis:
                database.create_entry(TABLENAME_WORDLE_EMOJIS, (emoji.id, emoji.name))

    # == HELPERS == 
    def embed_skeleton(self, arg):
        embed = discord.Embed(description=arg, color=RED)
        embed.set_author(name="Taylor Swift", icon_url=AUTHOR_EMBED_URL)
        return embed
        
bot = Bot()
database.create_table('misc_vars', ('name text PRIMARY KEY', 'value text'))

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run('NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs')