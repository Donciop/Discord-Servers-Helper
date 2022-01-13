from discord.ext import commands

class manageUsersCommands(commands.Cog):
  def __init__(self, client):
    self.client = client

@commands.command()
@commands.has_permissions(ban_members = True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def unban(self, ctx,*,member):
  banned_users = await ctx.guild.bans()
  member_name, member_discriminator = member.split("#")
  for ban_entry in banned_users:
    user = ban_entry.user
    if (user.name, user.discriminator) == (member_name, member_discriminator):
      await ctx.guild.unban(user)
      await ctx.send(f'**{user}** has been unbanned!')

def setup(client):
  client.add_cog(manageUsersCommands(client))