import discord
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.utils.manage_commands import create_option
from Cogs.settingsCommands import SettingsCommands
import cProfile
import pstats


class AdministratorCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(  # slash command decorator
        name="msg_leaderboard",  # name that will be displayed in Discord
        description="Show the channel's leaderboard",  # description of the command
        guild_ids=[218510314835148802],
        options=[
            create_option(  # parameters in slash command
                name="channel",  # name of the variable
                description="Select channel",  # description of the parameter
                option_type=7,  # option_type refers to type of the variable ( 7 - CHANNEL )
                required=True  # this parameter is required
            )
        ]
      )
    @commands.has_permissions(administrator=True)
    async def top(self, ctx, channel):
        """
        Command used to check who send the highest amount of messages in specific channel

            Args:
                ctx: Context of the command
                channel (discord.TextChannel): Discord Text Channel in which we want to count messages

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        await ctx.defer()
        leaderboard_not_sorted = {}
        async for msg in channel.history(limit=None):
            if str(msg.author.display_name) in leaderboard_not_sorted:
                leaderboard_not_sorted[str(msg.author.display_name)] += 1
            else:
                leaderboard_not_sorted[str(msg.author.display_name)] = 1
        leaderboard_sorted = sorted(leaderboard_not_sorted.items(), key=lambda x: x[1], reverse=True)
        iterator = 1
        file = discord.File(  # creating file to send image along the embed message
            "Media/trophy.png",  # file path to image
            filename="image.png"  # name of the file
        )
        embed = discord.Embed(
          color=0x11f80d,
          description=f'Leaderboard of the most active users in {channel.mention}',
          title="🏆 Leaderboard 🏆"
        )
        embed.set_thumbnail(url="attachment://image.png")
        for k, v in leaderboard_sorted:
            if iterator <= 10 and v > 0:
                if iterator == 1:
                    embed.add_field(
                        name=f"🥇 {iterator}. {k}",
                        value=f"{v} messages",
                        inline=False
                    )
                elif iterator == 2:
                    embed.add_field(
                        name=f"🥈 {iterator}. {k}",
                        value=f"{v} messages",
                        inline=False
                    )
                elif iterator == 3:
                    embed.add_field(
                        name=f"🥉 {iterator}. {k}",
                        value=f"{v} messages",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=f"{iterator}. {k}",
                        value=f"{v} messages",
                        inline=False
                    )
            iterator += 1
        await ctx.send(file=file, embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def upload_members_to_database(self, ctx):
        """
        Utility method used to import server members into database

            Args:
                ctx: Context of the command

            Returns:
                None
        """
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'new_members')
        for member in ctx.guild.members:
            if member.bot:
                continue
            check = collection.find_one({'_id': member.id})
            if not check:
                collection.insert_one({'_id': member.id, 'messages_sent': 0})
            else:
                collection.update_one({'_id': member.id},
                                      {'$set': {'messages_sent': 0}})


def setup(client):
    client.add_cog(AdministratorCommands(client))
