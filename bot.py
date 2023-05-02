import os
import datetime as time

import discord
from discord.ext import commands

AUTHOR_EMBED_URL = "https://i.imgur.com/6DSv0Su.jpg"
RED = 0xFF0000

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="ts ", intents=discord.Intents.all())
        self.user_data = {}
        self.seed_entries()

    '''
    In a practical environment, these are never being used.
    @bot.command()
    async def load(context, extension):
        bot.load_extension(f'cogs.{extension}')

    @bot.command()
    async def unload(context, extension):
        bot.unload_extension(f'cogs.{extension}')
    '''
    
    def seed_entries(self):
        def default_entries():
            def_user_configs = {"mention_on_listen":True}
            def_user_stats = {"cooldown":time.datetime(1,1,1,0,0), "listens":0, "configs":def_user_configs}
            return def_user_stats

        for member in self.get_all_members():
            if (not(member.id in self.user_data)):
                self.user_data[member.id] = {}
            self.user_data[member.id] = default_entries()

    # == HELPERS == 
    def embed_skeleton(self, arg):
        embed = discord.Embed(description=arg, color=RED)
        embed.set_author(name="Taylor Swift", icon_url=AUTHOR_EMBED_URL)
        return embed

    def update_entry(self, member, arg, val):
        if (not(member.id in self.user_data)):
            return
        if (arg in self.user_data[member.id]):
            self.user_data[member.id][arg] = val
        elif (arg in self.user_data[member.id]['configs']):
            self.user_data[member.id]['configs'][arg] = val

    def get_entry(self, member, arg):
        if (not(member.id in self.user_data)):
            return
        return self.user_data[member.id].get(arg, self.user_data[member.id]['configs'].get(arg, None))
        
bot = Bot()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(#BOT KEY#)
