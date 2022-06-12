import discord
from discord.ext import tasks, commands

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starboard_data = {}
        self.seed_entries()

    def seed_entries(self):
        def default_entries():
            def_user_configs = {"channel":None, "reactions_until_add":1}
            return def_user_configs

        self.starboard_data = default_entries()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if (str(payload.emoji) == "✨"):
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await self.send_starboard(message)
    
    @commands.command()
    async def starboard_channel(self, context):
        await context.channel.send(embed=self.bot.embed_skeleton("Please tag the channel that you want me to post starred messages to."))

        def check(message):
            if (message.author == context.author):
                for channel in self.bot.get_all_channels():
                    if (channel in message.channel_mentions):
                        self.starboard_data["channel"] = channel
                        return True
            return False            

        await self.bot.wait_for('message', timeout=60.0, check=check)
        await context.channel.send(embed=self.bot.embed_skeleton("I've set the starboard channel to: {}".format(self.starboard_data["channel"].mention)))

    #@commands.command()
    #async def starboard_count(self, context):
    #    await context.channel.send(embed=self.bot.embed_skeleton("Please respond with how many reactions I should wait for before I star a post."))

    #    def check(message):
    #        if (message.author == context.author):
    #            if (message.content == )
    #        return False            

    #    await self.bot.wait_for('message', timeout=60.0, check=check)
    #    await context.channel.send(embed=self.bot.embed_skeleton("I've set the starboard channel to: {}".format(self.starboard_data["channel"].mention)))

    # == HELPERS ==
    async def send_starboard(self, message):
        def process_cases(arg):
            #if (message.embeds):
            #    
            if (message.attachments):
                arg.set_image(url=message.attachments[0])

        embed = discord.Embed(description=message.content, color=0xFF0000)
        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
        process_cases(embed)
        embed.add_field(name=u'\u200b', value="[**Click here to jump to this message!**]({})".format(message.jump_url + "\n"))
        embed.set_footer(text="MessageID: {}".format(message.id))
        embed.timestamp = message.created_at
        await self.starboard_data["channel"].send(embed=embed)

def setup(bot):
    bot.add_cog(Starboard(bot))
