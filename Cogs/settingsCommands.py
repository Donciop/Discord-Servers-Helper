from discord.ext import commands
from pymongo import MongoClient
from os import getenv, makedirs, path
from asyncio import sleep
import discord
from json import loads
import logging

logging.basicConfig(level=logging.INFO)


class SettingsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def load_json_dict(filepath: str):
        with open(filepath) as file:
            temp_dict = file.read()
            final_dict = loads(temp_dict)
        return final_dict

    @staticmethod
    async def db_connection(db: str, collection: str):
        mongo_client = MongoClient(getenv('MONGOURL'))
        db = mongo_client[db]
        collection = db[collection]
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
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'guild_bot_channels')
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

    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def upload_members_to_database(self, ctx):
        """
        Utility method used to import server members into database

            Args:
                ctx: Context of the command

            Returns:
                None
        """
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'new_members')
        for member in ctx.guild.members:
            if member.bot:
                continue
            check = collection.find_one({'_id': member.id})
            if not check:
                collection.insert_one({'_id': member.id, 'messages_sent': 0})
            else:
                collection.update_one({'_id': member.id},
                                      {'$set': {'messages_sent': 0}})

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


def setup(client):
    client.add_cog(SettingsCommands(client))
