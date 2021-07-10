import discord
from discord.ext import commands
from config.all_global_variables import ActivityStrings
from config.queue_objects import aqo
from config.fileloader import fileloader
from config.queue_manipulator import qm

class AllCommands(commands.Cog, name='All Commands'):
    """All commands that can be used regardless of role."""
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(668621889593278464)

    def is_commmand_names(self, arg):
        RDO_Cog = self.bot.get_cog('Start RDO Roles')
        rdocommands = RDO_Cog.get_commands()
        all_role_commands = []
        for rdocommand in rdocommands:
            if rdocommand.name is not 'queue':
                all_role_commands.append(rdocommand.name)
                for i in range(len(rdocommand.aliases)):
                    all_role_commands.append(rdocommand.aliases[i])
        if arg in all_role_commands:
            return arg
        else:
            return None

    # =================================================== #
    # =======BOT COMMAND TO JOIN A DELIVERY  ============ #
    # =================================================== #
    @commands.command(name='j',
                      help="Join a hosts role posse")
    async def join(self, ctx, role, member: discord.Member):

        if not self.is_commmand_names(role):
            response = f"Could not locate role command `{role}`"
            await ctx.channel.send(response)
            return

        if not member:
            response = f"Could not locate member `{member}`"
            await ctx.channel.send(response)
            return

        host_display_name = member.display_name
        host_id = str(member.id)

        if member is self.bot:
            response = "If I had fingers I would play! Unfortunately.. "
            await ctx.channel.send(response)
            return

        if role is not None:
            queue_number, activity = aqo.get_queue_info(role)

        # Get the members display name and id from discord message
        member_display_name = ctx.message.author.display_name
        member_id = str(ctx.message.author.id)

        hosts_lists = aqo.get_hosts_list(queue_number, activity)

        # Check if there are any active queues (nature queues)
        if not hosts_lists:
            response = f'Nobody is hosting a {activity} posse right now'
            await ctx.channel.send(response)
            return

        # Check if member is host ( of nature queue)
        if member_id == host_id:
            response = f'Umm... You\'re already hosting a {activity} posse. Get going!'
            await ctx.channel.send(response)
            return

        list_of_host_ids = aqo.get_list_of_host_ids(activity)
        if host_id not in list_of_host_ids:
            response = host_display_name + f' is not currently hosting a {activity} posse. If you ask nicely maybe ' \
                                           f'they will :P '
            await ctx.channel.send(response)
            return

        # Get the hosts dictionary of information
        host_dict = aqo.get_host_dict(host_id, activity)

        if host_dict['activity_room'] is not '':
            name = host_dict['activity_room']
            role = discord.utils.find(lambda m: m.name == name, self.guild.roles)
            if role is not None:
                await ctx.message.author.add_roles(role)


        # Get a important information from host dictionary
        list_of_members_dicts = aqo.get_list_of_members(host_id, activity)
        slots = host_dict['slots']

        # Check if member is already in queue
        for member_dict in list_of_members_dicts:
            if member_id in member_dict:
                response = f'You are already helping this host with naturalist missions. Maybe there\'s another you ' \
                           f'can join!'
                await ctx.channel.send(response)
                return

        # Check if host queue is full
        if host_dict['status'] == 'full' or slots == 0:
            response = f'There is no more room in that hosts {activity} posse. Booooohooooo'
            await ctx.channel.send(response)
            return

        # Call function to add member to queue
        qm.add_to_queue(list_of_members_dicts, member_id, member_display_name)

        # Remove one slot from slow
        host_dict['slots'] = host_dict['slots'] - 1

        if host_dict['slots'] == 0:
            host_dict['status'] = 'full'
            response = f"Added {member_display_name} to {host_display_name}'s {activity} posse!\n\n" \
                       f"**<@{host_id}>'s posse is now full**"
            fileloader.dump_queues(aqo.get_all_queues())
            await ctx.channel.send(response)
            return
        else:
            # load queue back to JSON
            fileloader.dump_queues(aqo.get_all_queues())
            response = f"Added {member_display_name} to {host_display_name}'s {activity} posse! YAY!"
            await ctx.channel.send(response)

    # =================================================== #
    # =======BOT COMMAND TO CLEAR A QUEUE================= #
    # =================================================== #
    @commands.command(name='c',
                      help='Allows a host to clear their role posse')
    async def clear(self, ctx, role):
        host_id = str(ctx.message.author.id)

        if role is not None:
            queue_number, activity = aqo.get_queue_info(role)

        list_of_host_ids = aqo.get_list_of_host_ids(activity)

        # Check if host id is in list of host ids
        if host_id not in list_of_host_ids:
            response = f"You are not hosting a {activity} posse"
            await ctx.channel.send(response)

        # Get list of bounties host dicts
        hosts_list = aqo.get_hosts_list(queue_number, activity)

        i = 0
        for host_dict in hosts_list:
            if host_dict['host_id'] == host_id:
                if host_dict['activity_room'] is not '':
                    name = host_dict['activity_room']
                    nature_channel = discord.utils.find(lambda m: m.name == name, self.guild.channels)
                    nature_role = discord.utils.find(lambda m: m.name == name, self.guild.roles)
                    if nature_channel is not None:
                        await nature_channel.delete()
                    if nature_role is not None:
                        await nature_role.delete()
                del hosts_list[i]
                response = f"Cleared you as a host for your {activity} posse and deleted any private rooms you may have " \
                           "been hosting. Let's do it again soon! "
                await ctx.channel.send(response)
            i += 1

        # load queue back to JSON
        fileloader.dump_queues(aqo.get_all_queues())

    # =================================================== #
    # =======BOT COMMAND TO MARK QUEUE FULL============== #
    # =================================================== #
    ##Bot command to mark nature as full
    @commands.command(name='f',
                      help='Allows a host to mark their role posse full')
    async def full(self, ctx, role):
        host_id = str(ctx.message.author.id)

        if role is not None:
            queue_number, activity = aqo.get_queue_info(role)

        list_of_host_ids = aqo.get_list_of_host_ids(activity)

        # Check if host id is in list of host ids
        if host_id not in list_of_host_ids:
            response = f'You are not currently hosting any {activity} posse\'s'
            await ctx.channel.send(response)
            return

        # Call queue objects to get a list of hosts and their dicts of info
        hosts_list = aqo.get_hosts_list(queue_number, activity)

        for host_dict in hosts_list:
            if host_dict['host_id'] == host_id:
                host_dict['status'] = 'full'
                host_dict['slots'] = 0
                fileloader.dump_queues(aqo.get_all_queues())
                response = f'Your {activity} posse is now full! WWWeeeeee!'
                await ctx.channel.send(response)

    # =================================================== #
    # ==========BOT COMMAND TO MODIFY SLOTS============== #
    # =================================================== #
    @commands.command(name='slots',
                      help="Allows a host to update the number of slots NEEDED for their role posse")
    async def modify(self, ctx, role, slots: int):
        host_id = str(ctx.message.author.id)

        if role is not None:
            queue_number, activity = aqo.get_queue_info(role)

        list_of_host_ids = aqo.get_list_of_host_ids(activity)

        if host_id not in list_of_host_ids:
            response = f"You are not currently hosting a {activity} posse"
            await ctx.channel.send(response)
            return
        if activity == ActivityStrings.bounty_str:
            max_slots = 4
        else:
            max_slots = 7

        if slots < 0 or slots >= max_slots:
            response = "Amount of slots requested is out of posse size range. How long have you played this game?"
            await ctx.channel.send(response)
            return

        host_dict = aqo.get_host_dict(host_id, activity)

        if slots == host_dict['slots']:
            response = "You already have that many slots. It's okay. Math is hard."
            await ctx.channel.send(response)
            return

        list_of_members_dicts = aqo.get_list_of_members(host_id, activity)

        if len(list_of_members_dicts) + slots > max_slots:
            response = f"The amount of slots requested will overpack your posse. " \
                       f"Consider lowering the amount of slots requested or removing somebody from your {activity} posse"
            await ctx.channel.send(response)
            return
        else:
            if slots == 0:
                host_dict['slots'] = 0
                host_dict['status'] = 'full'
                response = f"I modified your available slots to zero, but next time consider using `!{role} f` " \
                           f"instead to mark your {activity} posse full!"
            else:
                host_dict['slots'] = slots
                host_dict['status'] = 'active'
                response = f"Success! You now have **{str(host_dict['slots'])} slots available** in you {activity} posse"

            fileloader.dump_queues(aqo.get_all_queues())
        await ctx.channel.send(response)

    # =================================================== #
    # =======BOT COMMAND TO REMOVE FROM NATURE========= #
    # =================================================== #
    @commands.command(name='rm',
                      help="Allows a host to remove a member from their role posse")
    async def remove(self, ctx, role, member: discord.Member):
        host_id = str(ctx.message.author.id)
        member_id = str(member.id)

        if role is not None:
            queue_number, activity = aqo.get_queue_info(role)

        if member_id == host_id:
            response = f"Leaving your posse out to dry? If you want to cancel your " \
                       f"{activity} posse, use `{role} c`"
            await ctx.channel.send(response)
            return

        list_of_host_ids = aqo.get_list_of_host_ids(activity)

        if host_id not in list_of_host_ids:
            response = f"You are not currently hosting a {activity} posse."
            await ctx.channel.send(response)
            return

        member_display_name = ctx.message.mentions[0].display_name

        list_of_members_dicts = aqo.get_list_of_members(host_id, activity)
        i = 1
        for member_dict in list_of_members_dicts[1:]:
            if member_id in member_dict:
                host_dict = aqo.get_host_dict(host_id, activity)
                if host_dict['activity_room'] is not '':
                    name = host_dict['activity_room']
                    channel_role = discord.utils.find(lambda m: m.name == name, self.guild.roles)
                    if channel_role is not None:
                        await ctx.message.mentions[0].remove_roles(channel_role)
                del list_of_members_dicts[i]
                host_dict = aqo.get_host_dict(host_id, activity)
                host_dict['slots'] = host_dict['slots'] + 1
                if host_dict['status'] == 'full':
                    host_dict['status'] = 'active'
                fileloader.dump_queues(aqo.get_all_queues())
                response = f"{member_display_name} has been removed from your {activity} posse. Bye {member_display_name}!"

                await ctx.channel.send(response)
                return
            i += 1
        response = f"{member_display_name} is not currently in your {activity} posse. You can always view " \
                   f"your current your posse " \
                   f"by using the `!q` or `!q {role}`"
        await ctx.channel.send(response)
        return

    @commands.command(name='l',
                      help="Allows a member to leave a hosts role posse")
    async def leave(self, ctx, role, member: discord.Member):
        host_display_name = member.display_name
        host_id = str(member.id)

        if host_id == "668885664925876257":
            response = "You know I can't play this game."
            await ctx.channel.send(response)
            return

        if role is not None:
            queue_number, activity = aqo.get_queue_info(role)

        # Get the members display name and id from discord message
        member_display_name = ctx.message.author.display_name
        member_id = str(ctx.message.author.id)
        hosts_lists = aqo.get_hosts_list(queue_number, activity)
        # Check if there are any active queues (delivery queues)
        if not hosts_lists:
            response = f'Nobody is hosting a {activity} posse right now'
            await ctx.channel.send(response)
            return

        # Check if member is host ( of delivery queue)
        if member_id == host_id:
            response = f"You cannot leave as host. If you would like to cancel it, use `!c {role}`"
            await ctx.channel.send(response)
            return

        list_of_host_ids = aqo.get_list_of_host_ids(activity)
        # Check if discord host_id exists in list of host ids
        if host_id not in list_of_host_ids:
            response = host_display_name + f' is not currently hosting a {activity} posse. If you ask nicely maybe ' \
                                           f'they will :P '
            await ctx.channel.send(response)
            return

        # Get a important information from host dictionary
        list_of_members_dicts = aqo.get_list_of_members(host_id, activity)

        i = 0
        for member_dict in list_of_members_dicts:
            if member_id in member_dict:
                host_dict = aqo.get_host_dict(host_id, activity)
                if host_dict['activity_room'] is not '':
                    name = host_dict['activity_room']
                    channel_role = discord.utils.find(lambda m: m.name == name, self.guild.roles)
                    if channel_role is not None:
                        await ctx.message.author.remove_roles(channel_role)
                del list_of_members_dicts[i]
                host_dict['slots'] = host_dict['slots'] + 1
                if host_dict['status'] == 'full':
                    host_dict['status'] = 'active'
                fileloader.dump_queues(aqo.get_all_queues())
                response = f"{member_display_name} has been successfully removed from {host_display_name}'s {activity} posse. BYEBYE! "
                await ctx.channel.send(response)
                return
            i += 1
        response = f"You are currently not helping that host. You can always view the current queue " \
                   f"by using the `!q` or `!q {role}` or join them by using `!j {role} @mention` the host"
        await ctx.channel.send(response)
        return

    @commands.command(name='move',
                      help="Allows the host of a role posse to create a separate room where only the posse can send "
                           "messages")
    async def move_channel(self, ctx, role):
        host_id = str(ctx.message.author.id)

        if role is not None:
            queue_number, activity = aqo.get_queue_info(role)

        list_of_host_ids = aqo.get_list_of_host_ids(activity)

        if host_id not in list_of_host_ids:
            response = f'You are not currently hosting any {activity} posse\'s'
            await ctx.channel.send(response)
            return

        host_dict = aqo.get_host_dict(host_id, activity)
        if host_dict['activity_room'] is not '':
            response = f'You are already hosting in a private {activity} room'
            await ctx.channel.send(response)
            return


        x = 1
        channel_role = None
        while channel_role is None:
            role_string = f'{activity}-channel-' + str(x)
            channel_role = discord.utils.find(lambda m: m.name == role_string, self.guild.roles)
            if channel_role is None:
                channel_role = await self.guild.create_role(name=role_string)
            else:
                x += 1

        host_dict['activity_room'] = channel_role.name
        fileloader.dump_queues(aqo.get_all_queues())

        list_of_members_dicts = aqo.get_list_of_members(host_id, activity)
        for member_dict in list_of_members_dicts:
            for key in member_dict:
                member_id = (int(key))
                member = discord.utils.find(lambda m: m.id == member_id, self.guild.members)
                if member is not None:
                    await member.add_roles(channel_role)

        overwrites = {
            self.guild.default_role: discord.PermissionOverwrite(send_messages=False),
            channel_role: discord.PermissionOverwrite(send_messages=True)
        }
        category = self.guild.get_channel(738472531127959602)
        channel = await self.guild.create_text_channel(f'{activity}-channel-{str(x)}', category=category, overwrites=overwrites)
        response = f'Successfully created private channel\n\n**NAME: {channel.mention}**\nYou can find it at the ' \
                   f'bottom of the channel list under the Activity Rooms category!  '
        await ctx.channel.send(response)

    @join.error
    @clear.error
    @full.error
    @remove.error
    @modify.error
    @leave.error
    @move_channel.error
    async def error_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if len(error.args) == 1 and error.param.name is 'member':
                if isinstance(error.param.name, str):
                    await ctx.channel.send(f'Please specify a member')
                else:
                    await ctx.channel.send(f'Please provide a role')
            elif error.param.name is 'slots':
                await ctx.channel.send(f'Please specify the number of slots you need')
            elif error.param.name is 'member':
                await ctx.channel.send(f'Please specify a member')
            elif error.param.name is 'role':
                await ctx.channel.send(f'Please provide a role')

        raise error

def setup(bot):
    bot.add_cog(AllCommands(bot))
