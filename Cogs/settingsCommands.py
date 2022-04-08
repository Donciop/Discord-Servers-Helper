import nextcord
from nextcord import Interaction
from nextcord.ext import commands, application_checks
from nextcord.abc import GuildChannel
import requests.exceptions
from typing import Union
from pymongo import MongoClient
from os import getenv, makedirs, path
from json import loads
import logging
from riotwatcher import TftWatcher, LolWatcher

logging.basicConfig(level=logging.INFO)


class SettingsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def load_json_dict(filepath: str):
        """
        Utility method that is used to load .json files as Python dictionaries

            Args:
                filepath (str): File path to desired .json file

            Returns:
                final_dict (dict): Dictionary contains passed .json file
        """
        with open(filepath) as file:
            temp_dict = file.read()
            final_dict = loads(temp_dict)
        return final_dict

    @staticmethod
    async def db_connection(db: str, collection: str, *, interaction: nextcord.Interaction = None):
        """
        Utility method that is used to connect to the MongoDB Database

            Args:
                db (str): Name of the Database
                collection (str): Name of the Collection in Database
                interaction (:obj:nextcord.Interaction, optional): Context of the command

            Returns:
                collection: Collection from the Database
        """
        mongo_client = MongoClient(getenv('MONGOURL'))
        db = mongo_client[db]
        collection = db[collection]
        if collection is None:
            if interaction:
                await interaction.response.send_message('Cannot connect to the database', ephemeral=True)
                return
        return collection

    @staticmethod
    async def channel_check(interaction: Interaction):
        """
        Utility method that is used to check if user is sending commands in channel that allows it

            Args:
                interaction (nextcord.Interaction): ???

            Returns:
                bool: True if user can send messages in this channel, False otherwise
        """
        channel_check = False
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'guild_bot_channels')
        if collection is None:
            return
        check = collection.find_one({'_id': interaction.guild_id})
        if not check:
            channel_check = True
        else:
            for bot_channel in check['bot_channels']:
                if interaction.channel_id == int(bot_channel):
                    channel_check = True

        # sends specific message if command is used in forbidden channel
        if not channel_check:
            await interaction.response.send_message(f'Please, use bot commands in bot channel to prevent spam',
                                                    ephemeral=True)
        return channel_check

    @staticmethod
    async def create_attachments_dir(*, filepath: str, channel: GuildChannel):
        """
        Utility method used to create specific directory when using *save_attachments command

            Args:
                filepath (str): Filepath to the directory that we want to create our subdirectory
                channel (nextcord.Channel): Discord Text Channel in which we want to save attachments

            Returns:
                None
        """
        exists = path.exists(f'{filepath}\\{channel.name}')
        if not exists:
            makedirs(f'{filepath}\\{channel.name}\\Video')
            makedirs(f'{filepath}\\{channel.name}\\Text')
            makedirs(f'{filepath}\\{channel.name}\\Uncategorized')
            makedirs(f'{filepath}\\{channel.name}\\Images')
            return

    @staticmethod
    async def save_attachment(*, filepath: str, counter: int,
                              channel: GuildChannel, msg: nextcord.Message):
        """
        Utility method used to categorize Attachments sent to channels

            Args:
                filepath (str): Filepath to the directory that we want to save our files in
                counter (int):  Number of attachment that we're trying to save
                channel (nextcord.GuildChannel): Discord Channel in which we're saving attachments
                msg (nextcord.Message): Discord Message that contains our attachment

            Returns:
                bool: True if successful, False otherwise
        """

        filetypes = {'Images': ['jpg', 'jpeg', 'png'],
                     'Video': ['mp4', 'mov', 'webm'],
                     'Text': ['pdf', 'txt']}
        created_time = msg.created_at.strftime("%Y_%m_%d_%H_%M_%S")
        await SettingsCommands.create_attachments_dir(filepath=filepath, channel=channel)
        filetype_found = False
        for i_counter, attachment in enumerate(msg.attachments):
            for category, category_filetypes in filetypes.items():
                for filetype in category_filetypes:
                    if attachment.filename.lower().endswith(filetype):
                        fp = f'{filepath}\\{channel.name}\\{category}\\{counter}' \
                             f'_{i_counter}_{msg.author.name}_{created_time}.{filetype}'
                        exists = path.exists(f'{filepath}\\{channel.name}')
                        if not exists:
                            return False
                        try:
                            await attachment.save(fp=fp)
                            return True
                        except nextcord.HTTPException:
                            return False
            if not filetype_found:
                try:
                    fp = f'{filepath}\\{channel.name}\\Uncategorized\\{counter}' \
                         f'_{i_counter}_{msg.author.name}_{created_time}.{str(attachment.filename)[:-5]}'
                    await attachment.save(fp=fp)
                    return True
                except nextcord.HTTPException:
                    return False

    @staticmethod
    async def get_riot_stats(interaction: nextcord.Interaction, *, stats_type: str, nickname: str, all_stats=False):
        """
        Utility method used to gather information about player's rank

            Args:
                interaction (nextcord.Interaction): Context of the command
                stats_type (str): Whether we gather stats from League of Legends (LOL) or Teamfight Tactics (TFT)
                nickname (str): Player's nickname
                all_stats (bool, optional): if True, gather information about all queue types
                from Teamfight Tactics (TFT)

            Returns:
                summoner (dict): Information about players profile
                summoner_stats (dict): Information about player's rank
        """
        watcher = TftWatcher(getenv('APIKEYTFT'))
        stats_name = 'RANKED_TFT'
        if stats_type.lower() == 'lol':
            watcher = LolWatcher(getenv('APIKEYLOL'))
            stats_name = 'RANKED_SOLO_5x5'
        try:
            summoner = watcher.summoner.by_name('eun1', nickname)
        except requests.exceptions.HTTPError:
            summoner_stats = []
            summoner = ''
            await interaction.response.send_message(f'Can\'t find **{nickname}** on EUNE server', ephemeral=True)
            return summoner, summoner_stats

        summoner_stats = watcher.league.by_summoner('eun1', summoner['id'])
        if not summoner_stats:
            summoner_stats = []
            await interaction.response.send_message(f'Player {nickname} is unranked', ephemeral=True)
            return summoner, summoner_stats

        if all_stats:
            return summoner, summoner_stats
        queue_found = False
        for league_type in summoner_stats:
            if league_type['queueType'] == stats_name:
                return summoner, league_type
            else:
                queue_found = False
        if not queue_found:
            summoner_stats = []
            await interaction.response.send_message(f'Player {nickname} is unranked', ephemeral=True)
            return summoner, summoner_stats

    @staticmethod
    async def riot_rank_check(summoner_rank: dict, *, tier_emoji=True, rank=True):
        """
        Method that checks player's rank and return specific information for further usage

            Args:
                summoner_rank (dict): Dictionary from RiotWatcher containing information about player's ranking
                tier_emoji (bool): if True, method will return specific emoji associated with ranked tier
                rank (bool): if True, method will return local rating

            Returns:
                tier_emoji: custom emoji based on player's ranking
                rank (int): calculated rating for local leaderboard
        """
        rank_dict = await SettingsCommands.load_json_dict("JsonData/rankDict.json")
        rank_list = ['I', 'II', 'III', 'IV']
        local_rank = 0
        local_tier_emoji = None
        if not summoner_rank:
            return local_tier_emoji, local_rank
        for tier in rank_dict:  # iterate over every tier until we find player's tier
            if summoner_rank['tier'] != tier:
                local_rank += 400
            else:
                local_tier_emoji = rank_dict[tier]
                break
        for lol_rank in rank_list:  # iterate over every rank until we find player's rank
            if summoner_rank['rank'] != lol_rank:
                local_rank += 100
            else:
                break
        local_rank += summoner_rank['leaguePoints']  # calculate final rating for leaderboard
        if rank and tier_emoji:
            return local_tier_emoji, local_rank
        elif not tier_emoji:
            return rank
        else:
            return local_tier_emoji

    @staticmethod
    async def upload_members_to_database(guild: nextcord.Guild):
        """
        Utility method used to import server members into database

            Returns:
                None
        """

        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'new_members')
        if collection is None:
            return
        for member in guild.members:
            if member.bot:
                continue
            check = collection.find_one({'_id': member.id})
            if not check:
                collection.insert_one({'_id': member.id, 'messages_sent': 0})
            else:
                collection.update_one({'_id': member.id},
                                      {'$set': {'messages_sent': 0}})

    @staticmethod
    async def format_missing_permissions(error: Union[application_checks.ApplicationMissingPermissions,
                                                      commands.MissingPermissions, commands.BotMissingPermissions]):
        """
        Utility method used to format missing permission strings for a user-friendly response

            Args:
                error (Union[application_checks.ApplicationMissingPermissions,
                             commands.MissingPermissions,
                             commands.BotMissingPermissions]): error caught during execution

            Returns:
                missing_perms (str): string contains all missing perms correctly formatted
        """
        missing_perms = ''
        for perms_error in error.missing_permissions:
            missing_perms += f'{perms_error}, '
        missing_perms = missing_perms.replace('_', ' ')
        if len(missing_perms) == 1:
            missing_perms = missing_perms.replace(',', '')
        return missing_perms


def setup(client):
    client.add_cog(SettingsCommands(client))
