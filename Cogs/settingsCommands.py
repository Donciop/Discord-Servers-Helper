import requests.exceptions
from discord.ext import commands
from pymongo import MongoClient
from os import getenv, makedirs, path
from asyncio import sleep
import discord
from json import loads, dump
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
    async def db_connection(db: str, collection: str, *, ctx=None):
        """
        Utility method that is used to connect to the MongoDB Database

            Args:
                db (str): Name of the Database
                collection (str): Name of the Collection in Database
                ctx (optional): Context of the command

            Returns:
                collection: Collection from the Database
        """
        mongo_client = MongoClient(getenv('MONGOURL'))
        db = mongo_client[db]
        collection = db[collection]
        if collection is None:
            if ctx:
                await ctx.send('Cannot connect to the database')
                return
            else:
                return
        return collection

    @staticmethod
    async def channel_check(ctx):
        """
        Utility method that is used to check if user is sending commands in channel that allows it

            Args:
                ctx: Context of the command

            Returns:
                bool: True if user can send messages in this channel, False otherwise
        """
        channel_check = False
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'guild_bot_channels', ctx=ctx)
        if collection is None:
            return
        check = collection.find_one({'_id': ctx.guild.id})
        if not check:
            channel_check = True
        else:
            for bot_channel in check['bot_channels']:
                if ctx.channel.id == int(bot_channel):
                    channel_check = True

        # sends specific message if command is used in forbidden channel
        if not channel_check:
            await ctx.channel.send(f'Please, use bot commands in bot channel to prevent spam')
            await sleep(2)
            await ctx.channel.purge(limit=1)
        return channel_check

    @staticmethod
    async def create_attachments_dir(*, filepath: str, channel: discord.TextChannel):
        """
        Utility method used to create specific directory when using *save_attachments command

            Args:
                filepath (str): Filepath to the directory that we want to create our subdirectory
                channel (discord.Channel): Discord Text Channel in which we want to save attachments

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
                              channel: discord.TextChannel, msg: discord.Message):
        """
        Utility method used to categorize Attachments sent to channels

            Args:
                filepath (str): Filepath to the directory that we want to save our files in
                counter (int):  Number of attachment that we're trying to save
                channel (discord.Channel): Discord Channel in which we're saving attachments
                msg (discord.Message): Discord Message that contains our attachment

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
                        except discord.HTTPException:
                            return False
            if not filetype_found:
                try:
                    fp = f'{filepath}\\{channel.name}\\Uncategorized\\{counter}' \
                         f'_{i_counter}_{msg.author.name}_{created_time}.{str(attachment.filename)[:-5]}'
                    await attachment.save(fp=fp)
                    return True
                except discord.HTTPException:
                    return False

    @staticmethod
    async def get_riot_stats(ctx, *, stats_type: str, nickname: str, all_stats=False):
        """
        Utility method used to gather information about player's rank

            Args:
                ctx: Context of the command
                stats_type (str): Whether we gather stats from League of Legends (LOL) or Teamfight Tactics (TFT)
                nickname (str): Player's nickname
                all_stats (bool, optional): if True, gather information about all queue types
                from Teamfight Tactics (TFT)

            Returns:
                summoner (dict): Information about players profile
                summoner_stats (dict): Information about player's rank
        """
        watcher = TftWatcher(getenv('APIKEYTFT'))
        if stats_type.lower() == 'lol':
            watcher = LolWatcher(getenv('APIKEYLOL'))

        try:
            summoner = watcher.summoner.by_name('eun1', nickname)
        except requests.exceptions.HTTPError:
            summoner_stats = []
            summoner = ''
            await ctx.send(f"Can't find **{nickname}** on EUNE server.")
            return summoner, summoner_stats

        summoner_stats = watcher.league.by_summoner('eun1', summoner['id'])
        if not summoner_stats:
            summoner_stats = []
            await ctx.send(f'Player {nickname} is unranked')
            return summoner, summoner_stats

        if all_stats:
            return summoner, summoner_stats
        queue_found = False
        for league_type in summoner_stats:
            if league_type['queueType'] == 'RANKED_TFT':
                queue_found = True
                return summoner, league_type
            else:
                queue_found = False
        if not queue_found:
            summoner_stats = []
            await ctx.send(f'Player {nickname} is unranked')
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
                tier_emoji: custom emoji based on player's rank
                rank (int): calculated rating for local leaderboard
        """

        rank_dict = await SettingsCommands.load_json_dict("JsonData/rankDict.json")
        rank_list = ['I', 'II', 'III', 'IV']
        local_rank = 0
        local_tier_emoji = None
        if not summoner_rank:
            return local_tier_emoji, local_rank
        for tier in rank_dict:  # iterate over every tier until we find player's tier
            if summoner_rank[0]['tier'] != tier:
                local_rank += 400
            else:
                local_tier_emoji = rank_dict[tier]
                break
        for lol_rank in rank_list:  # iterate over every rank until we find player's rank
            if summoner_rank[0]['rank'] != lol_rank:
                local_rank += 100
            else:
                break
        local_rank += summoner_rank[0]['leaguePoints']  # calculate final rating for leaderboard
        if rank and tier_emoji:
            return local_tier_emoji, local_rank
        elif rank:
            return rank
        else:
            return local_tier_emoji

def setup(client):
    client.add_cog(SettingsCommands(client))
