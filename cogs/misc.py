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

    @commands.command()
    async def mention(self, context):
        embed = await context.channel.send(embed=self.bot.embed_skeleton(("Should I mention you when I see you listening to my songs?")))
        await embed.add_reaction("😍")
        await embed.add_reaction("😭")

        def check(reaction, user):
            if (user == context.author):
                if (str(reaction.emoji) == "😍"):
                    self.bot.update_entry(user, 'mention_on_listen', True)
                    return True
                elif (str(reaction.emoji) == "😭"):
                    self.bot.update_entry(user, 'mention_on_listen', False)
                    return True
            return False

        await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        await context.channel.send(embed=self.bot.embed_skeleton("Mentions set to: {}".format(self.bot.get_entry(context.author, 'mention_on_listen'))))

    # == DEBUG ==
    @commands.Cog.listener()
    async def on_ready(self):
        print('Registered as {0.user}'.format(self.bot))

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