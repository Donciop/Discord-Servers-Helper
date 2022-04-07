import nextcord
from nextcord.ext import commands
from nextcord.abc import GuildChannel
from Cogs.settingsCommands import SettingsCommands
# from asyncio import sleep
# from random import randint


class ManageChannelsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='add_guild_channel', guild_ids=[218510314835148802], force_global=True)
    async def add_guild_channel(self, interaction: nextcord.Interaction,
                                channel: GuildChannel = nextcord.SlashOption(required=True,
                                                                             channel_types=[
                                                                                 nextcord.ChannelType.text])):
        """
        Command used to add channels that the Bot can be used in

            Args:
                interaction (nextcord.Interaction): Context of the command
                channel (nextcord.GuildChannel): Channel that we want to add to the database

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message('You don\'t have permission to Manage Channels to use this command',
                                                    ephemeral=True)
            return

        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'guild_bot_channels')
        if collection is None:
            return

        check = collection.find_one({'_id': interaction.guild.id})
        if not check:
            collection.insert_one({'_id': interaction.guild.id, 'bot_channels': [channel.id]})
            await interaction.response.send_message(f'Added {channel.mention} to the database', ephemeral=True)
            return

        for guild_channel in check['bot_channels']:
            if channel.id == guild_channel:
                await interaction.response.send_message(f'{channel.mention} already in the database', ephemeral=True)
                return

        collection.update_one({'_id': interaction.guild.id},
                              {'$push': {'bot_channels': channel.id}})
        await interaction.response.send_message(f'{channel.mention} successfully added to the database!',
                                                ephemeral=True)

    @nextcord.slash_command(name='remove_guild_channel', guild_ids=[218510314835148802], force_global=True)
    async def remove_guild_channel(self, interaction: nextcord.Interaction,
                                   channel: GuildChannel = nextcord.SlashOption(required=True,
                                                                                channel_types=[
                                                                                    nextcord.ChannelType.text])):
        """
        Command used to add channels that the Bot can be used in

            Args:
                interaction (nextcord.Interaction): Context of the command
                channel (nextcord.GuildChannel): Channel that we want to add to the database

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message('You don\'t have permission to Manage Channels to use this command',
                                                    ephemeral=True)
            return

        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'guild_bot_channels')
        if collection is None:
            return

        check = collection.find_one({'_id': interaction.guild.id})
        if not check:
            await interaction.response.send_message(f'There isn\'t any channel in the database\n'
                                                    f'Use `/add_guild_channel` to add one!', ephemeral=True)
            return

        if channel.id not in check['bot_channels']:
            await interaction.response.send_message(f'{channel.mention} isn\'t set as a bot channel', ephemeral=True)
            return

        collection.update_one({'_id': interaction.guild.id},
                              {'$pull': {'bot_channels': channel.id}})
        await interaction.response.send_message(f'Removed {channel.mention} from the database', ephemeral=True)

    @nextcord.slash_command(name='dc_mute', guild_ids=[218510314835148802], force_global=True)
    async def dc_mute(self, interaction: nextcord.Interaction,
                      member: nextcord.Member = nextcord.SlashOption(required=True),
                      reason: str = nextcord.SlashOption(required=False)):
        """
        Command used to mute someone, with or without specified reason

            Args:
                interaction: (nextcord.Interaction): Context of the command
                member (nextcord.Member): Discord Member that we want to mute
                reason (str, optional): Reason why the Member has been muted

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message('You don\'t have permission to Manage Channels to use this command',
                                                    ephemeral=True)
            return

        await member.edit(mute=True)
        if reason:
            await interaction.response.send_message(f"**{member.mention}** was muted by "
                                                    f"**{interaction.user.mention}**\n**Reason**: {reason}")
        else:
            await interaction.response.send_message(f"**{member.mention}** was muted by "
                                                    f"**{interaction.user.mention}**")

    @nextcord.slash_command(name='dc_deaf', guild_ids=[218510314835148802], force_global=True)
    async def dc_deaf(self, interaction: nextcord.Interaction,
                      member: nextcord.Member = nextcord.SlashOption(required=True),
                      reason: str = nextcord.SlashOption(required=False)):
        """
        Command used to deafen someone, with or without specified reason

            Args:
                interaction: (nextcord.Interaction): Context of the command
                member (nextcord.Member): Discord Member that we want to deafen
                reason (str, optional): Reason why the Member has been deafened

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message('You don\'t have permission to Manage Channels to use this command',
                                                    ephemeral=True)
            return

        await member.edit(deafen=True)
        if reason:
            await interaction.response.send_message(f'**{member.mention}** '
                                                    f'was deafened by **{interaction.user.mention}**\n'
                                                    f'**Reason**: {reason}')
        else:
            await interaction.response.send_message(f"**{member.mention}** "
                                                    f"was deafened by **{interaction.user.mention}**")

    # @nextcord.slash_command(name='mute_cf', guild_ids=[218510314835148802], force_global=True)
    # @commands.has_permissions(administrator=True)
    # @commands.cooldown(1, 181, commands.BucketType.user)
    # async def mute_cf(self, interaction: nextcord.Interaction,
    #                   member: nextcord.Member = nextcord.SlashOption(required=True)):
    #     """
    #     Command used to gamble with someone, whether You or someone else is getting muted
    #
    #         Args:
    #             interaction: (nextcord.Interaction): Context of the command
    #             member (nextcord.Member): Member that we want to gamble with
    #
    #         Returns:
    #             None
    #     """
    #     channel_check = await SettingsCommands.channel_check(interaction)
    #     if not channel_check:
    #         return
    #     mute_minutes_self = mute_minutes = 0
    #     number = randint(0, 100)
    #     if interaction.message.author == member:
    #         await interaction.response.send_message(f'🛑 Mute Coinflip Failed\n'
    #                                                 f'You can not coinflip with yourself')
    #         return
    #     if number >= 50:
    #         await member.edit(mute=True)
    #         await interaction.response.send_message(f'✅ Mute Coinflip Successful\n'
    #                                                 f'You have rolled {str(number)} and '
    #                                                 f'muted {member.mention} for 30 seconds')
    #         mute_minutes += 1
    #     else:
    #         await interaction.user.edit(mute=True)
    #         await interaction.response.send_message(f'🛑 Mute Coinflip Failed\n'
    #                                                 f'You have rolled {str(number)} and '
    #                                                 f'failed to mute {member.mention}, '
    #                                                 f'however you got muted for 2 minutes')
    #         mute_minutes_self += 2
    #     if mute_minutes_self > 0:
    #         await sleep(mute_minutes_self * 60)
    #         await interaction.user.edit(mute=False)
    #     if mute_minutes > 0:
    #         await sleep(mute_minutes * 30)
    #         await member.edit(mute=False)


def setup(client):
    client.add_cog(ManageChannelsCommands(client))
