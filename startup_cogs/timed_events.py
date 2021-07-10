import discord
from config.all_global_variables import *
from discord.ext import commands, tasks
from config.queue_objects import aqo
import datetime
import asyncio
from config.convert_time import *
from config.fileloader import fileloader


class TimedEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Discord Channel IDs
        self.announcements_channel_id = DiscordChannels.announcements_channel_id
        self.heftychonks_channel_id = DiscordChannels.heftychonks_channel_id
        self.heftychonks_rules_channel_id = DiscordChannels.heftychonks_rules_channel_id

        # Discord Role IDs
        self.delivery_role_id = DiscordRoles.delivery_role_id
        self.heftychonks_role_id = DiscordRoles.heftychonks_role_id
        self.heckinadmin_role_id = DiscordRoles.heckinadmin_role_id
        self.chonkerbot_role_id = DiscordRoles.chonkerbot_role_id
        self.megachonkers_role_id = DiscordRoles.megachonkers_role_id

        # Get Discord Guild
        self.guild = self.bot.get_guild(DiscordGuilds.heckinchonkers_id)

        # Set active channels
        self.delivery_active_channel = self.guild.get_channel(ActiveChannels.delivery_active_channel)
        self.bounty_active_channel = self.guild.get_channel(ActiveChannels.bounty_active_channel)
        self.nature_active_channel = self.guild.get_channel(ActiveChannels.nature_active_channel)
        self.moonshine_active_channel = self.guild.get_channel(ActiveChannels.moonshine_active_channel)
        self.stb_active_channel = self.guild.get_channel(ActiveChannels.stb_active_channel)
        self.general_active_channel = self.guild.get_channel(ActiveChannels.general_active_channel)
        self.bot_testing_channel = self.guild.get_channel(DiscordChannels.bot_testing_channel_id)

        # Get Discord Channels
        self.announcements_channel = self.guild.get_channel(self.announcements_channel_id)
        self.heftychonks_channel = self.guild.get_channel(self.heftychonks_channel_id)
        self.heftychonks_rules_channel = self.guild.get_channel(self.heftychonks_rules_channel_id)

        # Get Discord Roles
        self.delivery_role = self.guild.get_role(self.delivery_role_id)
        self.heftychonks_role = self.guild.get_role(self.heftychonks_role_id)
        self.heckinadmin_role = self.guild.get_role(self.heckinadmin_role_id)
        self.chonkerbot_role = self.guild.get_role(self.chonkerbot_role_id)
        self.megachonkers_role = self.guild.get_role(self.megachonkers_role_id)

        # Start Tasks Loops
        self.check_queue_times.start()
        #self.trade_route_reminder.start()
        self.update_heftychonks.start()

    async def queue_helper(self, activity):
        if activity == ActivityStrings.delivery_str:
            queue_number = 0
        elif activity == ActivityStrings.moonshine_str:
            queue_number = 1
        elif activity == ActivityStrings.bounty_str:
            queue_number = 2
        elif activity == ActivityStrings.nature_str:
            queue_number = 3
        elif activity == ActivityStrings.posse_str:
            queue_number = 4

        hosts_list = aqo.get_hosts_list(queue_number, activity)
        response = f'you did not respond in the allotted time so I deleted your {activity} posse for you, ' \
                   f'as well as any private rooms you were hosting. '

        if not hosts_list:
            return False
        else:
            try:
                current_datetime = datetime.utcnow()
            except Exception as e:
                    print(e)
            i = 0
            for host_dict in hosts_list:
                creation_datetime_str = host_dict['time_created']
                creation_datetime = convert_str_to_date(creation_datetime_str)
                time_pass = current_datetime - creation_datetime
                time_pass_in_s = time_pass.total_seconds()
                minutes = divmod(time_pass_in_s, 60)[0]

                if activity == ActivityStrings.delivery_str:
                    if minutes >= 60:
                        current_channel = self.delivery_active_channel
                    else:
                        continue
                elif activity == ActivityStrings.moonshine_str:
                    if minutes >= 60:
                        current_channel = self.moonshine_active_channel
                    else:
                        continue
                elif activity == ActivityStrings.bounty_str:
                    if minutes >= 60:
                        current_channel = self.bounty_active_channel
                    else:
                        continue
                elif activity == ActivityStrings.nature_str:
                    if minutes >= 120:
                        current_channel = self.nature_active_channel
                    else:
                        continue
                elif activity == ActivityStrings.posse_str:
                    if minutes >= 180:
                        current_channel = self.general_active_channel
                    else:
                        continue

                host = self.bot.get_user(int(host_dict['host_id']))
                extend = await self.extend_time(current_channel, host, activity)
                if extend == 'x':
                    host_dict['time_created'] = convert_date_to_str(current_datetime)
                    fileloader.dump_queues(aqo.get_all_queues())
                    await current_channel.send(f"Extended your queue!")
                    continue
                if extend != 'x' and extend is not False:
                    continue
                if host_dict['activity_room'] != '':
                    name = host_dict['activity_room']
                    channel = discord.utils.find(lambda m: m.name == name, self.guild.channels)
                    role = discord.utils.find(lambda m: m.name == name, self.guild.roles)
                    if channel is not None:
                        await channel.delete()
                    if role is not None:
                        await role.delete()

                del hosts_list[i]
                fileloader.dump_queues(aqo.get_all_queues())
                await current_channel.send(f"Hey {host.display_name}, {response}")
            i += 1
            return True

    @tasks.loop(seconds=60.0)
    async def trade_route_reminder(self):
        now = datetime.datetime.utcnow()
        time = datetime.time(hour=now.hour, minute=now.minute)
        trade_route_times = [datetime.time(12, 12),
                             datetime.time(19, 42),
                             datetime.time(4, 42)]

        if time in trade_route_times:
            # TODO Change this to delivery channel
            await self.delivery_active_channel.send(f'{self.delivery_role.mention} **Trade Route Event begins in 10 minutes!**\n\n '
                                    f'CHOOO-CHOOOOOOO - ALL ABOARD!')

    @tasks.loop(hours=24.0)
    async def update_heftychonks(self):
        today = datetime.today()
        today_month = today.month
        thx_dict = fileloader.load_thanks()

        if thx_dict['month'] == today_month:
            return


        top_ten = []
        top_ten_string = ''
        all_thx_string = ''
        sorted_thx = sorted(thx_dict.items(), key=lambda x: x[1], reverse=True)
        heftychonk_role_members = self.heftychonks_role.members
        x = 1
        for thx in sorted_thx:
            if thx[0] == 'month':
                continue
            thx_id = (int(thx[0]))
            amt_of_thx = thx[1]
            member = discord.utils.find(lambda m: m.id == thx_id, self.guild.members)
            if member is not None:
                all_thx_string += f'`{str(x).rjust(2)}. {str(amt_of_thx).rjust(2)} thx - {member.display_name}`\n'
            if len(top_ten) <= 9:
                top_ten.append(member)
                top_ten_string += f"{str(x)}. {member.mention} - {amt_of_thx} thanks\n"
            x += 1

        print(top_ten)
        top_two = []
        for member in top_ten:
            if member.top_role >= self.megachonkers_role:
                pass
            else:
                top_two.append(member)
                if len(top_two) <= 1:
                    continue
                else:
                    break

        print(top_two)
        if heftychonk_role_members:
            for member in heftychonk_role_members:
                if member not in top_two:
                    await member.remove_roles(self.heftychonks_role)

        promoted_str = ""
        retained_str = ""
        heft_channel_str = ""
        for top in top_two:
            if top not in heftychonk_role_members:
                promoted_str += f"**{top.display_name}**\n"
                heft_channel_str += f"{top.mention}\n"
                await top.add_roles(self.heftychonks_role)
            else:
                retained_str += f"**{top.display_name} has retained the {self.heftychonks_role.mention} mod role " \
                                f"again this month! Keep being awesome!**\n"

        response = f"**LAST MONTHS TOP TEN !THX MEMBERS**\n{top_ten_string}\n"
        if promoted_str:
            response += f"**THE FOLLOWING MEMBERS HAVE BEEN " \
                    f"PROMOTED TO THE {self.heftychonks_role.mention} MOD ROLE FOR THIS MONTH!**\n{promoted_str}"
        if retained_str:
            response += retained_str
        response += f"\nFor those who didn't get the role this month - keep doing those deliveries, being nice, " \
                    f"and getting them **!thx**"
        await self.announcements_channel.send(response)

        embed = discord.Embed(
            colour=discord.Colour.teal()
        )
        embed.add_field(name='THX RECEIVED BY MEMBER', value=all_thx_string)
        await self.announcements_channel.send(embed=embed)

        if heft_channel_str:
            await self.heftychonks_channel.send(f"**WELCOME TO THE HEFTYCHONKS MOD CHANNEL**\n {heft_channel_str}\nPlease "
                                        f"review the rules over in {self.heftychonks_rules_channel.mention} if you "
                                        f"haven't already. If you still have any questions, feel free to ask in here!")

        fileloader.copy_thx_file(str(thx_dict['month'])+str(today.year))
        thx_dict = {'month': today_month}
        fileloader.dump_thanks(thx_dict)

    @tasks.loop(seconds=60.0)
    async def check_queue_times(self):
        try:
            dq_exists = await self.queue_helper(ActivityStrings.delivery_str)
            mq_exists = await self.queue_helper(ActivityStrings.moonshine_str)
            bq_exists = await self.queue_helper(ActivityStrings.bounty_str)
            nq_exists = await self.queue_helper(ActivityStrings.nature_str)
            pq_exists = await self.queue_helper(ActivityStrings.posse_str)
            if (not dq_exists and not mq_exists and not bq_exists and not nq_exists and not pq_exists
                    and FilePaths.commands_cog_file_path in list(self.bot.extensions)):
                self.bot.unload_extension(FilePaths.commands_cog_file_path)
            if not nq_exists and FilePaths.naturalist_commands_cog_file_path in list(self.bot.extensions):
                self.bot.unload_extension(FilePaths.naturalist_commands_cog_file_path)

        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def extend_time(self, current_channel, host, activity):
        if activity == ActivityStrings.delivery_str:
            response = f'- your delivery has been active for over an hour. Respond "x" to extend your delivery by ' \
                       f'another hour, `!c d` to clear it yourself, or I will delete it automatically in five minutes'
        elif activity == ActivityStrings.moonshine_str:
            response = f'- your moonshine delivery has been active for over an hour. Respond "x" to extend it by ' \
                       f'another hour, `!c m` to clear it yourself, or I will delete it automatically in five minutes'
        elif activity == ActivityStrings.bounty_str:
            response = f'- your bounty hunt has been active for over an hour. Respond "x" to extend your bounty hunt ' \
                       f'by another hour, `!c b` to clear it yourself, or I will delete it automatically in five minutes '
        elif activity == ActivityStrings.nature_str:
            response = f'- your naturalist queue has been active for over two hours. Respond "x" to extend your ' \
                       f'naturalist queue by another two hours, `!c n` to clear it yourself, or I will delete it ' \
                       f'automatically in five minutes '
        elif activity == ActivityStrings.posse_str:
            response = f'- your general posse has been active for over three hours. Respond "x" to extend your ' \
                       f'queue by another three hours, `!c p` to clear it yourself, or I will delete it ' \
                       f'automatically in five minutes '
        await current_channel.send(f"{host.mention}{response}")


        def check(m):
            possible_clear = ['!c d', '!c b', '!c n', '!c m']
            if m.content == 'x' or m.content in possible_clear and m.channel == current_channel and m.author == host:
                return m.content
        try:
            content = await self.bot.wait_for('message', timeout=300.0, check=check)
        except asyncio.TimeoutError:
            return False
        else:
            return content.content

def setup(bot):
    bot.add_cog(TimedEvents(bot))
