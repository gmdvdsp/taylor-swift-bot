import discord
from discord.ext import commands

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Registered as {0.user}'.format(self.bot))

    @commands.command()
    async def say(self, context, *args):
        await context.channel.send("{}".format(" ".join(args)))

    @commands.command()
    async def count_users(self, context):
        i = 0
        for member in self.bot.get_all_members():
            if (not(member.bot)):
                print(member)
                i += 1
        await context.channel.send(i)
        
def setup(bot):
    bot.add_cog(Misc(bot))