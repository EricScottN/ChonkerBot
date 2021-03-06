import sys
import discord
import datetime
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from config.fileloader import fileloader
import asyncio
import random
from config.all_global_variables import *


def return_random_word():
    rdowords_list = fileloader.load_csv(FilePaths.txt_rdo_words, 2)
    rdowords_list.sort(key=lambda x: x[1])
    random_word_list = random.choice(rdowords_list[:50])
    random_word = random_word_list[0]
    fileloader.update_csv(random_word, FilePaths.txt_rdo_words, 2)
    return random_word


def acceptable_word(jumbled_word, random_word):
    if jumbled_word[0] == " " or jumbled_word[-1] == " ":
        return False
    else:
        for index in range(len(jumbled_word) - 1):
            two_letters = ''.join(jumbled_word[index: index + 2])
            if two_letters in random_word and len(two_letters) > 1:
                return False
            else:
                continue
        return True


async def jumble_word(i, jumbled_word, random_word, word, words):
    attempts = 0
    while attempts <= 500:
        attempts += 1
        jumbled_word = random.sample(word, len(word))
        if acceptable_word(jumbled_word, random_word):
            words[i] = ''.join(jumbled_word)
            break
    else:
        words[i] = ''.join(jumbled_word)
    return words


def update_thx_dict(receiver_id):
    thanks_dict = fileloader.load_json(FilePaths.json_thanks)
    if receiver_id not in thanks_dict:
        thanks_dict[receiver_id] = {}
        thanks_dict[receiver_id] = 1
    else:
        thanks_dict[receiver_id] += 1
    fileloader.dump_json(thanks_dict, FilePaths.json_thanks)


def update_jumblies_time(message):
    author_id = str(message.author.id)
    created_at = message.created_at
    jumblies_time_dict = fileloader.load_json(FilePaths.json_jumbles_time)
    if author_id not in jumblies_time_dict:
        jumblies_time_dict[author_id] = {'acquired': created_at, 'times_acquired': 1, 'mins_held': 0}
    else:
        if jumblies_time_dict[author_id]['acquired']:
            acquired_string = jumblies_time_dict[author_id]['acquired']
            acquired_datetime = datetime.strptime(acquired_string, "%Y-%m-%d %H:%M:%S.%f")
            time_delta = created_at - acquired_datetime
            jumblies_time_dict[author_id]['mins_held'] += int(time_delta.total_seconds() // 60)
            jumblies_time_dict[author_id]['acquired'] = created_at
            jumblies_time_dict[author_id]['times_acquired'] += 1
        else:
            for value in jumblies_time_dict.values():
                if value['acquired']:
                    acquired_string = value['acquired']
                    acquired_datetime = datetime.strptime(acquired_string, "%Y-%m-%d %H:%M:%S.%f")
                    time_delta = created_at - acquired_datetime
                    value['mins_held'] += int(time_delta.total_seconds() // 60)
                    value['acquired'] = ''
                    break
            jumblies_time_dict[author_id]['acquired'] = created_at
            jumblies_time_dict[author_id]['times_acquired'] += 1
    fileloader.dump_jumblies_time(jumblies_time_dict)
    return jumblies_time_dict


class BotGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(DiscordGuilds.heckinchonkers_id)
        self.jumbles_role = self.guild.get_role(DiscordRoles.jumblies_role_id)
        self.fast_fingers_role = self.guild.get_role(DiscordRoles.fast_fingers_role_id)
        #self.rdwordjumble.start()
        self.stb_active_channel = self.bot.get_channel(ActiveChannels.stb_active_channel)
        self.hours = 0
        self.jumble_countdown = Arguments.jumble_countdown
        self.jumble_wait = Arguments.jumble_wait

    @tasks.loop()
    async def rdwordjumble(self):
        if self.jumble_countdown:
            await asyncio.sleep(self.jumble_countdown)
            self.jumble_countdown = None
        else:
            interval = random.choices(population=[1.00, 5.00, 10.00, 15.00, 20.00],
                                         weights=[0.10, 0.10, 0.15, 0.25, 0.40])[0]
            interval_min = random.randint(0, 3600)
            print(f'Next RDO word jumble will run in {interval} hours')
            await asyncio.sleep(interval * 3600 + interval_min)
        message = await self.stb_active_channel.send(
            f"{self.jumbles_role.mention} React within {self.jumble_wait} (nice) "
            f"seconds with the <:campstew:678376192377618448> emoji to "
            f"play Red Dead Word Jumble")
        await message.add_reaction("<:campstew:678376192377618448>")
        await asyncio.sleep(self.jumble_wait)
        message = await self.stb_active_channel.fetch_message(message.id)
        reaction = [i for i in message.reactions if str(i.emoji.name) == "campstew"][0]
        users = await reaction.users().flatten()

        if len(users) > 1:
            await self.play_jumble(users)
        else:
            await self.stb_active_channel.send(f'No takers. Okay maybe next time!')
        return

    async def play_jumble(self, users):
        await self.stb_active_channel.send("Okay, lets play! Winner gets a free !thx")
        await self.stb_active_channel.trigger_typing()
        await asyncio.sleep(5)
        random_word = return_random_word()
        if ' ' in random_word and len(random_word) > 9:
            words = random_word.split(' ')
        else:
            words = [random_word]
        for index, word in enumerate(words):
            jumbled_word = None
            await jumble_word(index, jumbled_word, random_word, word, words)
        if words:
            jumbled_word = ' '.join(words)
            await self.stb_active_channel.send(f'The jumbled RDO word is: `{jumbled_word}`\nYou have 30 seconds to '
                                               f'guess correctly!')
            message = await self.get_message(users, random_word)
            if message is not None:
                await self.process_winner(message, random_word)
            else:
                await self.stb_active_channel.send(f'Sorry! Nobody won! The word was `{random_word}`\nBetter luck '
                                                   f'next time!')

        else:
            await self.stb_active_channel.send(f'I tried a bajillion times to scramble the word '
                                               f'and failed. Sorry. I will try to do better next time.')

    async def process_winner(self, message, random_word):
        response = f"{message.author.display_name} guessed correctly! The word was `{random_word}`!"
        await self.stb_active_channel.send(response)
        await self.update_jumblies_role(message)
        winner_id = str(message.author.id)
        update_thx_dict(winner_id)
        jumblies_time_dict = update_jumblies_time(message)
        total_mins_held = jumblies_time_dict[winner_id]['mins_held']
        times_acquired = jumblies_time_dict[winner_id]['times_acquired']
        days_held = total_mins_held // 60 // 24
        hours_remainder = (total_mins_held - (days_held * 60 * 24)) // 60
        mins_remainder = (total_mins_held - ((hours_remainder * 60) + (days_held * 60 * 24)))
        result_str = ''
        sorted_jumblies_time = {k: v for k, v in sorted(jumblies_time_dict.items(),
                                                        key=lambda item: (item[1]['mins_held']),
                                                        reverse=True)}
        sorted_jumblies_acq = {k: v for k, v in sorted(jumblies_time_dict.items(),
                                                        key=lambda item: (item[1]['times_acquired']),
                                                        reverse=True)}

        winner_time_rank = list(sorted_jumblies_time).index(winner_id) + 1
        winner_acq_rank = list(sorted_jumblies_acq).index(winner_id) + 1
        x = 1
        for k, v in sorted_jumblies_time.items():
            member_id = (int(k))
            member = discord.utils.find(lambda m: m.id == member_id, self.guild.members)
            if member is not None:
                result_str += f'`{str(x).rjust(2)}. {str(v).rjust(2)} minutes held - ' \
                              f'{member.display_name}`\n'

        response = f"I thanked {message.author.mention}! They now " \
                   f"have the {self.fast_fingers_role.mention}\n **Total Time Held**:\n" \
                   f"`{days_held} {'days' if days_held != 1 else 'day'} | " \
                   f"{hours_remainder} {'hours' if hours_remainder != 1 else 'hour'} | " \
                   f"{mins_remainder} {'minutes' if mins_remainder != 1 else 'minute'} | " \
                   f"rank {winner_time_rank} in total time held`\n\n`{message.author.display_name} " \
                   f"has won jumblies {times_acquired} {'times' if times_acquired != 1 else 'time'} " \
                   f"and ranks {winner_acq_rank} overall!`"
        await self.stb_active_channel.send(response)


    async def update_jumblies_role(self, message):
        fast_finger_role_member = self.fast_fingers_role.members
        if fast_finger_role_member:
            [member.remove_roles(self.fast_fingers_role) for member in fast_finger_role_member]
        await message.author.add_roles(self.fast_fingers_role)

    @commands.Cog.listener()
    async def get_message(self, users, rdoword):
        def check(m):
            if m.author is not self.bot \
                    and m.channel == self.stb_active_channel\
                    and m.author in users:
                if m.content.upper() == rdoword:
                    return m

        try:
            content = await self.bot.wait_for('message', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            return None
        else:
            return content


def setup(bot):
    bot.add_cog(BotGames(bot))
