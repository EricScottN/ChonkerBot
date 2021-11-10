import discord
from discord.ext import commands
from config.all_global_variables import *
from config.queue_objects import aqo
from config.fileloader import fileloader
from config.convert_time import convert_date_to_str


class ChannelError(commands.CheckFailure):
    pass


# Testing channel id
bot_testing_channel_id = DiscordChannels.bot_testing_channel_id

# RDO role channel ids
delivery_channel_id = DiscordChannels.delivery_channel_id
bounty_channel_id = DiscordChannels.bounty_channel_id
nature_channel_id = DiscordChannels.nature_channel_id
moonshine_channel_id = DiscordChannels.moonshine_channel_id

# Set channels to active or testing
delivery_active_channel = ActiveChannels.delivery_active_channel
bounty_active_channel = ActiveChannels.bounty_active_channel
nature_active_channel = ActiveChannels.nature_active_channel
moonshine_active_channel = ActiveChannels.moonshine_active_channel


def return_test_channel():
    return bot_testing_channel_id


def return_delivery_active():
    return delivery_active_channel

def return_moonshine_active():
    return moonshine_active_channel

def return_nature_active():
    return nature_active_channel

def return_bounty_active():
    return bounty_active_channel

def channel_check(channel):
    async def predicate(ctx):
        if channel == delivery_active_channel and channel != bot_testing_channel_id:
            if ctx.channel.id != channel:
                raise ChannelError('Delivery commands can only be used in the delivery channel')

        if channel == moonshine_active_channel and channel != bot_testing_channel_id:
            if ctx.channel.id != channel:
                raise ChannelError('Moonshine commands can only be used in the moonshine channel')

        if channel == bounty_active_channel and channel != bot_testing_channel_id:
            if ctx.channel.id != channel:
                raise ChannelError('Bounty commands can only be used in the bounty channel')

        if channel == nature_active_channel and channel != bot_testing_channel_id:
            if ctx.channel.id != channel:
                raise ChannelError('Naturalist commands can only be used in the naturalist channel')

        if channel == bot_testing_channel_id and ctx.channel.id != bot_testing_channel_id:
            raise ChannelError('This command is currently being tested! It will be back soon!')

        return True

    return commands.check(predicate)

class StartRDORoles(commands.Cog, name='Start RDO Roles'):
    """Start a role posse using the commands in this category, or see who already has a role posse by using \"queue\""""
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(DiscordGuilds.heckinchonkers_id)

    def generate_queue_embed(self, activity, host_dict):
        psn_names = fileloader.load_json(FilePaths.json_psn)
        if host_dict['host_id'] in psn_names:
            embed = discord.Embed(
                colour=discord.Colour.dark_red(),
                title=f"{host_dict['host_name']}\nPSN: {psn_names[host_dict['host_id']]}")

        else:
            embed = discord.Embed(
                colour=discord.Colour.dark_red(),
                title=f"{host_dict['host_name']}")
        user_avatar = self.bot.get_user(int(host_dict['host_id'])).avatar_url
        embed.set_thumbnail(url=user_avatar)
        members_string = ''
        members_dicts = host_dict['members']

        for member_dict in members_dicts:
            for key in member_dict:
                members_string += member_dict[key] + '\n'
        embed.add_field(name='Type', value=activity.upper())
        embed.add_field(name='Members', value=members_string, inline=False)

        slots_remaining = host_dict['slots']
        if slots_remaining <= 0:
            embed.add_field(name='Slots Remaining',
                            value="**NO SLOTS AVAILABLE!**",
                            inline=False)
        else:
            embed.add_field(name='Slots Remaining',
                            value=f"**{str(slots_remaining)} SLOTS REMAINING**",
                            inline=False)
        if host_dict['activity_room'] != '':
            embed.add_field(name='Private Room',
                            value=f"{host_dict['activity_room']}",
                            inline=False)
        return embed



    # =================================================== #
    # =======BOT COMMAND TO CREATE A DELIVERY============ #
    # =================================================== #
    @channel_check(return_delivery_active())
    @commands.command(name='delivery',
                      aliases=['d'],
                      help=f'Creates a delivery posse, where slots is the number of posse members needed [max 6]')
    async def create_delivery(self, ctx, slots: int):
        await ctx.channel.trigger_typing()
        if slots <= 0 or slots >= 7:
            response = "Amount of slots requested is out of posse size range"
            await ctx.channel.send(response)
            return

        # Get the host display name and host id from discord
        host_display_name = ctx.message.author.display_name
        host_id = str(ctx.message.author.id)
        delivery_role = ctx.guild.get_role(669707245621215244)

        # Get the time created and convert to str for JSON
        time_created = ctx.message.created_at
        time_created = convert_date_to_str(time_created)

        queue_number, activity = aqo.get_queue_info('d')

        list_of_host_ids = aqo.get_list_of_host_ids(activity)

        if host_id not in list_of_host_ids:
            temp_host_dict = {}
            temp_host_dict.update({'host_name': host_display_name})
            temp_host_dict.update({'host_id': host_id})
            temp_host_dict.update({'members': [{host_id: host_display_name}]})
            temp_host_dict.update({'time_created': time_created})
            temp_host_dict.update({'status': 'active'})
            temp_host_dict.update({'slots': slots})
            temp_host_dict.update({'activity_room': ''})
            delivery_hosts_list = aqo.get_hosts_list(queue_number, activity)
            delivery_hosts_list.append(temp_host_dict)
            fileloader.dump_queues(aqo.get_all_queues())
            response = f"{delivery_role.mention} {ctx.message.author.mention} has started a delivery with " \
                       f' {str(slots)} open slots! Join with `!j d @mention` the host'
            psn_names = fileloader.load_json(FilePaths.json_psn)
            if host_id in psn_names:
                response += f"\n\n{host_display_name}'s PSN is **{psn_names[host_id]}**. Add them if you haven't already!"
            if FilePaths.commands_cog_file_path not in list(self.bot.extensions):
                self.bot.load_extension(FilePaths.commands_cog_file_path)
            await ctx.channel.send(response)
        else:
            response = "You already have a delivery, you silly ass! If you wish to clear it and start a new one, " \
                       "type `!c d` "
            await ctx.channel.send(response)

    # =================================================== #
    # =======BOT COMMAND TO CREATE A MOONSHINE=========== #
    # =================================================== #
    @channel_check(return_moonshine_active())
    @commands.command(name='moonshine',
                      aliases=['m'],
                      help=f'Creates a moonshine posse, where slots is the number of posse members needed [max 6]')
    async def create_moonshine(self, ctx, slots: int):
        await ctx.channel.trigger_typing()
        if slots <= 0 or slots >= 7:
            response = "Amount of slots requested is out of posse size range"
            await ctx.channel.send(response)
            return

        # Get the host display name and host id from discord
        host_display_name = ctx.message.author.display_name
        host_id = str(ctx.message.author.id)
        moonshine_role = ctx.guild.get_role(681150692290723929)

        # Get the time created and convert to str for JSON
        time_created = ctx.message.created_at
        time_created = convert_date_to_str(time_created)

        queue_number, activity = aqo.get_queue_info('m')

        list_of_host_ids = aqo.get_list_of_host_ids(activity)

        if host_id not in list_of_host_ids:
            temp_host_dict = {}
            temp_host_dict.update({'host_name': host_display_name})
            temp_host_dict.update({'host_id': host_id})
            temp_host_dict.update({'members': [{host_id: host_display_name}]})
            temp_host_dict.update({'time_created': time_created})
            temp_host_dict.update({'status': 'active'})
            temp_host_dict.update({'slots': slots})
            temp_host_dict.update({'activity_room': ''})
            moonshine_hosts_list = aqo.get_hosts_list(queue_number, activity)
            moonshine_hosts_list.append(temp_host_dict)
            fileloader.dump_queues(aqo.get_all_queues())
            response = f"{moonshine_role.mention} {ctx.message.author.mention} has started a moonshine delivery with " \
                       f' {str(slots)} open slots! Join with `!j m @mention` the host'
            psn_names = fileloader.load_json(FilePaths.json_psn)
            if host_id in psn_names:
                response += f"\n\n{host_display_name}'s PSN is **{psn_names[host_id]}**. Add them if you haven't already!"
            if FilePaths.commands_cog_file_path not in list(self.bot.extensions):
                self.bot.load_extension(FilePaths.commands_cog_file_path)
            await ctx.channel.send(response)
        else:
            response = "You already have a moonshine delivery, you silly ass! If you wish to clear it and start a new one, " \
                       "type `!c m`"
            await ctx.channel.send(response)

    # =================================================== #
    # =======BOT COMMAND TO CREATE A BOUNTY============ #
    # =================================================== #
    @channel_check(return_bounty_active())
    @commands.command(name='bounty',
                      aliases=['b'],
                      help=f'Creates a bounty hunt posse, where slots is the amount of members needed [max 3]')
    async def create_bounty(self, ctx, slots: int):
        await ctx.channel.trigger_typing()
        if slots <= 0 or slots >= 4:
            response = "Amount of slots requested is out of posse size range for a bounty."
            await ctx.channel.send(response)
            return

        # Get the host display name and host id from discord
        host_display_name = ctx.message.author.display_name
        host_id = str(ctx.message.author.id)
        bounty_role = ctx.guild.get_role(681151630720368740)

        # Get the time created and convert to str for JSON
        time_created = ctx.message.created_at
        time_created = convert_date_to_str(time_created)

        queue_number, activity = aqo.get_queue_info('b')

        list_of_host_ids = aqo.get_list_of_host_ids(activity)

        if host_id not in list_of_host_ids:
            temp_host_dict = {}
            temp_host_dict.update({'host_name': host_display_name})
            temp_host_dict.update({'host_id': host_id})
            temp_host_dict.update({'members': [{host_id: host_display_name}]})
            temp_host_dict.update({'time_created': time_created})
            temp_host_dict.update({'status': 'active'})
            temp_host_dict.update({'slots': slots})
            temp_host_dict.update({'activity_room': ''})
            bounty_hosts_list = aqo.get_hosts_list(queue_number, activity)
            bounty_hosts_list.append(temp_host_dict)
            fileloader.dump_queues(aqo.get_all_queues())
            response = f"{bounty_role.mention} {ctx.message.author.mention} has started a bounty hunt with " \
                       f' {str(slots)} open slots! Join with `!j b @mention` the host'
            psn_names = fileloader.load_json(FilePaths.json_psn)
            if host_id in psn_names:
                response += f"\n\n{host_display_name}'s PSN is **{psn_names[host_id]}**. Add them if you haven't already!"
            await ctx.channel.send(response)
            try:
                self.bot.load_extension(FilePaths.commands_cog_file_path)
                print("All Commands loaded successfully")
            except:
                if FilePaths.commands_cog_file_path in list(self.bot.extensions):
                    pass
        else:
            response = "You are already hosting bounty hunts, you silly ass! If you wish to clear it and start a new one, " \
                       "type `!c b` "
            await ctx.channel.send(response)

    # =================================================== #
    # ======BOT COMMAND TO CREATE A NATURE SOMETHING===== #
    # =================================================== #
    @channel_check(return_nature_active())
    @commands.command(name='naturalist',
                      aliases=['n'],
                      help=f'Creates a naturalist posse, where slots is the amount of members needed [max 6]')
    async def create_nature(self, ctx, slots: int):
        await ctx.channel.trigger_typing()

        if slots <= 0 or slots >= 7:
            response = "Amount of slots requested is out of posse size range for a hosting naturalist missions"
            await ctx.channel.send(response)
            return

        # Get the host display name and host id from discord
        host_display_name = ctx.message.author.display_name
        host_id = str(ctx.message.author.id)
        nature_role = ctx.guild.get_role(738205376524058685)

        # Get the time created and convert to str for JSON
        time_created = ctx.message.created_at
        time_created = convert_date_to_str(time_created)

        queue_number, activity = aqo.get_queue_info('n')

        list_of_host_ids = aqo.get_list_of_host_ids(activity)

        if host_id not in list_of_host_ids:
            temp_host_dict = {}
            temp_host_dict.update({'host_name': host_display_name})
            temp_host_dict.update({'host_id': host_id})
            temp_host_dict.update({'members': [{host_id: host_display_name}]})
            temp_host_dict.update({'time_created': time_created})
            temp_host_dict.update({'status': 'active'})
            temp_host_dict.update({'slots': slots})
            temp_host_dict.update({'activity_room': ''})
            nature_hosts_list = aqo.get_hosts_list(queue_number, activity)
            nature_hosts_list.append(temp_host_dict)
            fileloader.dump_queues(aqo.get_all_queues())
            response = f"{nature_role.mention} {ctx.message.author.mention} is doing naturalist missions and has " \
                       f' {str(slots)} open slots! Join with `!j n @mention` the host'
            psn_names = fileloader.load_json(FilePaths.json_psn)
            if host_id in psn_names:
                response += f"\n\n{host_display_name}'s PSN is **{psn_names[host_id]}**. Add them if you haven't already!"
            await ctx.channel.send(response)
            if FilePaths.commands_cog_file_path not in list(self.bot.extensions):
                self.bot.load_extension(FilePaths.commands_cog_file_path)
            if FilePaths.naturalist_commands_cog_file_path not in list(self.bot.extensions):
                self.bot.load_extension(FilePaths.naturalist_commands_cog_file_path)
        else:
            response = "You are already hosting naturalist missions, you silly ass! If you wish to clear your helpers " \
                       "and start a new one, type `!c n`"
            await ctx.channel.send(response)

    # =================================================== #
    # ==========BOT COMMAND TO CREATE A POSSE============ #
    # =================================================== #
    @commands.command(name='posse',
                      aliases=['p'],
                      help=f'Creates a general posse, where slots is the number of posse members needed [max 6]')
    async def create_posse(self, ctx, slots: int):
        await ctx.channel.trigger_typing()
        if slots <= 0 or slots >= 7:
            response = "Amount of slots requested is out of posse size range"
            await ctx.channel.send(response)
            return

        # Get the host display name and host id from discord
        host_display_name = ctx.message.author.display_name
        host_id = str(ctx.message.author.id)

        # Get the time created and convert to str for JSON
        time_created = ctx.message.created_at
        time_created = convert_date_to_str(time_created)

        queue_number, activity = aqo.get_queue_info('p')

        list_of_host_ids = aqo.get_list_of_host_ids(activity)


        if host_id not in list_of_host_ids:
            x = 1
            channel_role = None
            while channel_role is None:
                role_string = f'{activity}-channel-' + str(x)
                channel_role = discord.utils.find(lambda m: m.name == role_string, self.guild.roles)
                if channel_role is None:
                    channel_role = await self.guild.create_role(name=role_string)
                    await ctx.message.author.add_roles(channel_role)
                else:
                    x += 1

            overwrites = {
                self.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                channel_role: discord.PermissionOverwrite(send_messages=True)
            }
            category = self.guild.get_channel(738472531127959602)
            channel = await self.guild.create_text_channel(f'{activity}-channel-{str(x)}', category=category,
                                                           overwrites=overwrites)

            temp_host_dict = {}
            temp_host_dict.update({'host_name': host_display_name})
            temp_host_dict.update({'host_id': host_id})
            temp_host_dict.update({'members': [{host_id: host_display_name}]})
            temp_host_dict.update({'time_created': time_created})
            temp_host_dict.update({'status': 'active'})
            temp_host_dict.update({'slots': slots})
            temp_host_dict.update({'activity_room': channel_role.name})
            delivery_hosts_list = aqo.get_hosts_list(queue_number, activity)
            delivery_hosts_list.append(temp_host_dict)
            fileloader.dump_queues(aqo.get_all_queues())
            response = f"{ctx.message.author.mention} has started a general posse with {str(slots)} open slots! Join " \
                       f"with `!j p @mention` the host \n\nPrivate channel {channel.mention} has been cre" \
                       f"ated under {category.name} for the posse's convenience. Feel free to use it!"
            psn_names = fileloader.load_json(FilePaths.json_psn)
            if host_id in psn_names:
                response += f"\n\n{host_display_name}'s PSN is **{psn_names[host_id]}**. Add them if you haven't already!"
            if FilePaths.commands_cog_file_path not in list(self.bot.extensions):
                self.bot.load_extension(FilePaths.commands_cog_file_path)
            await ctx.channel.send(response)
        else:
            response = "You are already hosting a general posse, you silly ass! If you wish to clear it and start a new one, " \
                       "type `!c p`"
            await ctx.channel.send(response)

    # =================================================== #
    # =======BOT COMMAND TO VIEW A QUEUE================= #
    # =================================================== #

    @commands.command(name='q',
                      help='Get info on current active role posses. You can pass in a role initial to see only queues '
                           'specific to that role, or just leave it blank to see them all!')
    async def view_queues(self, ctx, *role):
        await ctx.channel.trigger_typing()
        if not role:
            delivery_hosts = aqo.get_hosts_list(0, ActivityStrings.delivery_str)
            moonshine_hosts = aqo.get_hosts_list(1, ActivityStrings.moonshine_str)
            bounty_hosts = aqo.get_hosts_list(2, ActivityStrings.bounty_str)
            nature_hosts = aqo.get_hosts_list(3, ActivityStrings.nature_str)
            posse_hosts = aqo.get_hosts_list(4, ActivityStrings.posse_str)

            if not delivery_hosts and not moonshine_hosts and not bounty_hosts and not nature_hosts and not posse_hosts:
                await ctx.channel.send(f'There are currently no activity posses set up. You should do that!')
                return

            list_of_hosts_lists = [delivery_hosts, moonshine_hosts, bounty_hosts, nature_hosts, posse_hosts]
            for hosts_lists in list_of_hosts_lists:
                if hosts_lists:
                    for host_dict in hosts_lists:
                        if hosts_lists == delivery_hosts:
                            embed = self.generate_queue_embed(ActivityStrings.delivery_str, host_dict)
                        elif hosts_lists == moonshine_hosts:
                            embed = self.generate_queue_embed(ActivityStrings.moonshine_str, host_dict)
                        elif hosts_lists == bounty_hosts:
                            embed = self.generate_queue_embed(ActivityStrings.bounty_str, host_dict)
                        elif hosts_lists == nature_hosts:
                            embed = self.generate_queue_embed(ActivityStrings.nature_str, host_dict)
                        elif hosts_lists == posse_hosts:
                            embed = self.generate_queue_embed(ActivityStrings.posse_str, host_dict)
                        else:
                            embed = None
                        if embed:
                            await ctx.channel.send(embed=embed)
                else:
                    continue
        else:
            queue_number, activity = aqo.get_queue_info(role[0])
            if activity is None:
                await ctx.channel.send(f'Enter an accurate role initial after !q, for example, "!q d" or !q n" - or '
                                       f'just enter "!q" to see all activity posses')
                return
            hosts_lists = aqo.get_hosts_list(queue_number, activity)
            if not hosts_lists:
                await ctx.channel.send(f'Nobody is hosting a {activity} posse. You should start one!')
                return
            for host_dict in hosts_lists:
                embed = self.generate_queue_embed(activity, host_dict)
                await ctx.channel.send(embed=embed)

    @create_nature.error
    @create_delivery.error
    @create_bounty.error
    @create_moonshine.error
    async def error_handler(self, ctx, error):
        if isinstance(error, ChannelError):
            await ctx.send(error)
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'slots':
                await ctx.channel.send(f'Specify the number of slots you need to fill. For example, "!d 6" or "!b 3"')



def setup(bot):
    bot.add_cog(StartRDORoles(bot))
