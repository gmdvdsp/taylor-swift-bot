import discord
from discord.ext import commands

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # == MISC COMMANDS ==
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
        print(i)

    # == CONFIG ==
    @commands.command()
    async def prefix(self, context, arg):
        self.bot.command_prefix = arg
        await context.channel.send('Changed global command prefix to: {}'.format(arg))

    # == DEBUG ==
    @commands.Cog.listener()
    async def on_ready(self):
        print('Registered as {0.user}'.format(self.bot))

    @commands.command()
    async def db_ids(self, context):
        for member in self.bot.get_all_members():
            if (not(member.bot)):
                print('User: {}, {}'.format(member.name, member.id))

    @commands.command()
    async def db_members(self, context):
        for member in self.bot.get_all_members():
            if (not(member.bot)):
                print('User: {}, {}'.format(member.name, member.activities))

    @commands.command()
    @commands.is_owner()
    async def db_shutdown(self, context):
        await self.bot.close()
        
def setup(bot):
    bot.add_cog(Misc(bot))