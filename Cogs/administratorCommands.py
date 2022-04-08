import nextcord
from nextcord import Interaction
from nextcord.ext import commands
from nextcord.abc import GuildChannel
from Cogs.settingsCommands import SettingsCommands


class AdministratorCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='msg_leaderboard', guild_ids=[218510314835148802], force_global=True,
                            default_permission=False)
    async def msg_leaderboard(self,
                              interaction: Interaction,
                              channel: GuildChannel = nextcord.SlashOption(required=True,
                                                                           channel_types=[nextcord.ChannelType.text])):

        """
        Command used to check who send the highest amount of messages in specific channel

            Args:
                interaction (nextcord.Interaction): ????
                channel (nextcord.TextChannel): Discord Text Channel in which we want to count messages

            Returns:
                None
        """
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(f'You don\' have Administrator permissions to use this command')
            return

        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        await interaction.response.defer()
        leaderboard_not_sorted = {}
        async for msg in channel.history(limit=None):
            if str(msg.author.display_name) in leaderboard_not_sorted:
                leaderboard_not_sorted[str(msg.author.display_name)] += 1
            else:
                leaderboard_not_sorted[str(msg.author.display_name)] = 1
        leaderboard_sorted = sorted(leaderboard_not_sorted.items(), key=lambda x: x[1], reverse=True)
        iterator = 1
        file = nextcord.File(  # creating file to send image along the embed message
            "Media/trophy.png",  # file path to image
            filename="image.png"  # name of the file
        )
        embed = nextcord.Embed(
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
        await interaction.followup.send(file=file, embed=embed)

    @nextcord.slash_command(name='save_attachments', guild_ids=[218510314835148802], force_global=True)
    async def save_attachments(self,
                               interaction: nextcord.Interaction,
                               channel: GuildChannel = nextcord.SlashOption(required=False,
                                                                            channel_types=[nextcord.ChannelType.text])):
        """
        Command used to save attachments from all messages from specific channel

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
