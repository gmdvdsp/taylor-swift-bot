import discord
from discord.ext import tasks, commands

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starboard_data = {}

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if (str(payload.emoji) == "✨"):
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await channel.send(message.jump_url)

def setup(bot):
    bot.add_cog(Starboard(bot))
