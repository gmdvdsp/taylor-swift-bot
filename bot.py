import os
import datetime as time

import discord
from discord.ext import commands
# token: NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs

class Bot(commands.Bot):
    AUTHOR_EMBED_URL = "https://i.imgur.com/6DSv0Su.jpg"

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

    def seed_entries(self):
        def default_entries():
            def_user_configs = {"mention_on_listen":True}
            def_user_stats = {"cooldown":time.datetime(1,1,1,0,0), "listens":0, "configs":def_user_configs}
            return def_user_stats

        for member in self.get_all_members():
            if (not(member.id in self.data)):
                self.data[member.id] = {}
            self.data[member.id] = default_entries()

    # == HELPERS == 
    def embed_skeleton(self, arg):
        embed = discord.Embed(description=arg, color=0xFF0000)
        embed.set_author(name="Taylor Swift", icon_url=self.AUTHOR_EMBED_URL)
        return embed

    def update_entry(self, member, arg, val):
        if (not(member.id in self.data)):
            return
        if (arg in self.data[member.id]):
            print('in base')
            self.data[member.id][arg] = val
        elif (arg in self.data[member.id]['configs']):
            print('in config')
            self.data[member.id]['configs'][arg] = val

    def get_entry(self, member, arg):
        if (not(member.id in self.data)):
            return
        return self.data[member.id].get(arg, self.data[member.id]['configs'].get(arg, None))
        
bot = Bot()

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run('NTY5MjE1NDg2MDc2NjQ5NDg1.GkhadZ.Jn5r-8Qr3E-_OIC2wAIYqCF5ts3FnZDhQgn9fs')