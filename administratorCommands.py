import discord
from discord.ext import commands

class administratorCommands(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  @commands.has_permissions(administrator = True)
  @commands.cooldown(1, 10, commands.BucketType.guild)
  async def top(self, ctx, numberOfMessages):
    leaderboardNotSorted = {}
    channel = ctx.channel
    print(channel.members)
    async with ctx.typing():
      for member in channel.members:
        counter = 0
        async for msg in channel.history(limit=None):
          if msg.author == member:
            counter += 1
        leaderboardNotSorted["{}#{}".format(str(member.display_name), str(member.discriminator))] = counter
    leaderboardSorted = sorted(leaderboardNotSorted.items(), key=lambda x: x[1], reverse=True)
    iterator = 1
    embed=discord.Embed(color=0x11f80d, title="🏆 Leaderboard 🏆")
    for k, v in leaderboardSorted:
      if iterator <= 10:
        if iterator == 1:
          embed.add_field(name="🥇. {} | {} messages.".format(k, v), value="\u200B", inline=False)
        elif iterator == 2:
          embed.add_field(name="🥈. {} | {} messages.".format(k, v), value="\u200B", inline=False)
        elif iterator == 3:
          embed.add_field(name="🥉. {} | {} messages.".format(k, v), value="\u200B", inline=False)
        else:
          embed.add_field(name="{}. {} | {} messages.".format(iterator, k, v), value="\u200B", inline=False)
      iterator += 1
    await ctx.send(embed=embed)

def setup(client):
  client.add_cog(administratorCommands(client))