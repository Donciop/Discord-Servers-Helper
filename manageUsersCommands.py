from discord.ext import commands  # main packages
from discord_slash import cog_ext  # for slash commands
from discord_slash.utils.manage_commands import create_option


class ManageUsersCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(  # slash command decorator
        name="unban",  # name that will be displayed in Discord
        description="Check a specific player's Teamfight Tactics rank",  # description of the command
        guild_ids=[218510314835148802],  # list of server (guilds) id's that have access to this slash command
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
              option_type=4,  # (4 - INTEGER)
              required=True
            )
        ]
    )
    async def unban(self, ctx, nickname, discriminator):
        """
        Command used to un-ban members that are banned on server (guild)

        :param ctx: passing context of the command
        :param nickname: Discord's nickname
        :param discriminator: Discord's discriminator (for ex. #1234)
        """
        if not ctx.author.guild_permissions.manage_messages:  # check if author of the command has right permissions
            await ctx.send("You don't have permission to unban members")
            return  # return if author's missing permission
        banned_users = await ctx.guild.bans()  # access banned users of that discord server
        for ban_entry in banned_users:  # iterate over every ban entry in discord logs
            user = ban_entry.user
            if (user.name, user.discriminator) == (nickname, discriminator):  # check if banned user matches our member
                await ctx.guild.unban(user)  # un-ban if the member matches the banned user
                await ctx.send(f'**{user}** has been unbanned!')


def setup(client):  # adding cog to our main.py file
    client.add_cog(ManageUsersCommands(client))
