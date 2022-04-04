from discord.ext import commands  # main packages
from discord_slash import cog_ext  # for slash commands
from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_option, create_permission
from Cogs.settingsCommands import SettingsCommands


class ManageUsersCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(  # slash command decorator
        name="dc_unban",  # name that will be displayed in Discord
        description="Unban specific member from this discord server",  # description of the command
        guild_ids=[218510314835148802],  # list of server (guilds) id's that have access to this slash command
        permissions={
            218510314835148802: [
                create_permission(545658751689031699, SlashCommandPermissionType.ROLE, True),
                create_permission(748144455730593792, SlashCommandPermissionType.ROLE, False),
                create_permission(826094492309258291, SlashCommandPermissionType.ROLE, False),
                create_permission(541960938165764096, SlashCommandPermissionType.ROLE, False),
                create_permission(541961631954108435, SlashCommandPermissionType.ROLE, False)
            ]
        },
        options=[
            create_option(  # parameters in slash command
                name="nickname",  # name of the variable
                description="Type in player's nickname",  # description of the parameter
                option_type=3,  # option_type refers to type of the variable ( 3 - STRING )
                required=True  # this parameter is required
            ),
            create_option(
                name="discriminator",
                description="Type in player's discriminator",
                option_type=3,
                required=True
            )
        ]
    )
    async def unban(self, ctx, nickname, discriminator):
        """
        Command used to un-ban members that are banned on server (guild)

            Args:
                ctx: Context of the command
                nickname (str): Nickname of the person we want to unban
                discriminator (str): Discord discriminator that is used after every nickname
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        banned_users = await ctx.guild.bans()  # access banned users of that discord server
        not_found = 0
        for ban_entry in banned_users:  # iterate over every ban entry in discord logs
            user = ban_entry.user
            if (user.name, user.discriminator) == (nickname, discriminator):  # check if banned user matches our member
                not_found = 1
                await ctx.guild.unban(user)  # un-ban if the member matches the banned user
                await ctx.send(f'**{user}** has been unbanned!')
        if not_found == 0:  # check if user is user is banned
            await ctx.send(f"Seems like {nickname} #{discriminator} isn't banned on this server")
            return  # return if user's not banned on server


def setup(client):  # adding cog to our main.py file
    client.add_cog(ManageUsersCommands(client))
