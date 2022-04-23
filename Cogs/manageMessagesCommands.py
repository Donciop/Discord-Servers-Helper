import nextcord
from nextcord.ext import commands, application_checks


class ManageMessagesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='clear', guild_ids=[218510314835148802], force_global=True)
    @application_checks.has_permissions(manage_channels=True)
    async def clear(self,
                    interaction: nextcord.Interaction,
                    amount: int = nextcord.SlashOption(required=True)):
        """
        Command used to delete specific amount of messages from Discord Channel

            Args:
                interaction: (nextcord.Interaction): Context of the command
                amount (int): Amount of messages that will be deleted

            Returns:
                None
        """
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message('You don\'t have Manage Messages permission to use that command',
                                                    ephemeral=True)
            return

        if amount > 20 or amount < 0:  # check if number of messages is correct
            await interaction.response.send_message("Wrong amount of messages! (min: 1, max: 20)", ephemeral=True)
            return

        # delete that amount of messages
        await interaction.channel.purge(limit=amount)


def setup(client):  # adding cog to our main.py file
    client.add_cog(ManageMessagesCommands(client))
