import pprint
import discord
from discord.ext import commands

class Misc(commands.Cog):
    default = True

    def __init__(self, bot):
        self.bot = bot

    # == MISC COMMANDS ==
    @commands.command()
    async def say(self, context, *args):
        await context.channel.send(embed=self.bot.embed_skeleton(("{}".format(" ".join(args)))))

    # == CONFIG ==
    @commands.command()
    async def prefix(self, context, arg):
        self.bot.command_prefix = arg
        await context.channel.send(embed=self.bot.embed_skeleton(("I've changed the global command prefix to: {}".format(arg))))

    # == DEBUG ==
    @commands.command()
    async def db_printdata(self, context):
        msg = pprint.pformat(self.bot.data)
        await context.channel.send(msg)

    @commands.command()
    async def db_count_users(self, context):
        i = 0
        for member in self.bot.get_all_members():
            if (not(member.bot)):
                print(member)
                i += 1
        await context.channel.send(i)

    @commands.command()
    async def db_ids(self, context):
        for member in self.bot.get_all_members():
            if (not(member.bot)):
                await context.channel.send(('User: {}, {}'.format(member.name, member.id)))

    @commands.command()
    async def db_members(self, context):
        for member in self.bot.get_all_members():
            if (not(member.bot)):
                await context.channel.send(('User: {}, {}'.format(member.name, member.activities)))

    @commands.command()
    @commands.is_owner()
    async def db_shutdown(self, context):
        await self.bot.close()
        
def setup(bot):
    bot.add_cog(Misc(bot))