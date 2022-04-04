import discord
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option, create_permission
from Cogs.settingsCommands import SettingsCommands


class ManageMessagesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(  # slash command decorator
        name="dc_count_messages",  # name that will be displayed in Discord
        description="Count messages in specific discord's channel",  # description of the command
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
              name="channel",  # name of the variable
              description="Select channel",  # description of the parameter
              option_type=7,  # option_type refers to type of the variable ( 7 - CHANNEL )
              required=True  # this parameter is required
            ),
            create_option(
                name="member",
                description="Select member",
                option_type=6,
                required=False
            )
        ]
    )
    async def dc_count_messages(self, ctx, channel, member=None):
        """
        Command that is used to count all messages in specific channel

            Args:
                ctx: Context of the command
                channel (discord.Channel): Discord Channel in which we want to count messages
                member (:obj:discord.Member, optional): Discord Member from whom we want to count messages

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        await ctx.defer()
        count = 0
        if member:
            async for msg in channel.history(limit=None):  # iterate over every message in channel's history
                if msg.author == member:
                    count += 1  # increment count for every message
            # display amount of messages in channel
            await ctx.send(f"There were {count} messages in {channel.mention} from {member.mention}")
        else:
            async for msg in channel.history(limit=None):
                count += 1
            await ctx.send(f"There were {count} messages in {channel.mention}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def save_attachments(self, ctx, channel: discord.TextChannel = None):
        """
        Command used to save attachments from all messages from specific channel

            Args:
                ctx: Context of the command
                channel (:obj:discord.Channel, optional): Discord Channel in which we want to save attachments

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        attachment_saved_amount = attachment_failed_to_save_amount = counter = 0
        if not channel:
            channel = ctx.channel
        filepath = 'E:\\Discord Attachments'
        async for msg in channel.history(limit=None):  # iterate over every message in channel's history
            if not msg.attachments:
                continue
            attachment_saved = await SettingsCommands.save_attachment(counter=counter, filepath=filepath,
                                                                      channel=channel, msg=msg)
            if attachment_saved:
                attachment_saved_amount += 1
            else:
                attachment_failed_to_save_amount += 1
            counter += 1
        await ctx.send(f'Saved {attachment_saved_amount} files!\n'
                       f'Failed to save {attachment_failed_to_save_amount} files')

    @commands.command()  # decorator for discord.py commands
    @commands.has_permissions(manage_messages=True)  # check if user has permission to use that command
    @commands.cooldown(1, 1, commands.BucketType.user)  # assign cooldown for this command
    async def clear(self, ctx, amount: int):
        """
        Command used to delete specific amount of messages from Discord Channel

            Args:
                ctx: Context of the command
                amount (int): Amount of messages that will be deleted

            Returns:
                None
        """
        if amount > 20 or amount < 0:  # check if number of messages is correct
            await ctx.send("Wrong amount of messages! (min: 1, max: 20)")
            return  # return if wrong number of messages was specified
        else:
            # delete that amount of messages along with message with this command
            await ctx.channel.purge(limit=amount+1)

    @clear.error  # decorator for handling errors from 'clear' command
    async def clear_error(self, ctx, error):
        """
        Error handling for 'clear' command

            Args:
                ctx: Context of the command
                error (discord.ext.commands.errors): Error that we're trying to catch

            Returns:
                None
        """
        if isinstance(error, commands.BadArgument):  # check if error's type is 'Bad Argument'
            embed = discord.Embed(color=0xeb1414)  # style embed message
            embed.add_field(name='🛑 Clear Error', value='Number of messages must be an decimal number', inline=False)
            await ctx.send(embed=embed)  # send specific return message

        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(color=0xeb1414)
            embed.add_field(name='🛑 Clear Error', value='You need to specify number of messages', inline=False)
            await ctx.send(embed=embed)


def setup(client):  # adding cog to our main.py file
    client.add_cog(ManageMessagesCommands(client))
