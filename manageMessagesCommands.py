import discord
import typing
from discord.ext import commands
from main import client
class manageMessagesCommands(commands.Cog):
  def __init__(self, client):
    self.client = client
   
  @commands.command()
  @commands.has_permissions(manage_messages = True)
  @commands.cooldown(1, 10, commands.BucketType.user)
  async def msgCount(self, ctx, channel: typing.Optional[discord.TextChannel]):
    embed=discord.Embed(color=0x11f80d)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    if not channel:
      channel = ctx.channel
    count = 0
    async with ctx.typing():
      async for msg in channel.history(limit=None):
        count += 1
      embed.add_field(name="✅ Message Count Successfull", value=f"There were {count} messages in {channel.mention}", inline=False)
      await ctx.send(embed=embed)
      
  @commands.command()
  @commands.has_permissions(manage_messages = True)
  @commands.cooldown(1, 1, commands.BucketType.user)
  async def clear(self, ctx, amount: int = 0):
    embed=discord.Embed(color=0xeb1414)
    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
    if not amount:
      embed.add_field(name="🛑 Clear Error", value="Specify amount of messages to clear", inline=False)
      await ctx.send(embed=embed)
    elif amount > 20:
      embed.add_field(name="🛑 Clear Error", value="Too many messages to clear! (max: 20)", inline=False)
      await ctx.send(embed=embed)
    else:
      await ctx.channel.purge(limit=amount+1)

  @clear.error
  async def clear_error(self, ctx, error):
    if isinstance(error, commands.BadArgument):
      embed=discord.Embed(color=0xeb1414)
      embed.add_field(name="🛑 Clear Error", value="Wrong number of messages", inline=False)
      await ctx.send(embed=embed)

def setup(client):
  client.add_cog(manageMessagesCommands(client))