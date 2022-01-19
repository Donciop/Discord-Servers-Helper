import discord
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option, create_permission
from main import client


class ManageMessagesCommands(commands.Cog):
    def __init__(self, client):
      self.client = client

    @cog_ext.cog_slash(  # slash command decorator
        name="msg_count_channel",  # name that will be displayed in Discord
        description="Count messages in specific discord's channel",  # description of the command
        permissions={
            218510314835148802: [
                create_permission(545658751689031699, SlashCommandPermissionType.ROLE, True),
                create_permission(748144455730593792, SlashCommandPermissionType.ROLE, True),
                create_permission(826094492309258291, SlashCommandPermissionType.ROLE, True),
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
            )
        ]
    )
    async def msg_count_channel(self, ctx, channel):
        """
        Command used to count all messages in specific channel

        :param ctx: passing context of the command
        :param channel: discord's channel
        """
        await ctx.defer()
        count = 0
        async for msg in channel.history(limit=None):  # iterate over every message in channel's history
            count += 1  # increment count for every message
        await ctx.send(f"There were {count} messages in {channel.mention}")  # display amount of messages in channel

    @commands.command()  # decorator for discord.py commands
    @commands.has_permissions(manage_messages=True)  # check if user has permission to use that command
    @commands.cooldown(1, 1, commands.BucketType.user)  # assign cooldown for this command
    async def clear(self, ctx, amount: int = 0):
        """
        Command used to delete specific amount of messages from discord's channel

        :param ctx: passing context of the command
        :param amount: amount of messages to delete
        """
        if not amount:  # check if user specified number of messages
            await ctx.send("Specify amount of messages to clear")
            return  # return if amount of messages wasn't specified
        elif amount > 20 or amount <= 0:  # check if number of messages is correct
            await ctx.send("Wrong amount of messages! (min: 1, max: 20)")
            return  # return if wrong number of messages was specified
        else:
            await ctx.channel.purge(limit=amount+1)  # delete that amount of messages along with message with this command

    @clear.error  # decorator for handling errors from 'clear' command
    async def clear_error(self, ctx, error):
        """
        Error handling for 'clear' command

        :param ctx: passing context of the command
        :param error: discord.py error that occured when executing command
        """
        if isinstance(error, commands.BadArgument):  # check if error's type is 'Bad Argument'
            embed = discord.Embed(color=0xeb1414)  # style embed message
            embed.add_field(name="🛑 Clear Error", value="Wrong number of messages", inline=False)
            await ctx.send(embed=embed)  # send specific return message


def setup(client):  # adding cog to our main.py file
    client.add_cog(ManageMessagesCommands(client))
