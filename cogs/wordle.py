import re
import enum
import datetime as time

import database
from bot import TABLENAME_USERS
import discord
from discord.ext import commands
from wordle_guess import Wordle_guess

TABLENAME_ANSWERS = 'wordle_answers'
TABLENAME_ACCEPTED_WORDS = 'wordle_accepted_words'
TABLENAME_EMOJIS = 'wordle_letter_emojis'
TABLENAME_CONFIG = 'wordle_config'

COLUMNS_ANSWERS = ('word TEXT',)
COLUMNS_ACCEPTED_WORDS = ('word TEXT',)
COLUMNS_EMOJIS = ('id INTEGER PRIMARY KEY', 'name TEXT')
COLUMNS_WORDLE_CONFIG = ('config INTEGER PRIMARY KEY', 'channel_id INTEGER')

DEFAULT_CONFIG = (0, -1)

class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.initialize_database()
        self.accepted_words = set(database.get_all(TABLENAME_ACCEPTED_WORDS))
        self.answers = set(database.get_all(TABLENAME_ANSWERS))
        self.current_answer = None
        self.answer_data = []
        self.guess_list = []
        self.wordle_number = 1

    def initialize_database(self):
        database.create_table(TABLENAME_ANSWERS, COLUMNS_ANSWERS)
        database.create_table(TABLENAME_ACCEPTED_WORDS, COLUMNS_ACCEPTED_WORDS)
        database.create_table(TABLENAME_CONFIG, COLUMNS_WORDLE_CONFIG)
        
        database.create_entry(TABLENAME_CONFIG, DEFAULT_CONFIG)
        # If you need to recompile stuff (will be slow):
    #     self.recompile_words()

    def recompile_words(self):
        with open('answers.txt') as f:
            answers = f.read().splitlines()
        for word in answers:
            database.create_entry(TABLENAME_ANSWERS, (word,))

        with open('accepted_words.txt') as f:
            self.accepted_words = f.read().splitlines()
        for word in self.accepted_words:
            database.create_entry(TABLENAME_ACCEPTED_WORDS, (word,))

    def to_serialize(self, guesses):
        ret = ''
        for guess in guesses:
            for letter in guess.letters:
                ret += '{}{}'.format(letter[0], letter[1])
        return ret

    def from_serialize(self, text):
        ret = []
        for index in range(0, len(text), 2):
            word = []
            data = [text[index], text[index + 1]]
            word.append(data)
            if (len(word) == len(self.letters)):
                ret.append(word) 
        return ret

    @commands.group()
    @commands.guild_only()
    async def wordle(self, context):
        if context.invoked_subcommand is None:
            await context.channel.send(embed=self.bot.embed_skeleton("Commands: play"))

    @wordle.command()
    async def giveup(self, context): 
        sent = await context.send(embed=self.bot.embed_skeleton('Are you sure you want to reset your current Wordle game?'))
        await sent.add_reaction("😍")
        await sent.add_reaction("😭")

        def check(reaction, user):
            if (user == context.author):
                if (str(reaction.emoji) == "😍"):
                    database.update_entry(TABLENAME_USERS, 'wordle_current_game', 'user_id', user.id, None)
                    return True
                elif (str(reaction.emoji) == "😭"):
                    return True
            return False

        await self.bot.wait_for('reaction_add', timeout=None, check=check)
        await context.send(embed=self.bot.embed_skeleton('Wordle game reset.'))

    @wordle.command()
    async def channel(self, context):
        updated_channel = self.bot.get_channel(database.get_entry(TABLENAME_CONFIG, 'channel_id', 'config', 0))
        await context.channel.send(embed=self.bot.embed_skeleton("Please tag the channel that you want me to send your daily Wordle results to."))

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
        await context.channel.send(embed=self.bot.embed_skeleton("I've set the Wordle channel to: {}".format(updated_channel.mention)))

    @wordle.command()
    async def play(self, context):
        if (database.get_entry(TABLENAME_USERS, 'wordle_current_game', 'user_id', context.author.id) is None):
            database.update_entry(TABLENAME_USERS, 'wordle_current_game', 'user_id', context.author.id, '')
            self.guess_list = []
            await self.start_game(context)
        else:
            await context.send(embed=self.bot.embed_skeleton('You already have a game in progress!'))

    async def start_game(self, context):
        #self.current_answer = database.get_random_entry(TABLENAME_ANSWERS, 'word')
        self.current_answer = 'mimic'
        print(self.current_answer)
        self.answer_data = self.gen_answer_data(self.current_answer)
        await self.query(context.author, "What's your first guess?")

    def gen_answer_data(self, word):
        ret = Wordle_guess(word)
        return ret

    async def query(self, author, text=None):
        class Word(Exception):
            pass
        guess = None
        if (not(text == None)):
            await author.send(embed=self.bot.embed_skeleton(text))

        def check(message):
            if (message.author == author and message.channel == author.dm_channel):
                nonlocal guess
                guess = message.content.lower()
                if (re.match("^[A-Za-z]{5}", guess)):
                    # guess needs to be cast as a tuple because the set of words is a result of a query which is a tuple. This is probably bad?
                    if (((guess,) in self.accepted_words) or ((guess,) in self.answers)):
                        return True
                raise Word()
    
        try:
            await self.bot.wait_for('message', timeout=None, check=check)
            await self.process_turn(author, guess)
        except Word:
            await self.query(author, "I'm a renowned poet of the English language and even I don't recognize that word. Guess again?")
            return

    async def process_turn(self, author, message):
        guess = self.gen_answer_data(message)
        self.guess_list.append(guess)

        await self.process_guess(guess)
        await author.send(embed=self.bot.embed_skeleton(self.print_guess(author)))
        await self.process_gameover(author, guess)

    async def process_guess(self, guess):
        # Refactor
        index_g = 0
        index_ans = 0
        for g_element in guess.letters:
            index_ans = 0
            for ans_element in self.answer_data.letters:
                g_letter = g_element[0]
                ans_letter = ans_element[0]

                if (g_letter == ans_letter and not(guess.letters[index_ans][1] == 'g')):
                    if (index_g == index_ans):
                        g_element[1] = 'g'
                        guess.greens += 1
                        break
                    else:
                        g_element[1] = 'y'
                index_ans += 1
            index_g += 1

    # Refactor
    async def process_gameover(self, author, guess):
        if (guess.greens == 5):
            await self.print_win(author)
            await self.send_to_channel(author)
            self.wordle_number += 1
            database.update_entry(TABLENAME_USERS, 'wordle_current_game', 'user_id', author.id, None)
            return
        else:
            if (len(self.guess_list) == 6):
                await self.print_loss(author)
                await self.send_to_channel(author)
                self.wordle_number += 1
                database.update_entry(TABLENAME_USERS, 'wordle_current_game', 'user_id', author.id, None)
                return
            await self.query(author)

    async def print_win(self, author):
        await author.send(embed=self.bot.embed_skeleton('You won! Nice!'))

    async def print_loss(self, author):
        await author.send(embed=self.bot.embed_skeleton('Sorry, you lost. The correct answer was {}'.format(self.current_answer.upper())))

    async def send_to_channel(self, author):
        embed = self.bot.embed_skeleton(self.print_guess(author, obscured=True))
        embed.set_author(name=str(author), icon_url=author.avatar_url)
        embed.title = "Wordle {} {}/6".format(self.wordle_number, len(self.guess_list))
        await self.bot.get_channel(database.get_entry(TABLENAME_CONFIG, 'channel_id', 'config', 0)).send(embed=embed)

    def print_guess(self, author, obscured=False):
        ret = ''
        for guess in self.guess_list:
            ret += self.gen_row(guess, obscured)
            ret += '\n'
        return ret

    def gen_row(self, guess, obscured=False):
        ret = ''
        for element in guess.letters:
            color = element[1]
            if (obscured):
                if (color == 'w'):
                    ret += '⬛'
                elif (color == 'y'):
                    ret += '🟨'
                else:
                    ret += '🟩'
            else:
                letter = element[0]
                emoji_name = '{}_{}'.format(color, letter)
                id = database.get_entry('wordle_letter_emojis', 'id', 'name', emoji_name)
                ret += '<:{}:{}>'.format(emoji_name, id)
        return ret

def setup(bot):
    bot.add_cog(Wordle(bot))