from discord.ext import commands
import json
import asyncio
from pymongo import MongoClient


class SettingsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def load_json_dict(self, filepath: str):
        if not filepath:
            return
        with open(filepath) as file:
            temp_dict = file.read()
            final_dict = json.loads(temp_dict)
            file.close()
        return final_dict

    async def channel_check(self, ctx, channel_id):
        """
        Function used to check if we're sending commands in right channel
        :param ctx: context of the command
        :param channel_id: discord channel where message was sent
        :return channel_check: boolean, means we're in right channel if True
        """
        settings_cog = self.client.get_cog("SettingsCommands")
        if settings_cog is not None:
            guild_bot_channels_dict = await settings_cog.load_json_dict("JsonData/guild_bot_channel.json")
        else:
            await ctx.send("Failed to load server's bot channels file :(")
            return
        channel_check = False
        if guild_bot_channels_dict[str(ctx.guild.id)]:
            for bot_channel in guild_bot_channels_dict[str(ctx.guild.id)]:
                if channel_id == int(bot_channel):
                    channel_check = True
        else:
            channel_check = True
        # sends specific message when we're in wrong command
        if not channel_check:
            our_channel = self.client.get_channel(channel_id)
            await our_channel.send(f"Please, use bot commands in bot channel to prevent spam")
            await asyncio.sleep(3)
            await ctx.channel.purge(limit=1)
        return channel_check

    """
    async def check_time(self, ctx):
        print(f"{ctx.author.name}, Done")
        client = MongoClient()
        print(f"{ctx.author.name}, Done")
        db = client.test
        cluster = MongoClient(client)
        db = cluster['Discord_Bot_DB']
        collection = db['Guild_Members']
        await collection.insert_one({"nickname": ctx.author.name})
        print(f"{ctx.author.name}, Done")
    """

    async def load_members(self):
        iterator = 1
        guilds = {}
        for guild in self.client.guilds:
            guilds[guild.id] = {
                'nickname':
                {
                    'time_on_voice_channel': '',
                    'start_online_time': '',
                    'end_online_time': '',
                    'time_online': '',
                    'time_away': '',
                    'messages_sent': ''
                }
            }
            for member in guild.members:
                if member.bot:
                    continue
                else:
                    guilds[guild.id][member.name] = {
                            'time_on_voice_channel': '',
                            'start_online_time': '',
                            'end_online_time': '',
                            'time_online': '',
                            'time_away': '',
                            'messages_sent': ''
                        }

def setup(client):
    client.add_cog(SettingsCommands(client))
