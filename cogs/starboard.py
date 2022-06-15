import re
from bot import RED
import discord
from discord.ext import tasks, commands

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.starboard_data = {}
        self.seed_entries()

    def seed_entries(self):
        def default_entries():
            def_user_configs = {"channel":None, "reactions_until_add":1, "emoji":"✨"}
            return def_user_configs

        self.starboard_data = default_entries()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if ((str(payload.emoji) == self.starboard_data["emoji"]) and (payload.member.id != self.bot.user.id)):
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if (self.count_nonbot_reactions(message) >= self.starboard_data["reactions_until_add"]):
                await self.send_starboard(message, channel)

    @commands.group()
    async def starboard(self, context):
        if context.invoked_subcommand is None:
            await context.channel.send(embed=self.bot.embed_skeleton("Commands: emoji, channel, count"))

    @starboard.command()
    async def emoji(self, context):
        new_emoji = None
        await context.channel.send(embed=self.bot.embed_skeleton("Please react to this message with the emoji you want to trigger starboard functions."))

        def check(payload):
            if (payload.member == context.author):
                nonlocal new_emoji
                new_emoji = str(payload.emoji)
                return True
            return False            

        await self.bot.wait_for('raw_reaction_add', timeout=60.0, check=check)
        self.starboard_data["emoji"] = new_emoji
        await context.channel.send(embed=self.bot.embed_skeleton("I've changed the starboard reaction emoji to: {}".format(self.starboard_data["emoji"])))
    
    @starboard.command()
    async def channel(self, context):
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

    @starboard.command()
    async def count(self, context):
        await context.channel.send(embed=self.bot.embed_skeleton("Please respond with how many reactions I should wait for before I star a post."))

        def check(message):
            if (message.author == context.author):
                if (re.match("^\d+$", message.content)):
                    self.starboard_data["reactions_until_add"] = message.content
                    return True
            return False            

        await self.bot.wait_for('message', timeout=60.0, check=check)
        await context.channel.send(embed=self.bot.embed_skeleton("I've set the reactions needed to star a post to: {}".format(self.starboard_data["reactions_until_add"])))

    # == HELPERS ==
    def count_nonbot_reactions(self, message):
        ret = 0
        for emoji in message.reactions:
            if (self.starboard_data["emoji"] == str(emoji)):
                ret = emoji.count
                if (emoji.me):
                    ret -= 1
        return ret

    async def send_starboard(self, message, original_channel):
        def process_image():
            if (message.attachments):
                return message.attachments[0]
        
        def process_embed(arg):
            if (message.embeds):
                return message.embeds[0]
            else: 
                return arg

        embed = discord.Embed(description=message.content, color=RED)
        embed = process_image()
        embed = process_embed(embed)
        
        embed.set_author(name=str(message.author), icon_url=message.author.avatar_url)
        embed.add_field(name=u'\u200b', value="[**Click here to jump to this message!**]({})".format(message.jump_url + "\n"))
        embed.set_footer(text="MessageID: {}".format(message.id))
        embed.timestamp = message.created_at
        sent = await self.starboard_data["channel"].send(content="{} **{}** | {}".format(self.starboard_data["emoji"], self.count_nonbot_reactions(message), original_channel.mention), embed=embed)
        await sent.add_reaction(self.starboard_data["emoji"])

def setup(bot):
    bot.add_cog(Starboard(bot))
