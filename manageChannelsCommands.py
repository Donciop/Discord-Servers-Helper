import discord
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option, create_permission
import typing
import asyncio
import random


class ManageChannelsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(  # slash command decorator
        name="dc_mute",  # name that will be displayed in Discord
        description="Mute someone",  # description of the command
        permissions={
            218510314835148802: [
                create_permission(545658751689031699, SlashCommandPermissionType.ROLE, True),
                create_permission(748144455730593792, SlashCommandPermissionType.ROLE, True),
                create_permission(826094492309258291, SlashCommandPermissionType.ROLE, False),
                create_permission(541960938165764096, SlashCommandPermissionType.ROLE, False),
                create_permission(541961631954108435, SlashCommandPermissionType.ROLE, False)
            ]
        },
        guild_ids=[218510314835148802],  # list of server (guilds) id's that have access to this slash command
        options=[
            create_option(  # parameters in slash command
                name="member",  # name of the variable
                description="Choose who to mute",  # description of the parameter
                option_type=6,  # option_type refers to type of the variable ( 3 - STRING )
                required=True  # this parameter is required
            ),
            create_option(
                name="reason",
                description="Reason why to mute someone",
                option_type=3,
                required=False
            )
        ]
    )
    async def dc_mute(self, ctx, member, reason=None):
        channel_check_cog = self.client.get_cog("SettingsCommands")
        channel_check = False
        if channel_check_cog is not None:
            channel_check = await channel_check_cog.channel_check(ctx, ctx.channel.id)
        if not channel_check:
            return
        await member.edit(mute=True)
        if reason:
            await ctx.send(f"**{member.mention}** was muted by **{ctx.author.mention}**\n**Reason**: {reason}")
        else:
            await ctx.send(f"**{member.mention}** was muted by **{ctx.author.mention}**")

    @cog_ext.cog_slash(  # slash command decorator
        name="dc_deaf",  # name that will be displayed in Discord
        description="Deafen someone",  # description of the command
        permissions={
            218510314835148802: [
                create_permission(545658751689031699, SlashCommandPermissionType.ROLE, True),
                create_permission(748144455730593792, SlashCommandPermissionType.ROLE, True),
                create_permission(826094492309258291, SlashCommandPermissionType.ROLE, False),
                create_permission(541960938165764096, SlashCommandPermissionType.ROLE, False),
                create_permission(541961631954108435, SlashCommandPermissionType.ROLE, False)
            ]
        },
        guild_ids=[218510314835148802],  # list of server (guilds) id's that have access to this slash command
        options=[
            create_option(  # parameters in slash command
                name="member",  # name of the variable
                description="Choose who to deafen",  # description of the parameter
                option_type=6,  # option_type refers to type of the variable ( 3 - STRING )
                required=True  # this parameter is required
            ),
            create_option(
                name="reason",
                description="Reason why to deafen someone",
                option_type=3,
                required=False
            )
        ]
    )
    async def dc_deaf(self, ctx, member, reason=None):
        channel_check_cog = self.client.get_cog("SettingsCommands")
        channel_check = False
        if channel_check_cog is not None:
            channel_check = await channel_check_cog.channel_check(ctx, ctx.channel.id)
        if not channel_check:
            return
        await member.edit(deafen=True)
        if reason:
            await ctx.send(f"""
            **{member.mention}** was deafened by **{ctx.author.mention}**\n**Reason**: {reason}
            """)
        else:
            await ctx.send(f"**{member.mention}** was deafened by **{ctx.author.mention}**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def mute_cf(self, ctx, member: typing.Optional[discord.Member]):
        channel_check_cog = self.client.get_cog("SettingsCommands")
        channel_check = False
        if channel_check_cog is not None:
            channel_check = await channel_check_cog.channel_check(ctx, ctx.channel.id)
        if not channel_check:
            return
        mute_minutes_self = mute_minutes = 0
        number = random.randint(0, 100)
        if not member:
            await ctx.send("""
            🛑 Mute Coinflip Failed\n
You have to specify a Discord member to mute
            """)
            return
        if ctx.message.author == member:
            await ctx.send("""
            🛑 Mute Coinflip Failed
You can't coinflip with yourself
            """)
            return
        if number >= 50:
            await member.edit(mute=True)
            await ctx.send(f"""
            ✅ Mute Coinflip Successful\n
You've rolled {str(number)} and muted {member.mention} for 1 minute
            """)
            mute_minutes += 1
        else:
            await ctx.author.edit(mute=True)
            await ctx.send(f"""
            🛑 Mute Coinflip Failed\n
You've rolled {str(number)} and failed to mute {member.mention}, however you got muted for 3 minutes
            """)
            mute_minutes_self += 3
        if mute_minutes_self > 0:
            await asyncio.sleep(mute_minutes_self * 60)
            await ctx.author.edit(mute=False)
        if mute_minutes > 0:
            await asyncio.sleep(mute_minutes * 60)
            await member.edit(mute=False)


def setup(client):
    client.add_cog(ManageChannelsCommands(client))
