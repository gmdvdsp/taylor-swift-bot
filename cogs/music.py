#from cogs.classes.member_data import Member_data

# BROKEN UNTIL I FINISH THE DATABASE

from calendar import c
import datetime as time

import discord
from discord.ext import tasks, commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Must be this many seconds after last exposure for user to get re-exposed (in seconds). DEFAULT: 86400
        self.exposure_timer = 5

    # == COMMANDS ==
    @commands.command()
    # Monitor (reads m for ease of testing), change back for releases.
    async def m(self, context):
        if (not(self.monitor_task.is_running())):
            await self.monitor_task.start(context)

    @tasks.loop(seconds=10.0)
    async def monitor_task(self, context):
        for member in self.bot.get_all_members():
            if (not(member.bot) and (member.status != discord.Status.offline)):
                if (self.bot.get_entry(member, 'cooldown') > time.datetime.now()):
                    continue
                for activity in member.activities:
                    if (isinstance(activity, discord.Spotify)):
                        if ("Taylor Swift" in activity.artist):
                            self.bot.update_entry(member, 'cooldown', time.datetime.now() + time.timedelta(seconds=self.exposure_timer))
                            self.bot.update_entry(member, 'listens', self.bot.get_entry(member, 'listens') + 1)
                            await self.send_taylor(context, activity)
                            continue  

    @commands.command()
    async def listens(self, context):
        await context.channel.send(embed=self.bot.embed_skeleton("I've seen you listening to my songs {} times. Thank you!".format(self.bot.get_entry(context.author, 'listens'))))

    # == HELPERS ==
    async def send_taylor(self, context, spotify):
        embed = discord.Embed(title="Thank you!", description=("🚨 askl;dfjasdg swifteie!!~ 🌟 omg swiftie alert!!! 😩 🚨 we STAN `11 ~!>>>>>> SWIFTIE"), color=0xFF0000)
        embed.set_author(name="Taylor Swift", icon_url="https://i.imgur.com/6DSv0Su.jpg")
        embed.set_thumbnail(url=spotify.album_cover_url)
        embed.add_field(name="I've recorded you listening to me...", value=("{} times!".format(self.bot.get_entry(context.author, 'listens'))), inline=False)
        embed.add_field(name="Make sure you stream!", value=(spotify.title + " - " + spotify.album), inline=False)
        await context.channel.send(content="{}".format(context.author.mention) ,embed=embed)

    # == CONFIG ==
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
    @commands.command()
    async def db_data(self, context):
        await context.channel.send(self.bot.data)

def setup(bot):
    bot.add_cog(Music(bot))        