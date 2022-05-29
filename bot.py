import os
import discord
from discord.ext import commands
# token: NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def load(context, extension):
    bot.load_extension(f'cogs.{extension}')

@bot.command()
async def unload(context, extension):
    bot.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run('NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs')