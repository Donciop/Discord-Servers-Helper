import discord  # main packages
from discord.ext import commands, tasks
from discord_slash import SlashCommand  # for slash commands
import os  # utility packages
import datetime
import json
from datetime import datetime, timedelta

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
async def on_member_join(ctx, member):
    with open("JsonData/guild_members.json", 'w') as guild_members_file:
        guild_members_file_dict = guild_members_file.read()
        guilds = json.loads(guild_members_file_dict)
        guilds[ctx.guild.id][member.name] = {
                    'time_on_voice_channel': '',
                    'time_online': '',
                    'time_away': '',
                    'messages_sent': ''
                }
        json.dump(guilds, guild_members_file)
        guild_members_file.close()


@client.event
async def on_member_update(before, after):
    guild_members_dict = {}
    settings_cog = client.get_cog("SettingsCommands")
    if settings_cog is not None:
        guild_members_dict = await settings_cog.load_json_dict("JsonData/guild_members.json")
    if after.activities and not before.activities:
        for after_activity in after.activities:
            if after_activity.type == discord.ActivityType.playing:
                print(f"{before.display_name} has started playing {after_activity.name}")
            elif after_activity.type == discord.Game:
                print(f"{before.display_name} has started playing {after_activity.name} at {after_activity.start}")
            elif after_activity.type == discord.Spotify:
                print(f"{before.display_name} has started to listen to Spotify.")

    elif before.activities and not after.activities:
        for before_activity in before.activities:
            if before_activity.type == discord.ActivityType.playing:
                print(f"{before.display_name} stopped playing {before_activity.name}")
            elif before_activity.type == discord.Game:
                print(f"{before.display_name} stopped playing {before_activity.name}")
            elif before_activity.type == discord.Spotify:
                print(f"{before.display_name} stopped listening to Spotify.")

    if str(before.status) == 'offline' and str(after.status) == 'online':
        print(f"{before.display_name} went online")
        guild_members_dict[str(before.guild.id)][before.name]['start_online_time'] = datetime.now().replace(
            microsecond=0)
        with open("JsonData/guild_members.json", 'w') as file:
            json.dump(guild_members_dict, file, indent=6, default=str)
            file.close()
    if str(before.status) == 'online' and str(after.status) == 'offline':
        print(f"{before.display_name} went offline")
        guild_members_dict[str(before.guild.id)][before.name]['end_online_time'] = datetime.now().replace(
            microsecond=0)
        with open("JsonData/guild_members.json", 'w') as file:
            json.dump(guild_members_dict, file, indent=6, default=str)
            file.close()
        if guild_members_dict[str(before.guild.id)][before.name]['start_online_time']:
            start_time = guild_members_dict[str(before.guild.id)][before.name]['start_online_time']
            end_time = guild_members_dict[str(before.guild.id)][before.name]['end_online_time']
            if not guild_members_dict[str(before.guild.id)][before.name]['time_online']:
                final_time = "00:00:00"
            else:
                final_time = guild_members_dict[str(before.guild.id)][before.name]['time_online']
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
            final_time = datetime.strptime(final_time, '%H:%M:%S')
            start_time_delta = timedelta(days=start_time.day,
                                         hours=start_time.hour,
                                         minutes=start_time.minute,
                                         seconds=start_time.second)
            end_time_delta = timedelta(days=end_time.day,
                                       hours=end_time.hour,
                                       minutes=end_time.minute,
                                       seconds=end_time.second)
            final_time_delta = timedelta(hours=final_time.hour,
                                         minutes=final_time.minute,
                                         seconds=final_time.second)
            final_time_delta += end_time_delta - start_time_delta
            guild_members_dict[str(before.guild.id)][before.name]['time_online'] = final_time_delta
            print(final_time_delta)
            with open("JsonData/guild_members.json", 'w') as file:
                json.dump(guild_members_dict, file, indent=6, default=str)
                file.close()
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
