import os
import logging
import discord
from dotenv import load_dotenv
from discord.ext import commands
from config.setup import parse_arguments
from config.queue_objects import aqo
from config.all_global_variables import FilePaths, ActivityStrings

load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    try:
        print(f'{bot.user.name} has connected to Discord!')
        for filename in os.listdir('./startup_cogs'):
            if filename.endswith('.py'):
                bot.load_extension(f'startup_cogs.{filename[:-3]}')
        print('Start up cogs loaded successfully')
    except Exception as e:
        print(e)

    delivery_hosts_lists = aqo.get_hosts_list(0, ActivityStrings.delivery_str )
    moonshine_hosts_lists = aqo.get_hosts_list(1, ActivityStrings.moonshine_str)
    bounty_hosts_lists = aqo.get_hosts_list(2, ActivityStrings.bounty_str)
    nature_hosts_lists = aqo.get_hosts_list(3, ActivityStrings.nature_str)
    posse_hosts_lists = aqo.get_hosts_list(4, ActivityStrings.posse_str)

    if (delivery_hosts_lists or moonshine_hosts_lists or bounty_hosts_lists or nature_hosts_lists or posse_hosts_lists
            and FilePaths.commands_cog_file_path not in list(bot.extensions)):
        bot.load_extension(FilePaths.commands_cog_file_path)
        print('There is a host. All commands loaded successfully')
    else:
        print('No active hosts')
    if nature_hosts_lists and nature_hosts_lists not in list(bot.extensions):
        bot.load_extension(FilePaths.naturalist_commands_cog_file_path)
        print('There is a naturalist host. Naturalist commands loaded successfully')

    else:
        print('No active naturalist hosts')
if __name__ == "__main__":
    parse_arguments()
    bot.run(os.getenv("TOKEN"))