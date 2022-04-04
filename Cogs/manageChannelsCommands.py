import discord
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.utils.manage_commands import create_option
from Cogs.settingsCommands import SettingsCommands
from asyncio import sleep
from random import randint


class ManageChannelsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(  # slash command decorator
        name="dc_mute",  # name that will be displayed in Discord
        description="Mute someone",  # description of the command
        guild_ids=[218510314835148802],
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
    @commands.has_permissions(manage_channels=True)
    async def dc_mute(self, ctx, member: discord.Member, reason: str = None):
        """
        Command used to mute someone, with or without specified reason

            Args:
                ctx: Context of the command
                member (discord.Member): Discord Member that we want to mute
                reason (str, optional): Reason why the Member has been muted

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
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
        guild_ids=[218510314835148802],
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
    async def dc_deaf(self, ctx, member: discord.Member, reason: str = None):
        """
        Command used to deafen someone, with or without specified reason

            Args:
                ctx: Context of the command
                member (discord.Member): Discord Member that we want to deafen
                reason (str, optional): Reason why the Member has been deafened

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        await member.edit(deafen=True)
        if reason:
            await ctx.send(f'**{member.mention}** was deafened by **{ctx.author.mention}**\n**Reason**: {reason}')
        else:
            await ctx.send(f"**{member.mention}** was deafened by **{ctx.author.mention}**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def mute_cf(self, ctx, member: discord.Member):
        """
        Command used to gamble with someone, whether You or someone else is getting muted

            Args:
                ctx: Context of the command
                member (discord.Member): Member that we want to gamble with

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        mute_minutes_self = mute_minutes = 0
        number = randint(0, 100)
        if ctx.message.author == member:
            await ctx.send(f'🛑 Mute Coinflip Failed\n'
                           f'You can not coinflip with yourself')
            return
        if number >= 50:
            await member.edit(mute=True)
            await ctx.send(f'✅ Mute Coinflip Successful\n'
                           f'You have rolled {str(number)} and muted {member.mention} for 30 seconds')
            mute_minutes += 1
        else:
            await ctx.author.edit(mute=True)
            await ctx.send(f'🛑 Mute Coinflip Failed\n'
                           f'You have rolled {str(number)} and failed to mute {member.mention},'
                           f' however you got muted for 2 minutes')
            mute_minutes_self += 2
        if mute_minutes_self > 0:
            await sleep(mute_minutes_self * 60)
            await ctx.author.edit(mute=False)
        if mute_minutes > 0:
            await sleep(mute_minutes * 30)
            await member.edit(mute=False)


def setup(client):
    client.add_cog(ManageChannelsCommands(client))
