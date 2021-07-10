import discord
from discord.ext import commands

prefix = '!'
bot_title = ''
bot_description = ''
bottom_info = ''

class Help(commands.Cog):
    """ Help commands """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help',
                      description='Help command',
                      aliases=['info'],
                      case_insensitive=True)
    async def help_command(self, ctx, *commands: str):
        """ Shows this message """
        bot = ctx.bot


        def generate_usage(command_name):
            """ Generates a string of how to use a command """
            temp = f'{prefix}'
            command = bot.get_command(command_name)
            # Aliases
            if len(command.aliases) == 0:
                temp += f'{command_name}'
            elif len(command.aliases) == 1:
                temp += f'[{command.name}|{command.aliases[0]}]'
            else:
                t = '|'.join(command.aliases)
                temp += f'[{command.name}|{t}]'
            # Parameters
            params = f' '
            for param in command.clean_params:
                params += f'<{param}> '
            temp += f'{params}'
            return temp

        def generate_command_list(cog):
            """ Generates the command list with properly spaced help messages """
            # Determine longest word
            max = 0
            for command in bot.get_cog(cog).get_commands():
                if not command.hidden:
                    if command.aliases:
                        aliases = '|'.join([str(elem) for elem in command.aliases])
                    else:
                        aliases = ''
                    if len(f'{aliases}|{command}') > max:
                        max = len(f'{aliases}|{command}')
            # Build list
            temp = ""
            for command in bot.get_cog(cog).get_commands():
                if command.hidden:
                    temp += ''
                elif command.help is None:
                    temp += f'|{aliases}|{command}\n'
                else:
                    if command.aliases:
                        aliases = '|'.join([str(elem) for elem in command.aliases])
                        temp += f'`|{aliases}|{command}|`'
                    else:
                        aliases = ''
                        temp += f'`|{command}|`'
                    for i in range(0, max - len(f'{aliases}|{command}') + 1):
                        temp += '   '
                    temp += f'{command.help}\n'
            return temp

        # Help by itself just lists our own commands.
        if len(commands) == 0:
            embed = discord.Embed(title='ALL COMMANDS', description=f'A list of all currently available '
                                                                    f'commands\n*NOTE*: Some commands may be hidden '
                                                                    f'until a role posse is started')
            for cog in bot.cogs:
                temp = generate_command_list(cog)
                if temp != "":
                    embed.add_field(name=f'**{cog}**', value=temp, inline=False)
            if bottom_info != "":
                embed.add_field(name="Info", value=bottom_info, inline=False)
        elif len(commands) >= 1:

            # Try to see if it is a cog name
            name = ' '.join(commands)
            cog = bot.get_cog(name)
            if cog is not None:
                embed = discord.Embed(title='CATEGORY COMMANDS', description=f'A list of all category commands')
                msg = generate_command_list(name)
                embed.add_field(name=name, value=msg, inline=False)
                msg = f'{cog.description}\n'
                embed.set_footer(text=msg)

            # Must be a command then
            else:
                embed = discord.Embed(title='COMMAND', description=f'A description of the command is shown below')
                command = bot.get_command(name)
                if command is not None:
                    help = f''
                    if command.help is not None:
                        help = command.help
                    embed.add_field(name=f'{command.description}```{generate_usage(name)}```',
                                    value=f'{help}',
                                    inline=False)
                else:
                    msg = ' '.join(commands)
                    embed.add_field(name="Not found", value=f'Command/category `{msg}` not found.')
        else:

            msg = ' '.join(commands)
            embed = discord.Embed(title="NOT FOUND", description=f'Command/category `{msg}` not found.')

        await ctx.send(embed=embed)
        return


# Cog setup
def setup(bot):
    bot.add_cog(Help(bot))
