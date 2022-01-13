import discord
import os
import datetime
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext

intents = discord.Intents().all()
intents.members = True
client = commands.Bot(command_prefix='&', intents=intents, help_command=None)
slash = SlashCommand(client, sync_commands=True)
client.load_extension("everybodyCommands")
client.load_extension("manageChannelsCommands")
client.load_extension("manageMessagesCommands")
client.load_extension("administratorCommands")
client.load_extension("manageUsersCommands")
client.load_extension("lolCommands")
client.load_extension("tftCommands")


@client.event
async def on_ready():
    print("Bot is ready")
    await client.change_presence(
      activity=discord.Activity(
        type=discord.ActivityType.watching,
        name="small kids *help"
      )
    )

# Reaction roles


@client.event
async def on_raw_reaction_add(payload):
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
            await payload.member.add_roles(role)
            print(f"Added {role} to {member}")


@client.event
async def on_raw_reaction_remove(payload):
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
            await member.remove_roles(role)
            print(f"Removed {role} from {member}")

# Tasks


@tasks.loop(minutes=1)
async def reminder():
    current_time = datetime.datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    bot_channel = client.get_channel(796794980810620948)
    if hour == 12 and minute == 00:
        await bot_channel.send("Wybiło południe")


@reminder.before_loop
async def before():
    await client.wait_until_ready()


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(color=0xeb1414)
        embed.add_field(
          name="🛑 Command Error",
          value="Command's on cooldown. Time remaining: {}s :(".format(round(error.retry_after)),
          inline=False
        )
        await ctx.send(embed=embed)
        return
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(color=0xeb1414)
        embed.add_field(
          name="🛑 Command Error",
          value="You don't have permissions to use this command, check *help for more info",
          inline=False
        )
        await ctx.send(embed=embed)
        return

reminder.start()
client.run(os.getenv('ALPHATOKEN'))
