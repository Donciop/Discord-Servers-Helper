import nextcord
from nextcord.ext import commands, application_checks  # main packages
from Cogs.settingsCommands import SettingsCommands


class BanMembersCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='dc_unban', guild_ids=[218510314835148802],
                            description='Unban user. Needs BAN MEMBERS permission')
    @application_checks.has_permissions(ban_members=True)
    async def dc_unban(self,
                       interaction: nextcord.Interaction,
                       nickname: str = nextcord.SlashOption(required=True),
                       discriminator: str = nextcord.SlashOption(required=True)):
        """
        Command used to un-ban members that are banned on server (guild). Needs BAN MEMBERS permission to use.

            Args:
                interaction: (nextcord.Interaction): Context of the command
                nickname (str): Nickname of the person we want to unban
                discriminator (str): Discord discriminator that is used after every nickname

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message('You don\'t have permissions to Ban Members to use this command')
            return

        banned_users = await interaction.guild.bans()  # access banned users of that discord server
        found = False
        for ban_entry in banned_users:  # iterate over every ban entry in discord logs
            user = ban_entry.user
            if (user.name, user.discriminator) == (nickname, discriminator):  # check if banned user matches our member
                found = True
                await interaction.guild.unban(user)  # un-ban if the member matches the banned user
                await interaction.send(f'**{user}** has been unbanned!')

        if not found:  # check if user is user is banned
            await interaction.send(f"Seems like {nickname} #{discriminator} isn't banned on this server")
            return  # return if user's not banned on server


def setup(client):  # adding cog to our main.py file
    client.add_cog(BanMembersCommands(client))
