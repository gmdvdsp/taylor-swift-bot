import os

from cogs.classes.member_data import Member_data

import discord
from discord.ext import commands
# token: NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ts ", intents=discord.Intents.all())
        self.data = {} 

    '''
    In a practical environment, these are never being used.
    @bot.command()
    async def load(context, extension):
        bot.load_extension(f'cogs.{extension}')

    @bot.command()
    async def unload(context, extension):
        bot.unload_extension(f'cogs.{extension}')
    '''

bot = Bot()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run('NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs')