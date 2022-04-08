import nextcord
from nextcord.ext import commands, application_checks
from nextcord.abc import GuildChannel
from Cogs.settingsCommands import SettingsCommands


class ManageMessagesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='dc_count_messages', guild_ids=[218510314835148802], force_global=True)
    @application_checks.has_permissions(manage_messages=True)
    async def dc_count_messages(self,
                                interaction: nextcord.Interaction,
                                channel: GuildChannel = nextcord.SlashOption(required=True,
                                                                             channel_types=[nextcord.ChannelType.text]),
                                member: nextcord.Member = nextcord.SlashOption(required=False)):
        """
        Command that is used to count all messages in specific channel

            Args:
                interaction: (nextcord.Interaction): Context of the command
                channel (nextcord.GuildChannel): Discord Channel in which we want to count messages
                member (:obj:nextcord.Member, optional): Discord Member from whom we want to count messages

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message('You don\'t have permission to Manage Channels to use this command',
                                                    ephemeral=True)
            return

        await interaction.response.defer()
        count = 0
        if member:
            async for msg in channel.history(limit=None):  # iterate over every message in channel's history
                if msg.author == member:
                    count += 1  # increment count for every message
            # display amount of messages in channel
            await interaction.followup.send(f"There were {count} messages in {channel.mention} from {member.mention}")
        else:
            async for _ in channel.history(limit=None):
                count += 1
            await interaction.followup.send(f"There were {count} messages in {channel.mention}")

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
