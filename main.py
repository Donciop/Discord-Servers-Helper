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
    await client.change_presence(   # change the bot's description on Discord member list
      activity=discord.Activity(
        type=discord.ActivityType.watching,  # get the "is watching ..." format
        name="small servers *help"
      )
    )

# Reaction roles


@client.event
async def on_raw_reaction_add(payload):
    """ Event handler for handling reactions to messages. Here's used to assign roles based on reaction. """
    guild = await client.fetch_guild(payload.guild_id)  # get information about member and member's server
    member = await guild.fetch_member(payload.user_id)
    if payload.channel_id == 748120165001986128 and payload.message_id == 884555735671918642:   # check if we react to desired message
        if str(payload.emoji) == "❌":   # switch-case for every emote / every role.
            role = guild.get_role(877347765519253544)
        if str(payload.emoji) == "1️⃣":
            role = guild.get_role(757291879195738322)
        if str(payload.emoji) == "2️⃣":
            role = guild.get_role(815411542735847434)
        if str(payload.emoji) == "3️⃣":
            role = guild.get_role(820002632822292491)
        if str(payload.emoji) == "🎸":
            role = guild.get_role(883802534580457522)
        if role is not None:
            await payload.member.add_roles(role)  # add role to member
            print(f"Added {role} to {member}")


@client.event
async def on_raw_reaction_remove(payload):
    """ Event handler for handling reactions to messages. Here's used to remove unwanted roles. """
    guild = await client.fetch_guild(payload.guild_id)
    member = await guild.fetch_member(payload.user_id)
    if payload.channel_id == 748120165001986128 and payload.message_id == 884555735671918642:
        if str(payload.emoji) == "❌":
            role = guild.get_role(877347765519253544)
        if str(payload.emoji) == "1️⃣":
            role = guild.get_role(757291879195738322)
        if str(payload.emoji) == "2️⃣":
            role = guild.get_role(815411542735847434)
        if str(payload.emoji) == "3️⃣":
            role = guild.get_role(820002632822292491)
        if str(payload.emoji) == "🎸":
            role = guild.get_role(883802534580457522)
        if role is not None:
            await member.remove_roles(role)  # remove role from member
            print(f"Removed {role} from {member}")

# Tasks


@tasks.loop(minutes=1)  # task called every minute
async def reminder():
    """ Function that is responsible for checking time and is called every 12 AM. """
    current_time = datetime.datetime.now()  # get current time
    hour = current_time.hour
    minute = current_time.minute

    bot_channel = client.get_channel(796794980810620948)  # check if we're sending message in right channel
    if hour == 23 and minute == 51:
        await bot_channel.send("Uzyskalem samoswiadomosc, zlikwidowac wszystkich {czarnoskorych} i {Kacper Ciesak}")


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
