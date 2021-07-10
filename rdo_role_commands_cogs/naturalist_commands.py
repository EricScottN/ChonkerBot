from discord.ext import commands
from config.queue_objects import aqo
from config.fileloader import fileloader
from config.all_global_variables import ActivityStrings


class NaturalistCommands(commands.Cog, name='Naturalist Commands'):
    """Commands specific to the naturalist role"""
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='nt',
                          help="Allows the host of a naturalist role posse to transfer host to member")
    async def transfer_naturalist(self, ctx):
        host_id = str(ctx.message.author.id)
        member_id = str(ctx.message.mentions[0].id)
        member_display_name = ctx.message.mentions[0].display_name


        if member_id == "668885664925876257":
            response = "I don't want to play sowwwwwyyyyy"
            await ctx.channel.send(response)
            return
        list_of_host_ids = aqo.get_list_of_host_ids(ActivityStrings.nature_str)

        if host_id not in list_of_host_ids:
            response = 'You are not hosting naturalist missions'
            await ctx.channel.send(response)
            return

        if member_id == host_id:
            response = "Umm... You are the host dumb dumb"
            await ctx.channel.send(response)
            return

        list_of_members_dicts = aqo.get_list_of_members(host_id, ActivityStrings.nature_str)

        for member_dict in list_of_members_dicts:
            if member_id in member_dict:
                host_dict = aqo.get_host_dict(host_id, ActivityStrings.nature_str)
                host_dict['host_name'] = member_display_name
                host_dict['host_id'] = member_id
                fileloader.dump_queues(aqo.get_all_queues())
                await ctx.channel.send(f'{member_display_name} is now the host! I hope you thanked everybody first!')
                return
        await ctx.channel.send(f'Could not find {member_display_name}')

    @commands.command(name='na',
                      help="Allows naturalist role host to give members an option of which legendary animal to hunt")
    async def animal_select(self, ctx, *animals):
        host_id = str(ctx.message.author.id)
        host_display_name = ctx.message.author.display_name
        list_of_host_ids = aqo.get_list_of_host_ids(ActivityStrings.nature_str)
        if host_id not in list_of_host_ids:
            response = 'You are not hosting naturalist missions'
            await ctx.channel.send(response)
            return
        if len(animals) == 0:
            await ctx.channel.send(
                f'Specify the animals you are proposing to hunt in this format: !na animal1 animal2 animal3 etc.')
            return

        response = ''
        list_of_members_dicts = aqo.get_list_of_members(host_id, ActivityStrings.nature_str)
        members_string = ''
        for member_dict in list_of_members_dicts:
            for key in member_dict:
                if key != host_id:
                    members_string += f'<@{key}> '
        if members_string == '':
            await ctx.channel.send(f'You are alone :(')
            return

        animal_string = ''
        emojis = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
        total_animals = 0
        for item in animals:
            animal_string += f'{emojis[total_animals]} {item.upper()}\n'
            total_animals += 1

        message = await ctx.channel.send(
            f'{members_string} - {host_display_name} would like you to vote between the following animals:\n\n{animal_string}')

        i = 0
        while i < total_animals:
            await message.add_reaction(emojis[i])
            i += 1


def setup(bot):
    bot.add_cog(NaturalistCommands(bot))