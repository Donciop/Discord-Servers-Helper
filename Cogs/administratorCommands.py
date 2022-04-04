import discord
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.utils.manage_commands import create_option
from Cogs.settingsCommands import SettingsCommands


class AdministratorCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(  # slash command decorator
        name="msg_leaderboard",  # name that will be displayed in Discord
        description="Show the channel's leaderboard",  # description of the command
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
        for member in channel.members:
            counter = 0
            async for msg in channel.history(limit=None):
                if msg.author == member:
                    counter += 1
            leaderboard_not_sorted[f"{str(member.display_name)}#{str(member.discriminator)}"] = counter
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


def setup(client):
    client.add_cog(AdministratorCommands(client))
