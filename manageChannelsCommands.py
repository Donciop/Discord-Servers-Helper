import discord
import typing
import asyncio
import random
from discord.ext import commands
from main import client

class manageChannelsCommands(commands.Cog):
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
  @commands.has_permissions(mute_members = True)
  @commands.cooldown(1, 10, commands.BucketType.user)
  async def mute(self, ctx, member: typing.Optional[discord.Member], mute_minutes: typing.Optional[int] = 0,*, reason: typing.Optional[str] = ""):
    embed=discord.Embed(color=0xeb1414)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    if member:
      if ctx.channel.id == self.botChannel or ctx.channel.id == self.testChannel or ctx.channel.id == self.newsChannel:
        await member.edit(mute = True)
        embed=discord.Embed(color=0x11f80d)
        if not mute_minutes:
          embed.add_field(name="🔇 Mute Successful", value=f"**{member.display_name}** was muted by **{ctx.author.display_name}**", inline=False)
        else:
          embed.add_field(name="🔇 Mute Successful", value=f"**{member.display_name}** was muted by **{ctx.author.display_name}** for 🕐 **{str(mute_minutes)}** minutes", inline=False)
        if reason:
          embed.add_field(name="📜 Reason", value=reason, inline=False)
      else:
        embed.add_field(name="🛑 Mute Failed", value=f"You can't post commands outside of {self.botChannel.mention} dumbass", inline=False)
    else:
      embed.add_field(name="🛑 Mute Failed", value="You have to specify a Discord member to mute",inline=False)
    await ctx.send(embed=embed)
    if mute_minutes > 0:
      await asyncio.sleep(mute_minutes * 60)
      await member.edit(mute = False)
    
  @commands.command()
  @commands.has_permissions(mute_members = True)
  @commands.cooldown(1, 10, commands.BucketType.user)
  async def deaf(self, ctx, member: typing.Optional[discord.Member], deaf_minutes: typing.Optional[int] = 0,*, reason: typing.Optional[str] = ""):
    embed=discord.Embed(color=0xeb1414)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    if member:
      if ctx.channel.id == self.botChannel.id or ctx.channel.id == self.newsChannel.id or ctx.channel.id == self.testChannel.id:
        await member.edit(deafen = True)
        embed=discord.Embed(color=0x11f80d)
        if not deaf_minutes:
          embed.add_field(name="🔇 Deaf Successful", value=f"**{member.display_name}** was deafened by **{ctx.author.display_name}**", inline=False)
        else:
          embed.add_field(name="🔇 Deaf Successful", value=f"**{member.display_name}** was deafened by **{ctx.author.display_name}** for 🕐 **{str(deaf_minutes)}** minutes", inline=False)
        if reason:
          embed.add_field(name="📜 Reason", value=reason, inline=False)
      else:
        embed.add_field(name="🛑 Deaf Failed", value=f"You can't post commands outside of {self.botChannel.mention} dumbass", inline=False)
    else:
      embed.add_field(name="🛑 Deaf Failed", value="You have to specify a Discord member to mute",inline=False)
    await ctx.send(embed=embed)
    if deaf_minutes > 0:
      await asyncio.sleep(deaf_minutes * 60)
      await member.edit(deaf = False)

  @commands.command()
  @commands.has_permissions(mute_members = True)
  @commands.cooldown(1, 300, commands.BucketType.user)
  async def mutecf(self, ctx, member: typing.Optional[discord.Member]):
    mute_minutes_self = 0
    mute_minutes = 0
    number = random.randint(0,100)
    embed=discord.Embed(color=0xeb1414)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    if member:
      if ctx.channel.id == self.botChannel.id or ctx.channel.id == self.newsChannel.id or ctx.channel.id == self.testChannel.id:
        if ctx.message.author != member:
          if number >= 50:
            embed=discord.Embed(color=0x11f80d)
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
            await member.edit(mute = True)
            embed.add_field(name="✅ Mute Coinflip Succesful", value=f"You've rolled {str(number)} and muted {member.display_name} for 1 minute", inline=False)
            mute_minutes += 1
          else:
            await ctx.author.edit(mute = True)
            embed.add_field(name="🛑 Mute Coinflip Failed", value=f"You've rolled {str(number)} and failed to mute {member.display_name}, however you got muted for 3 minutes", inline=False)
            mute_minutes_self += 3
        else:
          embed.add_field(name="🛑 Mute Coinflip Failed", value="You can't coinflip with yourself dumbass", inline=False)
      else:
        embed.add_field(name="🛑 Mute Coinflip Failed", value=f"You can't post commands outside of {self.botChannel.mention} dumbass", inline=False)
    else:
      embed.add_field(name="🛑 Mute Coinflip Failed", value="You have to specify a Discord member to mute",inline=False)
    await ctx.send(embed=embed)
    if mute_minutes_self > 0:
      await asyncio.sleep(mute_minutes_self * 60)
      await ctx.author.edit(mute = False)
    if mute_minutes > 0:
      await asyncio.sleep(mute_minutes * 60)
      await member.edit(mute = False)

  @mute.error
  async def mute_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      embed=discord.Embed(color=0xeb1414)
      embed.add_field(name="🛑 Mute Error", value="Enter proper time (in minutes)", inline=False)
      await ctx.send(embed=embed)

  @deaf.error
  async def deaf_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      embed=discord.Embed(color=0xeb1414)
      embed.add_field(name="🛑 Deaf Error", value="Enter proper time (in minutes)", inline=False)
      await ctx.send(embed=embed)

def setup(client):
  client.add_cog(manageChannelsCommands(client))