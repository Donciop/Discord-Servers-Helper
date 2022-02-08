import discord  # main packages
from discord.ext import commands, tasks
from discord_slash import SlashCommand  # for slash commands
import os  # utility packages
import datetime
from datetime import datetime
from pymongo import MongoClient

# Making sure the bot has all the permissions

intents = discord.Intents().all()
intents.members = True

# Initialize bot

client = commands.Bot(command_prefix='*', intents=intents, help_command=None)
slash = SlashCommand(client, sync_commands=True)

# Loading cogs

for filename in os.listdir("./Cogs"):
    print(filename)
    if filename.endswith(".py"):
        client.load_extension(f"Cogs.{filename[:-3]}")
        print("Cog Loaded!")

# Event handling


@client.event
async def on_ready():
    """ Event handler that is called when bot is turned on. """
    print("Bot is ready")
    await client.change_presence(   # change the bot description on Discord member list
      activity=discord.Activity(
        type=discord.ActivityType.watching,  # get the "is watching ..." format
        name="small servers *help"
      )
    )


@client.event
async def on_message(message):
    mongo_client = MongoClient(os.getenv('MONGOURL'))
    db = mongo_client['Discord_Bot_Database']
    collection = db['members']
    collection.update_one(
        {"nickname": message.author.name},
        {"$inc": {"messages_sent": 1}}
    )
    await client.process_commands(message)


@client.event
async def on_member_join(member):
    mongo_client = MongoClient(os.getenv('MONGOURL'))
    db = mongo_client['Discord_Bot_Database']
    collection = db['members']
    check = collection.find_one({"_id": member.id})
    if not check:
        query = {
            '_id': member.id,
            'nickname': member.name,
            'time_on_voice_channel': 0,
            'start_online_time': 0,
            'end_online_time': 0,
            'time_online': 0,
            'time_away': 0,
            'messages_sent': 0
        }
        collection.insert_one(query)
    else:
        print("User's in database")


@client.event
async def on_member_update(before, after):
    mongo_client = MongoClient(os.getenv('MONGOURL'))
    db = mongo_client['Discord_Bot_Database']
    collection = db['members']
    if after.activities and not before.activities:
        for after_activity in after.activities:
            if after_activity.type == discord.ActivityType.playing:
                if after_activity.name == "League of Legends":
                    if collection.find_one({"_id": before.id}):
                        collection.update_one({"_id": after.id},
                                              {"$set": {"league_start_time": datetime.now().replace(microsecond=0)}})
                print(f"{before.display_name} has started playing {after_activity.name}")
            elif after_activity.type == discord.Game:
                print(f"{before.display_name} has started playing {after_activity.name} at {after_activity.start}")
            elif after_activity.type == discord.Spotify:
                print(f"{before.display_name} has started to listen to Spotify.")

    elif before.activities and not after.activities:
        for before_activity in before.activities:
            if before_activity.type == discord.ActivityType.playing:
                if before_activity.name == "League of Legends":
                    if collection.find_one({"_id": before.id}):
                        collection.update_one({"_id": after.id},
                                              {"$set": {"league_end_time": datetime.now().replace(microsecond=0)}})
                        start_time = collection.find_one({"_id": before.id}, {"league_start_time": 1})
                        end_time = collection.find_one({"_id": before.id}, {"league_end_time": 1})
                        final_time = collection.find_one({"_id": before.id}, {"league_time": 1})
                        if final_time['league_time'] == "00:00:00":
                            final_time['league_time'] = datetime.strptime(final_time['league_time'], '%H:%M:%S')
                        final_time['league_time'] += (end_time['league_end_time'] - start_time['league_start_time'])
                        collection.update_one({"_id": before.id},
                                              {"$set": {"league_time": final_time['league_time']}})
                print(f"{before.display_name} stopped playing {before_activity.name}")
            elif before_activity.type == discord.Game:
                print(f"{before.display_name} stopped playing {before_activity.name}")
            elif before_activity.type == discord.Spotify:
                print(f"{before.display_name} stopped listening to Spotify.")

    if str(before.status) == 'offline' and str(after.status) == 'online':
        print(f"{before.display_name} went online")
        if collection.find_one({"_id": before.id}):
            collection.update_one({"_id": before.id},
                                  {"$set": {"start_online_time": datetime.now().replace(microsecond=0)}})

    if str(before.status) == 'online' and str(after.status) == 'offline':
        print(f"{before.display_name} went offline")
        if collection.find_one({"_id": before.id}):
            collection.update_one({"_id": before.id},
                                  {"$set": {"end_online_time": datetime.now().replace(microsecond=0)}})
        start_time = collection.find_one({"_id": before.id}, {"start_online_time": 1, "_id": 0})
        if start_time['start_online_time'] == 0:
            start_time = datetime.now().replace(microsecond=0)
        end_time = collection.find_one({"_id": before.id}, {"end_online_time": 1, "_id": 0})
        if end_time['end_online_time'] == 0:
            end_time = datetime.now().replace(microsecond=0)
        final_time = collection.find_one({"_id": before.id}, {"time_online": 1, "_id": 0})
        if final_time['time_online'] == 0:
            final_time['time_online'] = "00:00:00"
            final_time['time_online'] = datetime.strptime("00:00:00", '%H:%M:%S')
        final_time['time_online'] += (end_time['end_online_time'] - start_time['start_online_time'])
        collection.update_one({"_id": before.id},
                              {"$set": {"time_online": final_time['time_online']}})

    if str(before.status) == 'online' and str(after.status) == 'idle':
        print(f"{before.display_name} is away")

    if str(before.status) == 'idle' and str(after.status) == 'online':
        print(f"{before.display_name} is back")


# Tasks


@tasks.loop(minutes=1)  # task called every minute
async def reminder():
    """ Function that is responsible for checking time and is called every 12 AM. """
    current_time = datetime.now()  # get current time
    hour = current_time.hour
    minute = current_time.minute

    bot_channel = client.get_channel(796794980810620948)  # check if we're sending message in right channel
    if hour == 11 and minute == 00:
        await bot_channel.send("""
        It's high noon!
        
        Please vote for my second bot, Discord Wordsy, so I could have Alak Kebab once a week
        https://top.gg/bot/934989894995021866/vote
        """)
    if hour == 23 and minute == 00:
        await bot_channel.send("""
        It's midnight!
        
        Please vote for my second bot, Discord Wordsy, so I could have Alak Kebab once a week
        https://top.gg/bot/934989894995021866/vote
        """)


@reminder.before_loop
async def before():  # wait for bot to go online to start the task
    await client.wait_until_ready()

# Error handling


@client.event
async def on_command_error(ctx, error):
    """ Error handling for exceptions when using commands. Called when bot encounters an error. """
    if isinstance(error, commands.CommandOnCooldown):  # called when you try to use command that is on cooldown.
        embed = discord.Embed(color=0xeb1414)  # Discord embed formatting
        embed.add_field(
          name="🛑 Command Error",
          value="Command's on cooldown. Time remaining: {}s :(".format(round(error.retry_after)),
          inline=False
        )
        await ctx.send(embed=embed)  # send the embed
        return
    if isinstance(error, commands.MissingPermissions):  # called when you don't have permission to use that command.
        embed = discord.Embed(color=0xeb1414)
        embed.add_field(
          name="🛑 Command Error",
          value="You don't have permissions to use this command, check *help for more info",
          inline=False
        )
        await ctx.send(embed=embed)
        return

reminder.start()  # start tasks
client.run(os.getenv('TOKEN'))  # actually run the bot and pass the secret TOKEN
