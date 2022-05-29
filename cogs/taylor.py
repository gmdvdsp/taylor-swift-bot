from cogs.classes.member_data import Member_data

import datetime as time

import discord
from discord.ext import tasks, commands

class Taylor(commands.Cog):
    # Must be this many seconds after last exposure for user to get re-exposed (in seconds).
    EXPOSURE_TIMER = 86400

    def __init__(self, bot):
        self.bot = bot
        #self.data = {}

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
                    self.bot.data[member.id].cooldown = time.datetime.now()
                else:
                    if (self.bot.data[member.id].cooldown > time.datetime.now()):
                        continue
                for activity in member.activities:
                    if (isinstance(activity, discord.Spotify)):
                        if (activity.artist == "Taylor Swift"):
                            self.bot.data[member.id].cooldown = time.datetime.now() + time.timedelta(seconds=self.EXPOSURE_TIMER)
                            await self.send_embed(context, activity)    

    @commands.Cog.listener()
    async def send_embed(self, context, spotify):
        embed = discord.Embed(title="Thank you!", description=("🚨 askl;dfjasdg swifteie!!~ 🌟 omg swiftie alert!!! 😩 🚨 we STAN `11 ~!>>>>>> SWIFTIE"), color=0xFF0000)
        embed.set_author(name="Taylor Swift", icon_url="https://i.imgur.com/6DSv0Su.jpg")
        embed.set_thumbnail(url=spotify.album_cover_url)
        embed.add_field(name="Make sure you stream...", value=(spotify.title + " - " + spotify.album), inline=False)
        await context.channel.send(embed=embed)

    # == HELPERS ==
    def add_entry(self, member):
        self.bot.data[member.id] = Member_data()

    # == DEBUG ==
    @commands.command()
    async def dbp_data(self, context):
        await context.channel.send(self.bot.data)

def setup(bot):
    bot.add_cog(Taylor(bot))        