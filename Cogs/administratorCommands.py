import nextcord
from nextcord import Interaction
from nextcord.ext import commands, application_checks
from nextcord.abc import GuildChannel
from Cogs.settingsCommands import SettingsCommands


class AdministratorCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='save_attachments', guild_ids=[218510314835148802],
                            description='Save attachments from channel. Needs ADMIN permissions', force_global=True)
    @application_checks.has_permissions(administrator=True)
    async def save_attachments(self,
                               interaction: nextcord.Interaction,
                               channel: GuildChannel = nextcord.SlashOption(required=False,
                                                                            channel_types=[nextcord.ChannelType.text])):

        """
        Command used to save attachments from all messages from specific channel, needs ADMINISTRATOR permissions to use

            Args:
                interaction: (nextcord.Interaction): Context of the command
                channel (:obj:nextcord.Channel, optional): Discord Channel in which we want to save attachments

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('You don\'t have permission Administrator permissions '
                                                    'to use this command',
                                                    ephemeral=True)
            return

        attachment_saved_amount = attachment_failed_to_save_amount = counter = 0

        if not channel:
            channel = interaction.channel

        await interaction.response.defer()
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
        await interaction.followup.send(f'Saved {attachment_saved_amount} files!\n'
                                        f'Failed to save {attachment_failed_to_save_amount} files')


def setup(client):
    client.add_cog(AdministratorCommands(client))
