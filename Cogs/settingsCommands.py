import nextcord
from nextcord import Interaction
from nextcord.ext import commands, application_checks
from nextcord.abc import GuildChannel
from pymongo import MongoClient
from riotwatcher import TftWatcher, LolWatcher
import requests.exceptions
import requests
import typing
import os
import json


class LolUtilityFunctions(commands.Cog):

    @staticmethod
    async def get_summoner(interaction: nextcord.Interaction, nickname: str):
        """
        Utility method for accessing player's account data from Riot API

            Args:
                interaction (nextcord.Interaction): Context of the command
                nickname (str): Nickname of the plyer

            Returns:
                summoner (dict): Dictionary containing information about specific player
        """
        watcher = LolWatcher(os.getenv('APIKEYLOL'))
        try:
            summoner = watcher.summoner.by_name('eun1', nickname)
            return summoner
        except requests.exceptions.HTTPError:
            await interaction.response.send_message(f'Can\'t find **{nickname}** on EUNE server', ephemeral=True)
            return None

    @staticmethod
    async def get_soloq_ranked_stats(interaction: nextcord.Interaction, summoner):
        """
        Utility method used to gather information about player's rank

            Args:
                interaction (nextcord.Interaction): Context of the command
                from Teamfight Tactics (TFT)
                summoner (summonerDTO): Represents summoner as Python dictionary

            Returns:
                summoner_stats (dict): Information about player's rank
        """
        watcher = LolWatcher(os.getenv('APIKEYLOL'))

        summoner_stats = watcher.league.by_summoner('eun1', summoner['id'])
        if not summoner_stats:
            await interaction.response.send_message(f'Player {summoner["name"]} is unranked', ephemeral=True)
            return None

        queue_found = False
        for league_type in summoner_stats:
            if league_type['queueType'] == 'RANKED_SOLO_5x5':
                return league_type

        if not queue_found:
            await interaction.response.send_message(f'Player {summoner["name"]} is unranked', ephemeral=True)
            return None

    @staticmethod
    async def get_flex_ranked_stats(interaction: nextcord.Interaction, summoner):
        """
        Utility method used to gather information about player's rank

            Args:
                interaction (nextcord.Interaction): Context of the command
                from Teamfight Tactics (TFT)
                summoner (summonerDTO): Represents summoner as Python dictionary

            Returns:
                summoner_stats (dict): Information about player's rank
        """
        watcher = LolWatcher(os.getenv('APIKEYLOL'))

        summoner_stats = watcher.league.by_summoner('eun1', summoner['id'])
        if not summoner_stats:
            await interaction.response.send_message(f'Player {summoner["name"]} is unranked', ephemeral=True)
            return None

        queue_found = False
        for league_type in summoner_stats:
            if league_type['queueType'] == 'RANKED_TEAM_5x5':
                return league_type

        if not queue_found:
            await interaction.response.send_message(f'Player {summoner["name"]} is unranked', ephemeral=True)
            return None


class TftUtilityFunctions(commands.Cog):

    @staticmethod
    async def get_summoner(interaction: nextcord.Interaction, nickname: str):
        """
        Utility method for accessing player's account data from Riot API

            Args:
                interaction (nextcord.Interaction): Context of the command
                nickname (str): Nickname of the plyer

            Returns:
                summoner (dict): Dictionary containing information about specific player
        """
        watcher = TftWatcher(os.getenv('APIKEYTFT'))
        try:
            summoner = watcher.summoner.by_name('eun1', nickname)
            return summoner
        except requests.exceptions.HTTPError:
            await interaction.response.send_message(f'Can\'t find **{nickname}** on EUNE server', ephemeral=True)
            return None

    @staticmethod
    async def get_tft_ranked_stats(interaction: nextcord.Interaction, summoner):
        watcher = TftWatcher(os.getenv('APIKEYTFT'))

        summoner_stats = watcher.league.by_summoner('eun1', summoner['id'])
        if not summoner_stats:
            await interaction.response.send_message(f'Player {summoner} is unranked', ephemeral=True)
            return None

        queue_found = False
        for league_type in summoner_stats:
            if league_type['queueType'] == 'RANKED_TFT':
                return league_type

        if not queue_found:
            await interaction.response.send_message(f'Player {summoner} is unranked', ephemeral=True)
            return


class RiotUtilityFunctions(commands.Cog):

    @staticmethod
    async def get_rank_emoji(summoner_rank: dict):
        rank_dict = await SettingsCommands.load_json_dict("JsonData/rankDict.json")
        for tier in rank_dict:  # iterate over every tier until we find player's tier
            if summoner_rank['tier'] == tier:
                tier_emoji = rank_dict[tier]
                return tier_emoji

    @staticmethod
    async def get_local_rank(summoner_rank: dict):
        local_rank = 0
        rank_list = ['I', 'II', 'III', 'IV']
        rank_dict = await SettingsCommands.load_json_dict("JsonData/rankDict.json")

        for tier in rank_dict:
            if summoner_rank['tier'] != tier:
                local_rank += 400
            else:
                break

        for lol_rank in rank_list:  # iterate over every rank until we find player's rank
            if summoner_rank['rank'] != lol_rank:
                local_rank += 100
            else:
                local_rank += summoner_rank['leaguePoints']  # calculate final rating for leaderboard
                return local_rank


class DatabaseManager(commands.Cog):

    @staticmethod
    async def get_db_collection(db: str, collection: str, *, interaction: nextcord.Interaction = None):
        """
        Utility method that is used to connect to the MongoDB Database

            Args:
                db (str): Name of the Database
                collection (str): Name of the Collection in Database
                interaction (:obj:nextcord.Interaction, optional): Context of the command

            Returns:
                collection: Collection from the Database
        """
        mongo_client = MongoClient(os.getenv('MONGOURL'))
        db = mongo_client[db]
        collection = db[collection]
        if collection is None:
            if interaction:
                await interaction.response.send_message('Cannot connect to the database', ephemeral=True)
                return
        return collection

    @staticmethod
    async def upload_members_to_database(guild: nextcord.Guild):
        """
        Utility method used to import server members into database

            Returns:
                None
        """

        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'new_members')
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


class FilesManager(commands.Cog):

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
        exists = os.path.exists(f'{filepath}\\{channel.name}')
        if not exists:
            os.makedirs(f'{filepath}\\{channel.name}\\Video')
            os.makedirs(f'{filepath}\\{channel.name}\\Text')
            os.makedirs(f'{filepath}\\{channel.name}\\Uncategorized')
            os.makedirs(f'{filepath}\\{channel.name}\\Images')
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
        await FilesManager.create_attachments_dir(filepath=filepath, channel=channel)
        filetype_found = False
        for i_counter, attachment in enumerate(msg.attachments):
            for category, category_filetypes in filetypes.items():
                for filetype in category_filetypes:
                    if attachment.filename.lower().endswith(filetype):
                        fp = f'{filepath}\\{channel.name}\\{category}\\{counter}' \
                             f'_{i_counter}_{msg.author.name}_{created_time}.{filetype}'
                        exists = os.path.exists(f'{filepath}\\{channel.name}')
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


class SettingsCommands(commands.Cog):

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
            final_dict = json.loads(temp_dict)
        return final_dict

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
        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'guild_bot_channels')
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
    async def format_missing_permissions(error: typing.Union[application_checks.ApplicationMissingPermissions,
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

    @staticmethod
    async def get_json_response(url, params, ctx):
        print('Trying to get url...')
        request = requests.get(url, params=params)
        print('Success! Got url, checking status...')
        if request.status_code == 404:
            await ctx.send(f'Couldn\'t find {params["name"]} MMR on EUNE')
            return None
        print('Success! Status is correct, trying to .json()...')
        request = request.json()
        print('Success! Returning dict...')
        return request


def setup(client):
    client.add_cog(LolUtilityFunctions(client))
    client.add_cog(TftUtilityFunctions(client))
    client.add_cog(RiotUtilityFunctions(client))
    client.add_cog(DatabaseManager(client))
    client.add_cog(FilesManager(client))
    client.add_cog(SettingsCommands(client))
