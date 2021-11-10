from discord.ext import commands
from config.fileloader import fileloader
from config.all_global_variables import FilePaths

class ConfigCommands(commands.Cog, name='Config Commands'):
    """Configure your stuff with ChonkerBot"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='psn',
                      help='Register your PSN name with the bot by entering you PSN name after !psn')
    async def psn(self, ctx, psn_name):
        psn_dict = fileloader.load_json(FilePaths.json_psn)
        member_id = str(ctx.message.author.id)

        if member_id not in psn_dict:
            psn_dict[member_id] = {}
            psn_dict[member_id] = psn_name
            response = f"Your PSN name is now registered as {psn_name}! Now people can stop bothering you for it :)"
        else:
            old_name = psn_dict[member_id]
            psn_dict[member_id] = psn_name
            response = f"I updated your PSN name from {old_name} to {psn_name}! Isn't that nice?"

        fileloader.dump_json(psn_dict, FilePaths.json_psn)
        await ctx.channel.send(response)

def setup(bot):
    bot.add_cog(ConfigCommands(bot))
