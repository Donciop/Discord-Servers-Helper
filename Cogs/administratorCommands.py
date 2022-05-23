import nextcord
from nextcord import Interaction
from nextcord.ext import commands, application_checks
from nextcord.abc import GuildChannel
from Cogs.settingsCommands import SettingsCommands
import random


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

    @nextcord.slash_command(name='metinize', guild_ids=[218510314835148802],
                            description='Metinize the server. Needs ADMIN permissions', force_global=True)
    @application_checks.has_permissions(administrator=True)
    async def change_nicknames(self, interaction: nextcord.Interaction):
        await interaction.response.defer()
        mobs_dict = await SettingsCommands.load_json_dict('JsonData/mobs_dict.json')
        npc_dict = await SettingsCommands.load_json_dict('JsonData/npc_dict.json')
        for member in interaction.guild.members:
            if member.display_name not in mobs_dict and member.display_name not in npc_dict and not member.bot:
                chosen_dict = random.choice([mobs_dict, npc_dict])
                chosen_nickname = random.choice(list(chosen_dict.keys()))
                chosen_dict.pop(chosen_nickname)
                print(chosen_nickname)
                print(f'Changed nickname for {member.display_name}')
                await member.edit(nick=chosen_nickname)
                print(f'New nickname: {member.display_name}')


def setup(client):
    client.add_cog(AdministratorCommands(client))
