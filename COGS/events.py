from nextcord.ext import commands
from COGS.settingsCommands import DatabaseManager
from logger import get_logger
import nextcord

# Setting up logging
bot_logger = get_logger()


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """ Event handler that is called when bot is turned on. """
        bot_logger.info("Bot is ready")
        await self.client.sync_all_application_commands()

        bot_logger.info("Application commands synced")
        await self.client.change_presence(  # change the bot description on Discord member list
            activity=nextcord.Activity(
                type=nextcord.ActivityType.watching,  # get the "is watching ..." format
                name="small servers *help"
            )
        )
        bot_logger.info("Activity changed")
    #
    # @commands.Cog.listener()
    # async def on_message(self, message: nextcord.Message):
    #     """
    #     Event handler that is called when someone sends a message on discord channel
    #
    #         Args:
    #             message (nextcord.Message): Discord Message
    #
    #         Returns:
    #             None
    #     """
    #     collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'new_members')
    #     if collection is None:
    #         return
    #     collection.update_one(
    #         {"_id": message.author.id},
    #         {"$inc": {"messages_sent": 1}}
    #     )
    #     await self.client.process_commands(message)

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        """
        Event handler that is called when a new member joins a Discord Channel

            Args:
                member (nextcord.Member): Discord Member that joins Discord Server (Guild)

            Returns:
                None
        """
        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'new_members')
        if collection is None:
            return

        check = collection.find_one({"_id": member.id})
        if not check:
            query = {
                '_id': member.id,
                'messages_sent': 0
            }
            collection.insert_one(query)

    # @client.event
    # async def on_member_update(before, after):
    #     collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'members')
    #     if after.activities and not before.activities:
    #         for after_activity in after.activities:
    #             if after_activity.type == discord.ActivityType.playing:
    #                 if after_activity.name == "League of Legends":
    #                     league_player = collection.find_one({"_id": before.id})
    #                     if league_player is not None:
    #                         collection.update_one({"_id": after.id},
    #                                               {"$set": {"league_start_time": datetime.now().replace(microsecond=0)}})
    #                 print(f"{before.display_name} has started playing {after_activity.name}")
    #             elif after_activity.type == discord.Game:
    #                 print(f"{before.display_name} has started playing {after_activity.name} at {after_activity.start}")
    #             elif after_activity.type == discord.Spotify:
    #                 print(f"{before.display_name} has started to listen to Spotify.")
    #
    #     elif before.activities and not after.activities:
    #         for before_activity in before.activities:
    #             if before_activity.type == discord.ActivityType.playing:
    #                 if before_activity.name == "League of Legends":
    #                     if collection.find_one({"_id": before.id}):
    #                         collection.update_one({"_id": after.id},
    #                                               {"$set": {"league_end_time": datetime.now().replace(microsecond=0)}})
    #                         start_time = collection.find_one({"_id": before.id}, {"league_start_time": 1})
    #                         end_time = collection.find_one({"_id": before.id}, {"league_end_time": 1})
    #                         final_time = collection.find_one({"_id": before.id}, {"league_time": 1})
    #                         if final_time['league_time'] == "00:00:00":
    #                             final_time['league_time'] = datetime.strptime(final_time['league_time'], '%H:%M:%S')
    #                         final_time['league_time'] += (end_time['league_end_time'] - start_time['league_start_time'])
    #                         collection.update_one({"_id": before.id},
    #                                               {"$set": {"league_time": final_time['league_time']}})
    #                 print(f"{before.display_name} stopped playing {before_activity.name}")
    #             elif before_activity.type == discord.Game:
    #                 print(f"{before.display_name} stopped playing {before_activity.name}")
    #             elif before_activity.type == discord.Spotify:
    #                 print(f"{before.display_name} stopped listening to Spotify.")
    #
    #     if str(before.status) == 'offline' and str(after.status) == 'online':
    #         print(f"{before.display_name} went online")
    #         if collection.find_one({"_id": before.id}):
    #             collection.update_one({"_id": before.id},
    #                                   {"$set": {"start_online_time": datetime.now().replace(microsecond=0)}})
    #
    #     if str(before.status) == 'online' and str(after.status) == 'offline':
    #         print(f"{before.display_name} went offline")
    #         if collection.find_one({"_id": before.id}):
    #             collection.update_one({"_id": before.id},
    #                                   {"$set": {"end_online_time": datetime.now().replace(microsecond=0)}})
    #         start_time = collection.find_one({"_id": before.id}, {"start_online_time": 1, "_id": 0})
    #         if start_time['start_online_time'] == 0:
    #             start_time = datetime.now().replace(microsecond=0)
    #         end_time = collection.find_one({"_id": before.id}, {"end_online_time": 1, "_id": 0})
    #         if end_time['end_online_time'] == 0:
    #             end_time = datetime.now().replace(microsecond=0)
    #         final_time = collection.find_one({"_id": before.id}, {"time_online": 1, "_id": 0})
    #         if final_time['time_online'] == 0:
    #             final_time['time_online'] = "00:00:00"
    #             final_time['time_online'] = datetime.strptime("00:00:00", '%H:%M:%S')
    #         final_time['time_online'] += (end_time['end_online_time'] - start_time['start_online_time'])
    #         collection.update_one({"_id": before.id},
    #                               {"$set": {"time_online": final_time['time_online']}})
    #
    #     if str(before.status) == 'online' and str(after.status) == 'idle':
    #         print(f"{before.display_name} is away")
    #
    #     if str(before.status) == 'idle' and str(after.status) == 'online':
    #         print(f"{before.display_name} is back")


def setup(client):
    client.add_cog(Events(client))
