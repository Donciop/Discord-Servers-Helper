import discord
import asyncio
import typing
from discord.ext import commands
from main import client

class everybodyCommands(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.Cog.listener()
  async def on_ready(self):
    self.newsChannel = client.get_channel(748120165001986128)
    self.botChannel = client.get_channel(888056072538042428)
    self.testChannel = client.get_channel(902710519646015498)
    self.owner = client.get_user(198436287848382464)
    self.guild = client.get_guild(218510314835148802)
  
  @commands.command()
  @commands.cooldown(1, 1, commands.BucketType.user)
  async def help(self, ctx):
    if ctx.channel.id == self.botChannel.id or ctx.channel.id == self.newsChannel.id or ctx.channel.id == self.testChannel.id:
      embed=discord.Embed(color=0x11f80d, title="📜 COMMANDS")
      embed.add_field(name="**Use `*` before every command**", value="Most of the commands have to be used in -> ".format(self.botChannel.mention), inline=False)
      embed.add_field(name="📜 EVERYBODY", value="""
      **★ `msgCountMember [Optional(@user)]`**\nCount all messages from specific user in channel where this command is sent. If user isn't specified, it will count messages of person who send the command\n
      **★ `poke [@user]`**\nMoves user between voice channels to poke him.\n
      **★ `online [@role]`**\nShows online users with this role\n
      **★ `papaj`**\nSends cenzo.\n
      **★ `keyword [word: str]`**\nLook for a specific word or words in last 1k messages and get jump URL's to them. Keyword has to be longer than 5 letters.\n
      **★ `bans`**\nShow banned users on this server""", inline=False)
      embed.add_field(name="📜 MANAGE CHANNELS", value="""
      **★ `mute [@user] [Optional(time: min)] [Optional(reason: str)]`**\nMute user for certain amount of time (permanently if no time specified). You can provide a reason or leave it blank.\n
      **★ `deaf [@user] [Optional(time: min)] [Optional(reason: str)]`**\nDeafen user for certain amount of time (permanently if no time specified). You can provide a reason or leave it blank.\n
      **★ `mutecf [@user]`**\n50% chance to mute user for 1 minute, but 50% chance to mute yourself for 3 minutes instead.""", inline=False)
      embed.add_field(name="📜 MANAGE MESSAGES", value="""
      **★ `clear [amount: int]`**\nDelete specified amount of messages from channel\n
      **★ `msgCount [Optional(#channel)]`**\nCount messages in specific channel or in current channel if not specified.
      """, inline=False)
      embed.add_field(name="📜 MANAGE USERS", value="""
      **★ `unban [@user]`**\nUnban specific user
      """, inline=False)
      embed.add_field(name="📜 ADMINISTRATOR", value="""
      **★ `top`**\nShows leaderboard of messages in specific channel, only available for administrator because of long computing time""", inline=False)
      embed.add_field(name="📜 ROLES", value="Get yourself a role or remove it here -> {}".format(self.newsChannel.mention), inline=False)
      embed.set_footer(text=f"Copyrighted by {self.owner.name}#9970")
      await ctx.send(embed=embed)
    else:
      embed=discord.Embed(color=0xeb1414)
      embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
      embed.add_field(name="🛑 Help Failed", value="You can't post commands outside of {}, dumbass".format(self.botChannel.mention), inline=False)
      await ctx.send(embed=embed)

  @commands.command()
  @commands.cooldown(1, 30, commands.BucketType.user)
  async def online(self, ctx, role: typing.Optional[discord.Role]):
    members = role.members
    empty = True
    embed=discord.Embed(color=0x11f80d)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    if not role:
      embed.add_field(name="🛑 Online Failed", value="You have to specify a role")
    for member in members:
      if str(member.status) == "online":
        embed.add_field(name="✅ Online", value=f"★ {member.display_name}", inline = False)
        empty = False
    if empty:
      embed=discord.Embed(color=0xeb1414)
      embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
      embed.add_field(name="💤 Offline", value="Everybody's offline :(", inline = False)
    await ctx.send(embed=embed)

  @commands.command()
  @commands.cooldown(1, 30, commands.BucketType.user)
  async def poke(self, ctx, *members: typing.Optional[discord.Member]):
    embed=discord.Embed(color=0x11f80d)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    if not members:
      embed.add_field(name="🛑 Poke Failed", value="You have to specify who to poke")
      return
    if len(members) > 3:
      embed.add_field(name="🛑 Poke Failed", value="You can't poke that many users")
      return
    for member in members:
      if ctx.message.author == member:
        embed=discord.Embed(color=0xeb1414)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="🛑 Poke Failed", value="You can't poke yourself, dumbass")
      else:
        embed.add_field(name="✅ Poke Successful", value=f"You've poked {member.display_name}", inline=False)
        userChannel = member.voice.channel
        if member.voice.channel == self.guild.afk_channel:
          await member.move_to(userChannel)
          await asyncio.sleep(2)
          await member.move_to(self.guild.afk_channel)
        else:
          await member.move_to(self.guild.afk_channel)
          await asyncio.sleep(2)
          await member.move_to(userChannel)
    await ctx.send(embed=embed)

  @commands.command()
  @commands.cooldown(1, 10, commands.BucketType.user)
  async def msgCountMember(self, ctx, member: typing.Optional[discord.Member]):
    if not member:
      member = ctx.author
    channel = ctx.channel
    counter = 0
    async with ctx.typing():
      async for msg in channel.history(limit=None):
        if msg.author == member:
          counter += 1
      await ctx.send(f"User {member.display_name} had written {str(counter)} messages in {channel.mention}")

  @commands.command()
  @commands.cooldown(1, 10, commands.BucketType.user)
  async def bans(self, ctx):
    bannedUsers = await self.guild.bans()
    embed=discord.Embed(color=0xeb1414, title="👮‍♂️ BANNED USERS 👮‍♂️", description="For advanced information, ask administration or moderators.")
    auditLogs = {}
    async for entry in self.guild.audit_logs(action=discord.AuditLogAction.ban, limit=None):
      auditLogs[entry.target.name] = entry.user.name
    for banEntry in bannedUsers:
      if str(banEntry.user.name) in auditLogs:
        embed.add_field(name=f"{banEntry.user.name} #{banEntry.user.discriminator}", value=f"banned by {auditLogs[str(banEntry.user.name)]}", inline=False)
      else:
        embed.add_field(name="{} #{}".format(banEntry.user.name, banEntry.user.discriminator), value="\u200B", inline=False)
    file = discord.File("Media/jail.png", filename="image.png")
    embed.set_thumbnail(url="attachment://image.png")
    await ctx.send(embed=embed, file=file)
      
  @commands.command()
  @commands.cooldown(1, 10, commands.BucketType.user)
  async def keyword(self, ctx,*,word: str):
    count = 0
    if len(word) >= 5:
      async with ctx.typing():
        messages = await ctx.channel.history(limit=1000).flatten()
        for msg in messages:
          if word in msg.content:
            count += 1
            await ctx.send(msg.jump_url)
    else:
      await ctx.send("A keyword should be longer or equal to 5 letters")

def setup(client):
    client.add_cog(everybodyCommands(client))