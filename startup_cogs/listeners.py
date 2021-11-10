import discord
import random
import datetime
from discord.ext import commands
from config.all_global_variables import DiscordChannels, DiscordGuilds, RoleMessages, FilePaths
from config.fileloader import fileloader



class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(DiscordGuilds.heckinchonkers_id)
        self.reactions_to_square = 3
        self.mentioned_time = None

        # Get Discord MEGACHONKERS channel
        self.megachonkers_channel_id = DiscordChannels.megachonkers_channel_id
        self.megachonkers_channel = self.guild.get_channel(self.megachonkers_channel_id)

        self.stb_channel_id = DiscordChannels.stb_channel_id
        self.stb_channel = self.guild.get_channel(self.stb_channel_id)

        # Get Discord AHeckinAdmin channel
        self.aheckinadmin_channel_id = DiscordChannels.aheckinadmin_channel_id
        self.aheckinadmin_channel = self.guild.get_channel(self.aheckinadmin_channel_id)

        # Get Discord SquareBoard channel
        self.squareboard_channel_id = DiscordChannels.squareboard_channel_id
        self.squareboard_channel = self.guild.get_channel(self.squareboard_channel_id)

    async def return_post(self, message_id):
        channel = self.squareboard_channel
        async for post in channel.history(limit=20):
            if post.embeds:
                if post.embeds[0].footer.text:
                    if str(message_id) in post.embeds[0].footer.text:
                        return post


    # Do more code
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        if message_id in RoleMessages.list_of_role_messages:
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)
            if payload.emoji.name == u"\U0001F44D":
                role = discord.utils.get(guild.roles, name='HeckinTraders')
            if payload.emoji.name == 'bounty':
                role = discord.utils.get(guild.roles, name='BountyHunters')
            if payload.emoji.name == 'moonshiner':
                role = discord.utils.get(guild.roles, name='Moonshiners')
            if payload.emoji.name == 'wagon':
                role = discord.utils.get(guild.roles, name='WagonThieves')
            if payload.emoji.name == 'protection':
                role = discord.utils.get(guild.roles, name='Protectors')
            if payload.emoji.name == 'naturalist':
                role = discord.utils.get(guild.roles, name='NatureFreaks')
            if payload.emoji.name == 'space_thot':
                role = discord.utils.get(guild.roles, name='SpaceThots')
            if payload.emoji.name == 'apex':
                role = discord.utils.get(guild.roles, name='Legends')
            if payload.emoji.name == "💡":
                role = discord.utils.get(guild.roles, name='Jumblies')

            if role is not None:
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
                if member is not None:
                    await member.add_roles(role)
                    embed = discord.Embed(colour=discord.Colour.gold(),
                                          title=f'{member.display_name} has picked up the `{role}` role')
                    await self.megachonkers_channel.send(embed=embed)
                    await self.aheckinadmin_channel.send(embed=embed)
                else:
                    # TODO add to a log
                    print('Member not found')
            else:
                print('Role not found')
        if payload.emoji.name == 'squareclimb':
            channel = self.guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            file = None
            for reaction in message.reactions:
                if reaction.emoji == payload.emoji and reaction.count == self.reactions_to_square:
                    reactions = reaction.count
                    squareboard_post = await self.return_post(payload.message_id)
                    if squareboard_post is None:
                        embed = discord.Embed(colour=discord.Colour.gold())
                        embed.set_author(name=f'{message.author}', icon_url=message.author.avatar_url)
                        if message.content != '':
                            embed.add_field(name="\u200b", value=f'{message.content}\n\n', inline=True)
                        for message_attachment in message.attachments:
                            file = await message_attachment.to_file()
                            embed.set_image(url=f"attachment://{file.filename}")
                        embed.add_field(name="\u200b", value=f'[**GO TO MESSAGE**]({message.jump_url})', inline=False)
                        for message_embed in message.embeds:
                            if message_embed.type == 'video':
                                url = message_embed.thumbnail.url
                            else:
                                url = message_embed.url
                            embed.set_image(url=url)
                        embed.set_footer(text=f'MessageID:{message_id} | {message.created_at.month}/{message.created_at.day}/{message.created_at.year}')
                        await self.squareboard_channel.send(f':star: **{reactions}** |{channel.mention}\n', file=file, embed=embed)
                        return
                elif reaction.emoji == payload.emoji and reaction.count > self.reactions_to_square:
                    reactions = reaction.count
                    squareboard_post = await self.return_post(payload.message_id)
                    if squareboard_post is not None:
                        await squareboard_post.edit(content=f':star: **{reactions}** |{channel.mention}\n')


    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        message_id = payload.message_id
        if message_id in RoleMessages.list_of_role_messages:
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)
            if payload.emoji.name == u"\U0001F44D":
                role = discord.utils.get(guild.roles, name='HeckinTraders')
            if payload.emoji.name == 'bounty':
                role = discord.utils.get(guild.roles, name='BountyHunters')
            if payload.emoji.name == 'moonshiner':
                role = discord.utils.get(guild.roles, name='Moonshiners')
            if payload.emoji.name == 'wagon':
                role = discord.utils.get(guild.roles, name='WagonThieves')
            if payload.emoji.name == 'protection':
                role = discord.utils.get(guild.roles, name='Protectors')
            if payload.emoji.name == 'naturalist':
                role = discord.utils.get(guild.roles, name='NatureFreaks')
            if payload.emoji.name == 'space_thot':
                role = discord.utils.get(guild.roles, name='SpaceThots')
            if payload.emoji.name == 'apex':
                role = discord.utils.get(guild.roles, name='Legends')
            if payload.emoji.name == "💡" :
                role = discord.utils.get(guild.roles, name='Jumblies')

            if role is not None:
                member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
                if member is not None:
                    await member.remove_roles(role)
                    embed = discord.Embed(colour=discord.Colour.gold(),
                                          title=f'{member.display_name} has dropped the `{role}` role')
                    await self.megachonkers_channel.send(embed=embed)
                    await self.aheckinadmin_channel.send(embed=embed)

                    print('done')
                else:
                    print('Member not found')
            else:
                print('Role not found')
        if payload.emoji.name == 'squareclimb':
            # Get the message that was reacted to
            channel = self.guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            for reaction in message.reactions:
                if reaction.emoji == payload.emoji and reaction.count == self.reactions_to_square - 1:
                    squareboard_post = await self.return_post(payload.message_id)
                    if squareboard_post is not None:
                        await squareboard_post.delete()
                        return

    @commands.Cog.listener()
    async def on_message(self, message):
        created_time = message.created_at
        if 'wine' in message.content.lower() and not message.author.bot:
            list_of_wine_strings = fileloader.load_txt(FilePaths.txt_winelines)
            wine_message = random.choice(list_of_wine_strings)
            await message.channel.send(wine_message)
            if message.content.lower() not in (line.lower() for line in list_of_wine_strings) and len(message.mentions) == 0:
                fileloader.add_text_line(message.content, FilePaths.txt_winelines)
        if message.author.id == 448469697034321932 and message.mentions:
            for member in message.mentions:
                if member.id == 448469697034321932:
                    if self.mentioned_time is None:
                        self.mentioned_time = created_time
                    else:
                        d = datetime.timedelta(minutes=10)
                        if created_time - self.mentioned_time < d:
                            await message.channel.send("Leave my master alone. You haz lost a !thx. JK no you didn't but stop plz")
                        self.mentioned_time = created_time
                else:
                    continue
        return


    @commands.Cog.listener()
    async def on_member_join(self, member):
        await member.create_dm()
        await member.dm_channel.send(f'Hi {member.name}, welcome to HECKINCHONKERS! If you wish to be notified of '
                                     f'trader deliveries, moonshine deliveries, naturalist legendary animal missions, etc,'
                                     f'head over to the Heckin-Roles channel and react with the corresponding emoji to '
                                     f'pick up the role! There are also other fun roles to choose from! To see a list of '
                                     f'commands that I can do, type !help in any channel or just ask somebody!')
        embed = discord.Embed(colour=discord.Colour.gold(),
                              title=f'{member.display_name} has **JOINED** the server')
        await self.megachonkers_channel.send(embed=embed)
        await self.aheckinadmin_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(colour=discord.Colour.gold(),
                              title=f'{member.display_name} has **LEFT** the server')
        await self.megachonkers_channel.send(embed=embed)
        await self.aheckinadmin_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        old_nick = before.nick
        new_nick = after.nick
        if old_nick != new_nick:
            if old_nick is None and new_nick is None:
                return
            if new_nick is not None:
                await self.stb_channel.send(f'**{before.name}** changed their nickname to **{new_nick}**')
            if old_nick is not None and new_nick is None:
                await self.stb_channel.send(f'**{after.name}** cleared their nickname - **{before.nick}**')
                return

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            if ctx.invoked_with.startswith('d') or ctx.invoked_with.startswith('n') or ctx.invoked_with.startswith('b'):
                await ctx.channel.send(f'That is the old way. Start with the action first, then the role initial. For '
                                       f'example, `!j d @mention` or `!c n`\n..or check out the new help function with'
                                       f' `!help`')

            else:
                await ctx.channel.send(f'Command not found')

        raise error


def setup(bot):
    bot.add_cog(Listeners(bot))