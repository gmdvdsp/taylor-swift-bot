import re
from bot import TABLENAME_MISC_VARS, RED
import database

import discord
from discord.ext import commands

TABLENAME_CONFIG = 'starboard_config'
TABLENAME_STARRED_MESSAGES = 'starboard_starred_messages'

COLUMNS_STARRED_MESSAGES = ('message_id integer PRIMARY KEY', 'channel_id integer')
COLUMNS_CONFIG = ('config PRIMARY KEY', 'channel_id INTEGER', 'reactions_until_add INTEGER', 'emoji TEXT', 'reactions_until_condense INTEGER')

DEFAULT_CONFIG = (0, -1, 1, "✨", 3)

class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_database()

    def initialize_database(self):
        database.create_table(TABLENAME_CONFIG, COLUMNS_CONFIG)
        database.create_table(TABLENAME_STARRED_MESSAGES, COLUMNS_STARRED_MESSAGES)

        database.create_entry(TABLENAME_CONFIG, DEFAULT_CONFIG)
        database.create_entry(TABLENAME_MISC_VARS, ('starboard_until_condense', 0))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, event):
        if (event.member.id == self.bot.user.id):
            return
        
        if (str(event.emoji) == database.get_entry(TABLENAME_CONFIG, 'emoji', 'config', 0)):
            channel = self.bot.get_channel(event.channel_id)
            message = await channel.fetch_message(event.message_id)
            if (self.count_nonbot_reactions(message) >= database.get_entry(TABLENAME_CONFIG, 'reactions_until_add', 'config', 0)):
                await self.send_starboard(message, channel)

    def count_nonbot_reactions(self, message):
        ret = 0
        for emoji in message.reactions:
            if (database.get_entry(TABLENAME_CONFIG, 'emoji', 'config', 0) == str(emoji)):
                ret = emoji.count
                if (emoji.me):
                    ret = 0
                return ret
        return ret

    @commands.group()
    async def starboard(self, context):
        if context.invoked_subcommand is None:
            await context.channel.send(embed=self.bot.embed_skeleton("Commands: emoji, channel, count"))

    @starboard.command()
    async def channel(self, context):
        updated_channel = self.bot.get_channel(database.get_entry(TABLENAME_CONFIG, 'channel_id', 'config', 0))
        await context.channel.send(embed=self.bot.embed_skeleton("Please tag the channel that you want me to post starred messages to."))

        def check(message):
            if (message.author == context.author):
                for channel in self.bot.get_all_channels():
                    if (channel in message.channel_mentions):
                        nonlocal updated_channel
                        updated_channel = channel
                        database.update_entry(TABLENAME_CONFIG, 'channel_id', 'config', 0, channel.id)
                        return True
            return False            

        await self.bot.wait_for('message', timeout=60.0, check=check)
        await context.channel.send(embed=self.bot.embed_skeleton("I've set the starboard channel to: {}".format(updated_channel.mention)))

    @starboard.command()
    async def condense(self, context):
        if (int(database.get_entry(TABLENAME_MISC_VARS, 'value', 'name', 'starboard_until_condense')) == 0):
            return

        for message_tuple in database.get_all(TABLENAME_STARRED_MESSAGES):
            message_id = message_tuple[0]
            message_channel_id = message_tuple[1]

            channel = self.bot.get_channel(message_channel_id)
            message = await channel.fetch_message(message_id)
            sent = await self.bot.get_channel(database.get_entry(TABLENAME_CONFIG, 'channel_id', 'config', 0)).send(content=message.content, embed=message.embeds[0])
            for reaction in message.reactions:
                await sent.add_reaction(reaction)

            await message.delete()
            database.delete_entry(TABLENAME_STARRED_MESSAGES, 'message_id', message_id)
            database.create_entry(TABLENAME_STARRED_MESSAGES, (message_id, message_channel_id))
        
        await sent.pin()

    @starboard.command()
    async def count(self, context):
        updated_count = database.get_entry(TABLENAME_CONFIG, 'reactions_until_add', 'config', 0)
        await context.channel.send(embed=self.bot.embed_skeleton("Please respond with how many reactions I should wait for before I star a post."))

        def check(message):
            if (message.author == context.author):
                if (re.match("^\d+$", message.content)):
                    database.get_entry(TABLENAME_CONFIG, 'reactions_until_add', 'config', int(message.content))
                    return True
            return False            

        await self.bot.wait_for('message', timeout=60.0, check=check)
        await context.channel.send(embed=self.bot.embed_skeleton("I've set the reactions needed to star a post to: {}".format(updated_count)))

    @starboard.command()
    async def frequency(self, context):
        updated_frequency = database.get_entry(TABLENAME_CONFIG, 'reactions_until_condense', 'config', 0)
        await context.channel.send(embed=self.bot.embed_skeleton("Please respond with how many newly starred messages I should wait for before I repost all starred messages for readability.\n\
        If you don't know what starboard condensation is, use the help command!\n Please also note that starboard condensation can be done at any time with the command: (prefix) starboard condense"))

        def check(message):
            if (message.author == context.author):
                if (re.match("^\d+$", message.content)):
                    database.update_entry(TABLENAME_CONFIG, 'reactions_until_condense', 'config', 0, int(message.content))
                    database.update_entry(TABLENAME_MISC_VARS, 'starboard_until_condense', 'config', 0, 0)
                    return True
            return False            

        await self.bot.wait_for('message', timeout=60.0, check=check)
        await context.channel.send(embed=self.bot.embed_skeleton("I've set the starboard condense frequency to: {}".format(updated_frequency)))

    @starboard.command()
    async def emoji(self, context):
        updated_emoji = database.get_entry(TABLENAME_CONFIG, 'emoji', 'config', 0)
        await context.channel.send(embed=self.bot.embed_skeleton("Please react to this message with the emoji you want to trigger starboard functions."))

        def check(payload):
            if (payload.member == context.author):
                nonlocal updated_emoji
                updated_emoji = str(payload.emoji)
                return True
            return False            

        await self.bot.wait_for('raw_reaction_add', timeout=60.0, check=check)
        database.update_entry(TABLENAME_CONFIG, 'emoji', 'config', 0, updated_emoji)
        await context.channel.send(embed=self.bot.embed_skeleton("I've changed the starboard reaction emoji to: {}".format(updated_emoji)))

    async def send_starboard(self, original_message, original_channel):
        embed = discord.Embed(description=original_message.content, color=RED)
        star_channel = self.bot.get_channel(database.get_entry(TABLENAME_CONFIG, 'channel_id', 'config', 0))
        emoji = database.get_entry(TABLENAME_CONFIG, 'emoji', 'config', 0)

        if (original_message.attachments):
            if (original_message.attachments[0].content_type.startswith("image")):
                embed.set_image(url=original_message.attachments[0].url)
            else:
                embed.description = original_message.attachments[0].filename
        if (original_message.embeds):
            if (original_message.embeds[0].video == discord.Embed.Empty):   
                embed = original_message.embeds[0]

        embed.set_author(name=str(original_message.author), icon_url=original_message.author.avatar_url)
        embed.add_field(name=u'\u200b', value="[**Click here to jump to this message!**]({})".format(original_message.jump_url + "\n"))
        embed.set_footer(text="MessageID: {}".format(original_message.id))
        embed.timestamp = original_message.created_at
        sent = await star_channel.send(content="{} **{}** | {}".format(emoji, self.count_nonbot_reactions(original_message), original_channel.mention), embed=embed)
        database.create_entry(TABLENAME_STARRED_MESSAGES, (sent.id, sent.channel.id))
        await sent.add_reaction(emoji)
        await self.update_starred_messages()

    async def update_starred_messages(self):
        stars_until_condense = database.get_entry(TABLENAME_CONFIG, 'reactions_until_condense', 'config', 0)
        until_last_condense = int(database.get_entry(TABLENAME_MISC_VARS, 'value', 'name', 'starboard_until_condense'))

        database.update_entry(TABLENAME_MISC_VARS, 'value', 'name', 'starboard_until_condense', until_last_condense + 1)
        if (not(stars_until_condense is None)):
            if (stars_until_condense <= until_last_condense):
                await self.condense()
                database.update_entry(TABLENAME_MISC_VARS, 'value', 'name', 0)

def setup(bot):
    bot.add_cog(Starboard(bot))
