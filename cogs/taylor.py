import datetime as time

import discord
from discord.ext import tasks, commands

class Taylor(commands.Cog):
    # Must be this many seconds after last exposure for user to get re-exposed (in seconds).
    COOLDOWN = 86400

    def __init__(self, bot):
        self.bot = bot
        # {k = user_id, v = {cooldown, num_times_exposed}}
        self.member_data = {}

    # == COMMANDS ==

    @commands.command()
    async def monitor(self, context):
        await self.monitor_task.start(context)

    @tasks.loop(seconds=5.0)
    async def monitor_task(self, context):
        for member in self.bot.get_all_members():
            if (not(member.bot) and (member.status != discord.Status.offline)):
                if (not(member.id in self.member_data)):
                    self.member_data[member.id] = time.datetime.now()
                else:
                    if (self.member_data.get(member.id) > time.datetime.now()):
                        continue
                for activity in member.activities:
                    if (isinstance(activity, discord.Spotify)):
                        if (activity.artist == "Taylor Swift"):
                            self.member_data[member.id] = time.datetime.now() + time.timedelta(seconds=self.COOLDOWN)
                            await self.send_embed(context, activity)    

    @commands.Cog.listener()
    async def send_embed(self, context, spotify):
        embed = discord.Embed(title="Thank you!", description=("🚨 askl;dfjasdg swifteie!!~ 🌟 omg swiftie alert!!! 😩 🚨 we STAN `11 ~!>>>>>> SWIFTIE"), color=0xFF0000)
        embed.set_author(name="Taylor Swift", icon_url="https://i.imgur.com/6DSv0Su.jpg")
        embed.set_thumbnail(url=spotify.album_cover_url)
        embed.add_field(name="Make sure you stream...", value=(spotify.title + " - " + spotify.album), inline=False)
        await context.channel.send(embed=embed)

    # == DEBUG ==
    @commands.command()
    async def debug_show_member_data(self, context):
        await context.channel.send(self.member_data)

def setup(bot):
    bot.add_cog(Taylor(bot))        