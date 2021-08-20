import datetime

import discord
from discord.ext import commands
from config.fileloader import fileloader
import random
from config.queue_objects import aqo
from config.all_global_variables import DiscordRoles, ActivityStrings
import asyncio


class FunCommands(commands.Cog, name='Fun Commands'):
    """Just some fun things that ChonkerBot can do!"""

    def __init__(self, bot):
        self.bot = bot
        self.thx_dict = {}

    async def delete_pic_or_gif(self, ctx, pic_or_gif, name, num):
        pics_n_gifs_dict = fileloader.load_pics_n_gifs()
        pic_or_gif_dict = pics_n_gifs_dict[pic_or_gif]

        if name not in pic_or_gif_dict:
            await ctx.channel.send(f'Could not find a {pic_or_gif} with name {name}')
            return

        if num not in pic_or_gif_dict[name]:
            await ctx.channel.send(f'That number does not exist for {name}')
            return

        pic_or_gif_dict[name][num] = '[REDACTED]'
        fileloader.dump_pics_n_gifs(pics_n_gifs_dict)
        await ctx.channel.send(f'`{pic_or_gif} {name} {num}` has been `[REDACTED]`')


    async def generate_pic_or_gif(self, ctx, pic_or_gif, name, num):
        pics_n_gifs_dict = fileloader.load_pics_n_gifs()
        pic_or_gif_dict = pics_n_gifs_dict[pic_or_gif]

        if name not in pic_or_gif_dict:
            await ctx.channel.send(f'Could not find a {pic_or_gif} with name {name}')
            return

        if num not in pic_or_gif_dict[name]:
            await ctx.channel.send(f'That number does not exist for {name}')
            return

        url = pic_or_gif_dict[name][num]

        await ctx.channel.send(url)
        return

    @commands.command(name='dice',
                      help="Roll two six sided dice")
    async def roll_dice(self, ctx):
        min_value = 1
        max_value = 6
        await ctx.channel.send(f'Okay! Rolling the dices!')
        await ctx.channel.trigger_typing()
        await asyncio.sleep(3)
        await ctx.channel.send(
            f'The values are `{random.randint(min_value, max_value)}` and `{random.randint(min_value, max_value)}`!')

    # =================================================== #
    # =======BOT COMMAND FOR RDM SPIRIT ANIMAL=========== #
    # =================================================== #
    @commands.command(name='spirit',
                      help="Will return your RDR2 spirit animal")
    async def spirit_animal(self, ctx):
        await ctx.channel.trigger_typing()
        await asyncio.sleep(2)
        animals = fileloader.load_animals()
        legendary_animals = []
        for animal in animals:
            if animal.startswith('Legendary'):
                legendary_animals.append(animal)
                animals.remove(animal)

        random_animal = random.choices(population=[random.choice(animals), random.choice(legendary_animals)],
                                       weights=[0.99, 0.01])[0]

        if random_animal.startswith(('A', 'E', 'I', 'O', 'U')):
            response = f'Your spirit animal is an {random_animal}!\n'
        else:
            response = f'Your spirit animal is a {random_animal}!\n'

        await ctx.channel.send(response)

    # =================================================== #
    # ===========BOT COMMAND TO THX MEMBERS============== #
    # =================================================== #
    @commands.command(name='thx',
                      help='Give somebody a thanks! Ask somebody what they\'re for!')
    async def thanks(self, ctx, members):
        await ctx.channel.trigger_typing()
        if members == 'all':
            channel = ctx.message.channel
            if 'deliver' in channel.name:
                activity = ActivityStrings.delivery_str
                unfound = 'You are not hosting any deliveries, thus, nobody to thank!'
            elif 'natur' in channel.name:
                activity = ActivityStrings.nature_str
                unfound = 'You are not hosting any naturalist missions. Who all are you trying to thank?'
            elif 'bounty' in channel.name:
                activity = ActivityStrings.bounty_str
                unfound = 'You are not hosting any bounty hunts. thx all FOR NOTHING'
            elif 'moonshine' in channel.name:
                activity = ActivityStrings.moonshine_str
                unfound = 'You are not hosting any moonshine deliveries you silly freaking gooseface'
            elif 'general-channel' in channel.name:
                activity = ActivityStrings.posse_str
                unfound = 'You are not hosting any general posses'
            else:
                unfound = 'Go to the correct role channel where you are hosting to thx all. If you are hosting a ' \
                          'general posse, go to the private room that was made for the posse to thx all'

            host_id = str(ctx.message.author.id)

            list_of_host_ids = aqo.get_list_of_host_ids(activity)

            if host_id not in list_of_host_ids:
                await ctx.channel.send(unfound)
                return
            thx_dict = fileloader.load_thanks()
            list_of_member_dicts = aqo.get_list_of_members(host_id, activity)
            receiver_str = ''
            for member_dict in list_of_member_dicts:
                for member_id in member_dict:
                    if member_id != host_id:
                        receiver_str += f"{member_dict[member_id]}\n"
                        if member_id not in thx_dict:
                            thx_dict[member_id] = {}
                            thx_dict[member_id] = 1
                        else:
                            thx_dict[member_id] += 1
            fileloader.dump_thanks(thx_dict)
            response = f"{ctx.message.author.display_name} thanked:\n{receiver_str}"
            await ctx.channel.send(response)
            return
        else:
            author_id = str(ctx.message.author.id)
            receiver_id = str(ctx.message.mentions[0].id)
            time_created = ctx.message.created_at
            if not self.thx_dict or author_id not in self.thx_dict.keys():
                self.thx_dict[author_id] = {receiver_id: time_created}
            else:
                if receiver_id not in self.thx_dict[author_id].keys():
                    self.thx_dict[author_id][receiver_id] = time_created
                else:
                    d = datetime.timedelta(minutes=60)
                    if time_created - self.thx_dict[author_id][receiver_id] < d:
                        await ctx.channel.send("Don't spam thx k thx (You can thank that person in an hour)")
                        self.thx_dict[author_id][receiver_id] = time_created
                        return
                    else:
                        self.thx_dict[author_id][receiver_id] = time_created

            receiver_display_name = ctx.message.mentions[0].display_name

            if int(receiver_id) == ctx.message.author.id:
                response = "Hey! That's cheating you dishonorable fool!"
                await ctx.channel.send(response)
                return

            thanks_dict = fileloader.load_thanks()

            if receiver_id not in thanks_dict:
                thanks_dict[receiver_id] = {}
                thanks_dict[receiver_id] = 1
            else:
                thanks_dict[receiver_id] += 1

            response = f"{ctx.message.author.display_name} thanked {receiver_display_name}!"

            fileloader.dump_thanks(thanks_dict)
            await ctx.channel.send(response)

    megachonkers = DiscordRoles.megachonkers_role_id
    admin = DiscordRoles.heckinadmin_role_id
    heftychonks = DiscordRoles.heftychonks_role_id

    @commands.command(name='pic',
                      help='Spam a pic!')
    async def pic(self, ctx, name, num):
        await self.generate_pic_or_gif(ctx, 'pic', name.lower(), num)
        return

    @commands.command(name='gif',
                      help='Spam a gif!')
    async def gif(self, ctx, name, num):
        await self.generate_pic_or_gif(ctx, 'gif', name.lower(), num)
        return
    @commands.command(name='8ball',
                      aliases=['8', '8b'],
                      help="Ask ChonkerBot a question - receive an answer (maybe)!")
    async def ball(self, ctx, *question):
        if not question:
            await ctx.channel.send('Ummmmmm what do you want to ask me?')
            return
        else:
            responses = fileloader.load_ball()
            response = random.choice(responses)
            await ctx.channel.send(response)
            return


    @commands.has_role(admin)
    @commands.command(name='dpic',
                      hidden=True)
    async def dpic(self, ctx, name, num):
        await self.delete_pic_or_gif(ctx, 'pic', name.lower(), num)
        return

    @commands.has_role(admin)
    @commands.command(name='dgif',
                      hidden=True)
    async def dgif(self, ctx, name, num):
        await self.delete_pic_or_gif(ctx, 'gif', name.lower(), num)
        return

    @commands.command(name='pandg',
                      help='See all available Pics and Gifs')
    async def pandg(self, ctx):

        pics_n_gifs_dict = fileloader.load_pics_n_gifs()
        gif_dict = pics_n_gifs_dict['gif']
        pic_dict = pics_n_gifs_dict['pic']

        embed = discord.Embed(
            colour=discord.Colour.teal(),
            title='All Pics and Gifs'
        )
        gandp_string = ''
        total = 0
        for key in sorted(pic_dict.keys()):
            gandp_string += f'`{key}|{len(pic_dict[key].keys())}|`,'
            total += len(pic_dict[key].keys())
        embed.add_field(name=f'PICS ({total} TOTAL)', value=gandp_string[:-1])
        gandp_string = ''
        total = 0
        for key in sorted(gif_dict.keys()):
            gandp_string += f'`{key}|{len(gif_dict[key].keys())}|`,'
            total += len(gif_dict[key].keys())
        embed.add_field(name=f'GIFS ({total} TOTAL)', value=gandp_string[:-1] + '\n\n', inline=False)
        await ctx.channel.send(embed=embed)

    @commands.has_any_role(heftychonks, megachonkers, admin)
    @commands.command(name='create',
                      help='Create a pic or a gif! Can only be used by `HeftyChonks, MEGACHONKERS` or `AHeckinAdmin`')
    async def create(self, ctx, pic_or_gif, name, url):
        if pic_or_gif != 'pic' and pic_or_gif != 'gif':
            await ctx.channel.send('Your first argument should either be `pic` or `gif`.')
            return

        valid_pic_ext = ('jpg', 'jpeg', 'png')
        valid_gif_ext = ('gif')
        if pic_or_gif == 'pic' and not url.endswith(valid_pic_ext):
            message = f'That is not a valid pic. Maybe you linked a gif?'
            await ctx.channel.send(message)
            return
        if pic_or_gif == 'gif' and valid_gif_ext not in url:
            message = f'That is not a valid gif. Maybe you linked a pic?'
            await ctx.channel.send(message)
            return


        pics_n_gifs_dict = fileloader.load_pics_n_gifs()
        pic_or_gif_dict = pics_n_gifs_dict[pic_or_gif]

        for p_or_g_arg, p_or_g_entries in pic_or_gif_dict.items():
            for i in p_or_g_entries:
                if p_or_g_entries[i] == url:
                    await ctx.channel.send(f'That url already exists under `{pic_or_gif} {p_or_g_arg} {i}`')
                    return
                else:
                    continue
        x = 1
        if name.lower() not in pic_or_gif_dict:
            pic_or_gif_dict[name.lower()] = {x: url}
        else:
            arg_dicts = pic_or_gif_dict[name.lower()]
            while x <= len(arg_dicts):
                if arg_dicts[str(x)] == '[REDACTED]':
                    break
                else:
                    x += 1
            pic_or_gif_dict[name.lower()][x] = url

        fileloader.dump_pics_n_gifs(pics_n_gifs_dict)
        await ctx.channel.send(f'I added a new {pic_or_gif}! You can summon it with `!{pic_or_gif} {name.lower()} {x}`')

    @create.error
    async def error_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.channel.send(f'Pics and Gifs can only be created by `AHeckinAdmin, MEGACHONKERS, or HeftyChonks`')
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.channel.send(f'You are missing an argument. Use `!help create` to see the correct format')
        raise error

    @dgif.error
    @dpic.error
    async def error_handler(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.channel.send(f'Pics and Gifs can only be deleted by `AHeckinAdmin`')


    @pic.error
    @gif.error
    async def error_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'name':
                await ctx.channel.send(f'Please specify a name and number')
            if error.param.name == 'num':
                await ctx.channel.send(f'Please specify a number')
        raise error


def setup(bot):
    bot.add_cog(FunCommands(bot))
