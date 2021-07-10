import discord
from discord.ext import commands
from config.all_global_variables import *

class ModeratorCommands(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

        # Get Discord Guild
        self.guild = self.bot.get_guild(DiscordGuilds.heckinchonkers_id)

        # Get Discord MEGACHONKERS channel
        self.megachonkers_channel_id = DiscordChannels.megachonkers_channel_id
        self.megachonkers_channel = self.guild.get_channel(self.megachonkers_channel_id)

        # Get Discord AHeckinAdmin channel
        self.aheckinadmin_channel_id = DiscordChannels.aheckinadmin_channel_id
        self.aheckinadmin_channel = self.guild.get_channel(self.aheckinadmin_channel_id)

    # Roles for checks
    megachonkers = DiscordRoles.megachonkers_role_id
    admin = DiscordRoles.heckinadmin_role_id
    heftychonks = DiscordRoles.heftychonks_role_id

    def embed_log_report(self, incident, author, member, reason):
        embed = discord.Embed(author=f"{incident} REPORT")
        if incident == 'BAN':
            embed.colour = discord.Colour.dark_red()
            embed.title = f"{author} BANNED {member}"
            if reason is not None:
                embed.add_field(name="Reason: ", value=f"{reason}")
            else:
                embed.add_field(name="Reason: ", value="No reason given")
            return embed
        elif incident == 'KICK':
            embed.colour = discord.Colour.red()
            embed.title = f"{author} KICKED {member}"
            if reason is not None:
                embed.add_field(name="Reason: ", value=f"{reason}")
            else:
                embed.add_field(name="Reason: ", value="No reason given")
            return embed
        elif incident == 'MUTE':
            embed.colour = discord.Colour.orange()
            embed.title = f"{author} MUTED {member}"
            if reason is not None:
                embed.add_field(name="Reason: ", value=f"{reason}")
            else:
                embed.add_field(name="Reason: ", value="No reason given")
            return embed
        elif incident == 'WARN':
            embed.colour = discord.Colour.dark_blue()
            embed.title = f"{author} WARNED {member}"
            if reason is not None:
                embed.add_field(name="Reason: ", value=f"{reason}")
            else:
                embed.add_field(name="Reason: ", value="No reason given")
            return embed
        elif "FAILED" in incident:
            if "MUTE" in incident:
                embed.colour = discord.Colour.dark_grey()
                embed.title = f"{author} ATTEMPTED TO MUTE {member}"
                embed.add_field(name="Failure Reason: ", value=f"{author} has equal or lower role")
                return embed
            if "BAN" in incident:
                embed.colour = discord.Colour.dark_grey()
                embed.title = f"{author} ATTEMPTED TO BAN {member}"
                embed.add_field(name="Failure Reason: ", value=f"{author} has equal or lower role")
                return embed
            if "KICK" in incident:
                embed.colour = discord.Colour.dark_grey()
                embed.title = f"{author} ATTEMPTED TO KICK {member}"
                embed.add_field(name="Failure Reason: ", value=f"{author} has equal or lower role")
                return embed
        else:
            embed.colour = discord.Colour.green()
            if incident == 'UNBAN':
                embed.title = f"{author} UNBANNED {member}"
                if reason is not None:
                    embed.add_field(name="Reason: ", value=f"{reason}")
                else:
                    embed.add_field(name="Reason: ", value="No reason given")
                return embed
            if incident == 'UNMUTE':
                embed.title = f"{author} UNMUTED {member}"
                if reason is not None:
                    embed.add_field(name="Reason: ", value=f"{reason}")
                else:
                    embed.add_field(name="Reason: ", value="No reason given")
                return embed


    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @commands.has_any_role(megachonkers, admin)
    async def ban_member(self, ctx, member: discord.Member, *, reason=None):
        banisher_top_role = ctx.author.top_role
        banishee_top_role = member.top_role

        if banishee_top_role >= banisher_top_role:
            incident = "FAILED BAN"
            if banishee_top_role.name == 'AHeckinAdmin':
                await ctx.channel.send(f"Yeah, no.")
                await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                await self.megachonkers_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                return

            if banisher_top_role == banishee_top_role:
                await ctx.channel.send(f'You cannot ban a fellow MEGACHONKER. Shame on you!')
                await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                await self.megachonkers_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                return

        # Send message to user about ban
        ban_message = f'You were banned by {ctx.author.display_name}'
        if reason is None:
            ban_message += f' with no reason given.\n\n'
        else:
            ban_message += f' because: {reason}\n\n'
        ban_message += f'If you have any objections, you may reach out to AHeckinMeow and attempt to appeal your ban.'
        await member.send(ban_message)
        await member.ban(reason=reason)

        # Send ban incident to aheckinadmin and megachonker channels
        incident = "BAN"
        await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
        await self.megachonkers_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    @commands.has_any_role(megachonkers, admin)
    async def unban_member(self, ctx, *, member, reason=None):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await user.send(f'Your ban from HECKINCHONKERS has been appealed. In the case that you are banned again, '
                          f'you will not be able to appeal it.')
                await ctx.guild.unban(user)

                incident = "UNBAN"
                await self.aheckinadmin_channel.send(embed=
                    self.embed_log_report(incident, ctx.author.name, member.name, reason))
                await self.megachonkers_channel.send(embed=
                    self.embed_log_report(incident, ctx.author.name, member.name, reason))




    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @commands.has_any_role(megachonkers, admin)
    async def kick_member(self, ctx, member: discord.Member, *, reason=None):
        kicker_top_role = ctx.author.top_role
        kickee_top_role = member.top_role
        if kickee_top_role >= kicker_top_role:
            incident = 'FAILED KICK'
            if kickee_top_role.name == 'AHeckinAdmin':
                await ctx.channel.send(f"Yeah, no.")
                await self.aheckinadmin_channel.send(embed=
                    self.embed_log_report(incident, ctx.author.name, member.name, reason))
                await self.megachonkers_channel.send(embed=
                    self.embed_log_report(incident, ctx.author.name, member.name, reason))
                return

            if kicker_top_role == kickee_top_role:
                await ctx.channel.send(f'You cannot kick a fellow MEGACHONKER. Shame on you!')
                await self.aheckinadmin_channel.send(embed=
                    self.embed_log_report(incident, ctx.author.name, member.name, reason))
                await self.megachonkers_channel.send(embed=
                    self.embed_log_report(incident, ctx.author.name, member.name, reason))
                return

        # Send kick message to user
        kick_message = f'You were kicked by {ctx.author.display_name}'
        if reason is None:
            kick_message += f' with no reason given.\n\n'
        else:
            kick_message += f' because: {reason}\n\n'
        kick_message += f'If you have any objections, you may reach out to AHeckinMeow and '\
                        f'present your case for an invite back to HECKINCHONKERS.'
        await member.send(kick_message)
        await member.kick(reason=reason)

        # Send kick report to aheckinadmin and megachonkers
        incident = "KICK"
        await self.aheckinadmin_channel.send(embed=
            self.embed_log_report(incident, ctx.author.name, member.name, reason))
        await self.megachonkers_channel.send(embed=
            self.embed_log_report(incident, ctx.author.name, member.name, reason))

    @commands.command(name='mute')
    @commands.has_any_role(megachonkers,admin, heftychonks)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        muter_top_role = ctx.author.top_role
        mutee_top_role = member.top_role
        if mutee_top_role >= muter_top_role:
            incident = "FAILED MUTE"
            if mutee_top_role.name == 'AHeckinAdmin':
                await ctx.channel.send(f"Yeah, no.")
                await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                await self.megachonkers_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                return
            if mutee_top_role.name == 'ChonkerBot':
                await ctx.channel.send(f"Now why would you want to do that?")
                await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                return
            if mutee_top_role.name == 'MEGACHONKERS':
                await ctx.channel.send(f"You cannot mute other MEGACHONKERS")
                await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                await self.megachonkers_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                return
            if muter_top_role.name == mutee_top_role:
                await ctx.channel.send(f'You cannot mute somebody in your own rank')
                await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                await self.megachonkers_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                return

        # Mute the member
        role = discord.utils.get(ctx.guild.roles, name='TheDogHouse')
        await member.add_roles(role)

        # Send mute report to aheckinadmin and megachonkers channels
        incident = "MUTE"
        await ctx.channel.send(f'{ctx.author.display_name} muted {member.display_name}')
        await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
        await self.megachonkers_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))

    @commands.command(name='unmute')
    @commands.has_any_role(megachonkers, admin, heftychonks)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        guild = ctx.guild
        for role in guild.roles:
            if role.name == 'TheDogHouse':
                await ctx.channel.send(f'{member.display_name} has been unmuted')
                await member.remove_roles(role)
                incident = 'UNMUTE'
                await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                await self.megachonkers_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
                return

    @commands.command(name='warn')
    @commands.has_any_role(megachonkers, admin, heftychonks)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        await ctx.channel.send(f"Hey {member.display_name}. Whatever you're doing needs to stop. If it continues, you may be"
                               f" muted indefinitely until you're unmuted by another HeftyChonk or MEGACHONKER\n\n"
                               f"If the behavior breaks any server rules, further disciplinary action may be taken."
                               f"\n\n-With Love\nChonkerBot.")

        incident = "WARN"
        await self.aheckinadmin_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))
        await self.megachonkers_channel.send(embed=self.embed_log_report(incident, ctx.author.name, member.name, reason))






def setup(bot):
    bot.add_cog(ModeratorCommands(bot))