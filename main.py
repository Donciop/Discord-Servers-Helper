import discord  # main packages
from discord.ext import commands, tasks
from discord_slash import SlashCommand  # for slash commands
import os  # utility packages
import datetime

# Making sure the bot has all the permissions

intents = discord.Intents().all()
intents.members = True

# Initialize bot

client = commands.Bot(command_prefix='*', intents=intents, help_command=None)
slash = SlashCommand(client, sync_commands=True)

# Loading cogs

client.load_extension("everybodyCommands")
client.load_extension("reactionCommands")
client.load_extension("manageChannelsCommands")
client.load_extension("manageMessagesCommands")
client.load_extension("administratorCommands")
client.load_extension("manageUsersCommands")
client.load_extension("lolCommands")
client.load_extension("tftCommands")

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

# Tasks


@tasks.loop(minutes=1)  # task called every minute
async def reminder():
    """ Function that is responsible for checking time and is called every 12 AM. """
    current_time = datetime.datetime.now()  # get current time
    hour = current_time.hour
    minute = current_time.minute

    bot_channel = client.get_channel(796794980810620948)  # check if we're sending message in right channel
    if hour == 11 and minute == 00:
        await bot_channel.send("It's high noon!")


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
