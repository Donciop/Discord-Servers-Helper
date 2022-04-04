from discord.ext import commands
from pymongo import MongoClient
import discord
import os
import json
import asyncio


class SettingsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def load_json_dict(filepath: str):
        with open(filepath) as file:
            temp_dict = file.read()
            final_dict = json.loads(temp_dict)
            file.close()
        return final_dict

    @staticmethod
    async def db_connection(db: str, collection: str):
        mongo_client = MongoClient(os.getenv('MONGOURL'))
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
            await asyncio.sleep(2)
            await ctx.channel.purge(limit=1)
        return channel_check

    @staticmethod
    async def create_attachments_dir(channel: discord.TextChannel):
        """
        Utility method used to create specific directory when using *save_attachments command

            Args:
                channel (discord.Channel): Discord Text Channel in which we want to save attachments

            Returns:
                None
        """
        exists = os.path.exists(f'{channel.name}')
        if not exists:
            os.makedirs(f'{channel.name}/Attachments/Video')
            os.makedirs(f'{channel.name}/Attachments/Text')
            os.makedirs(f'{channel.name}/Attachments/Uncategorized')
            os.makedirs(f'{channel.name}/Attachments/Images')

    @staticmethod
    async def get_filetype(*, filetypes: list = None, dir_name: str, attachment: discord.Attachment, counter: int,
                           internal_counter: int,
                           channel: discord.TextChannel, msg: discord.Message, created_time: str):
        """
        Utility method used to categorize Attachments sent to channels

            Args:
                filetypes (:obj:'list', optional): List of filetypes that we're looking for
                dir_name (str): Name of the subdirectory that we want to save our files in
                attachment (discord.Attachment): Discord attachment that we want to save
                counter (int):  Number of attachment that we're trying to save
                internal_counter (int): If there's more than one attachment in message,
                                        we separate them by internal counters
                channel (discord.Channel): Discord Channel in which we're saving attachments
                msg (discord.Message): Discord Message that contains our attachment
                created_time (str): Date, which tells us, when the message was created

            Returns:
                bool: True if successful, False otherwise
        """
        if not filetypes:
            dir_name = 'Uncategorized'
        for filetype in filetypes:
            if attachment.filename.lower().endswith(filetype):
                try:
                    await attachment.save(
                        f'{channel.name}/Attachments/{dir_name}/{counter}'
                        f'_{internal_counter}'
                        f'_{msg.author.name}'
                        f'_{created_time}.{filetype}')
                    return True
                except discord.HTTPException:
                    print('Cannot save attachment')
                    return False


def setup(client):
    client.add_cog(SettingsCommands(client))
