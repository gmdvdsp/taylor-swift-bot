from cogs.classes.member_data import Member_data

import datetime as time

import discord
from discord.ext import tasks, commands

class Music_detection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Must be this many seconds after last exposure for user to get re-exposed (in seconds). DEFAULT: 86400
        self.exposure_timer = 86400

    # == COMMANDS ==
    @commands.command()
    # Monitor (reads m for ease of testing), change back for releases.
    async def m(self, context):
        if (not(self.monitor_task.is_running())):
            await self.monitor_task.start(context)

    @tasks.loop(seconds=5.0)
    async def monitor_task(self, context):
        for member in self.bot.get_all_members():
            if (not(member.bot) and (member.status != discord.Status.offline)):
                if (not(member.id in self.bot.data)):
                    self.add_entry(member)
                else:
                    if (self.bot.data[member.id].cooldown > time.datetime.now()):
                        continue
                for activity in member.activities:
                    if (isinstance(activity, discord.Spotify)):
                        if ("Taylor Swift" in activity.artist):
                            self.bot.data[member.id].cooldown = time.datetime.now() + time.timedelta(seconds=self.exposure_timer)
                            self.bot.data[member.id].listens += 1
                            await self.send_embed(context, activity)  

    @commands.command()
    async def listens(self, context, arg: discord.Member):
        await context.channel.send(self.bot.data[arg.id].listens)

    # == HELPERS ==
    def add_entry(self, member):
        self.bot.data[member.id] = Member_data()

    async def send_embed(self, context, spotify):
        embed = discord.Embed(title="Thank you!", description=("🚨 askl;dfjasdg swifteie!!~ 🌟 omg swiftie alert!!! 😩 🚨 we STAN `11 ~!>>>>>> SWIFTIE"), color=0xFF0000)
        embed.set_author(name="Taylor Swift", icon_url="https://i.imgur.com/6DSv0Su.jpg")
        embed.set_thumbnail(url=spotify.album_cover_url)
        embed.add_field(name="I've recorded you listening to me...", value=("{} times!".format(self.bot.data[context.author.id].listens)), inline=False)
        embed.add_field(name="Make sure you stream!", value=(spotify.title + " - " + spotify.album), inline=False)
        await context.channel.send(content="{}!".format(context.author.mention) ,embed=embed)

    # == CONFIG ==
    '''
    Can someone who wants to deal with args -> seconds conversion deal with this :sob:
    @commands.command()
    async def set_exposure_timer(self, context, arg):
        self.exposure_timer = time.datetime.strptime(arg, "%-S")
        await context.channel.send('Changed global exposure timer to: {}, in seconds'.format(arg))
    '''    

    # == DEBUG ==
    @commands.command()
    async def db_data(self, context):
        await context.channel.send(self.bot.data)

def setup(bot):
    bot.add_cog(Music_detection(bot))        