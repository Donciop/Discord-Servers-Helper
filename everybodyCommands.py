import discord
import asyncio
from discord.ext import commands
from discord_slash import cog_ext, context  # for slash commands
from discord_slash.utils.manage_commands import create_option
from main import client


class EverybodyCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.newsChannel = client.get_channel(748120165001986128)
        self.botChannel = client.get_channel(888056072538042428)
        self.testChannel = client.get_channel(902710519646015498)
        self.owner = client.get_user(198436287848382464)
        self.guild = client.get_guild(218510314835148802)

    @cog_ext.cog_slash(
        name="help",
        description="Show information about commands",
        guild_ids=[218510314835148802]
    )
    async def help(self, ctx):
        if ctx.channel.id == self.botChannel.id or ctx.channel.id == self.newsChannel.id or ctx.channel.id == self.testChannel.id:
            embed = discord.Embed(
                color=0x11f80d,
                title="📜 COMMANDS"
            )
            embed.add_field(
                name="**Use `*` before every command**",
                value=f"Most of the commands have to be used in -> {self.botChannel.mention}",
                inline=False
            )
            embed.add_field(
                name="📜 EVERYBODY",
                value="""
                      **★ `msgCountMember [Optional(@user)]`**
                      Count all messages from specific user in channel where this command is sent. If user isn't specified, it will count messages of person who send the command
                      **★ `poke [@user]`**
                      Moves user between voice channels to poke him.
                      **★ `online [@role]`**
                      Shows online users with this role
                      **★ `keyword [word: str]`**
                      Look for a specific word or words in last 1k messages and get jump URL's to them. Keyword has to be longer than 5 letters.
                      **★ `bans`**
                      Show banned users on this server
                      """,
                inline=False
            )
            embed.add_field(
                name="📜 MANAGE CHANNELS",
                value="""
                    **★ `mute [@user] [Optional(time: min)] [Optional(reason: str)]`**
                    Mute user for certain amount of time (permanently if no time specified). You can provide a reason or leave it blank.
                    **★ `deaf [@user] [Optional(time: min)] [Optional(reason: str)]`**
                    Deafen user for certain amount of time (permanently if no time specified). You can provide a reason or leave it blank.
                    **★ `mutecf [@user]`**
                    50% chance to mute user for 1 minute, but 50% chance to mute yourself for 3 minutes instead.
                    """,
                inline=False
            )
            embed.add_field(
                name="📜 MANAGE MESSAGES",
                value="""
                    **★ `clear [amount: int]`**
                    Delete specified amount of messages from channel
                    **★ `msgCount [Optional(#channel)]`**
                    Count messages in specific channel or in current channel if not specified.
                    """,
                inline=False
            )
            embed.add_field(
                name="📜 MANAGE USERS",
                value="""
                      **★ `unban [@user]`**
                      Unban specific user
                      """,
                inline=False
            )
            embed.add_field(
                name="📜 ADMINISTRATOR",
                value="""
                      **★ `top`**
                      Shows leaderboard of messages in specific channel, only available for administrator because of long computing time
                      """,
                inline=False
            )
            embed.add_field(
                name="📜 ROLES",
                value=f"Get yourself a role or remove it here -> {self.newsChannel.mention}",
                inline=False
            )
            embed.set_footer(text=f"Copyrighted by {self.owner.name} #{self.owner.discriminator}")
        else:
            embed=discord.Embed(color=0xeb1414)
            embed.set_author(
              name=ctx.author.display_name,
              icon_url=ctx.author.avatar_url
            )
            embed.add_field(
              name="🛑 Help Failed",
              value=f"You can't post commands outside of {self.botChannel.mention}",
              inline=False
            )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="dc_online",
        description="Display a list of online members of selected role",
        guild_ids=[218510314835148802],
        options=[
            create_option(
                name="role",
                description="Select player's role",
                option_type=8,
                required=True
            )
        ]
    )
    async def online(self, ctx, role):
        members = role.members
        empty = True
        embed = discord.Embed(color=0x11f80d)
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar_url
        )
        if not role:
            embed.add_field(
                name="🛑 Online Failed",
                value="You have to specify a role"
            )
        for member in members:
            if str(member.status) == "online":
                embed.add_field(
                    name="✅ Online",
                    value=f"★ {member.display_name}",
                    inline=False
                )
                empty = False
        if empty:
            embed = discord.Embed(color=0xeb1414)
            embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar_url
            )
            embed.add_field(
                name="💤 Offline",
                value="Everybody's offline :(",
                inline=False
            )
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="dc_poke",
        description="Poke a member!",
        guild_ids=[218510314835148802],
        options=[
            create_option(
                name="member",
                description="Select member!",
                option_type=6,
                required=True
            )
        ]
    )
    async def poke(self, ctx, member):
        await ctx.defer()
        embed = discord.Embed(color=0x11f80d)
        embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar_url
        )
        if ctx.author == member:
            embed = discord.Embed(color=0xeb1414)
            embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar_url
            )
            embed.add_field(
                name="🛑 Poke Failed",
                value="You can't poke yourself"
            )
        else:
            embed.add_field(
                name="✅ Poke Successful",
                value=f"You've poked {member.display_name}",
                inline=False
            )
            user_channel = member.voice.channel
            if member.voice.channel == self.guild.afk_channel:
                await member.move_to(user_channel)
                await asyncio.sleep(2)
                await member.move_to(self.guild.afk_channel)
            else:
                await member.move_to(self.guild.afk_channel)
                await asyncio.sleep(2)
                await member.move_to(user_channel)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="dc_count_messages",
        description="Count messages from specific member in that channel!",
        guild_ids=[218510314835148802],
        options=[
            create_option(
              name="member",
              description="Select member!",
              option_type=6,
              required=True
            )
        ]
    )
    async def msg_count_member(self, ctx, member):
        await ctx.defer()
        counter = 0
        async for msg in ctx.channel.history(limit=None):
            if msg.author == member:
                counter += 1
        await ctx.send(f"User {member.display_name} had written {str(counter)} messages in {ctx.channel.mention}")

    @cog_ext.cog_slash(
      name="dc_bans",
      description="Show banned users",
      guild_ids=[218510314835148802]
    )
    async def bans(self, ctx):
        banned_users = await self.guild.bans()
        embed = discord.Embed(
          color=0xeb1414,
          title="👮‍♂ BANNED USERS 👮‍♂",
          description="For advanced information, ask administration or moderators."
        )
        audit_logs = {}
        async for entry in self.guild.audit_logs(action=discord.AuditLogAction.ban, limit=None):
            audit_logs[entry.target.name] = entry.user.name
        for banEntry in banned_users:
            if str(banEntry.user.name) in audit_logs:
                embed.add_field(
                  name=f"{banEntry.user.name} #{banEntry.user.discriminator}",
                  value=f"banned by {audit_logs[str(banEntry.user.name)]}",
                  inline=False
                )
            else:
                embed.add_field(
                  name=f"{banEntry.user.name} #{banEntry.user.discriminator}",
                  value="\u200B",
                  inline=False
                )
        file = discord.File("Media/jail.png", filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        await ctx.send(embed=embed, file=file)

    @cog_ext.cog_slash(
        name="dc_search",
        description="Search channel for specific message",
        guild_ids=[218510314835148802],
        options=[
            create_option(
              name="keyword",
              description="Type in keywords!",
              option_type=3,
              required=True
            )
        ]
    )
    async def keyword(self, ctx, keyword):
        await ctx.defer()
        count = 0
        if len(keyword) >= 5:
            messages = await ctx.channel.history(limit=1000).flatten()
            for msg in messages:
                if keyword in msg.content:
                    count += 1
                    await ctx.send(msg.jump_url)
        else:
            await ctx.send("A keyword should be longer or equal to 5 letters")
            return
        if count < 0:
            await ctx.send("Keywords not found")
            return
        else:
            await ctx.send(f"Found {count} messages!")
            return


def setup(client):
    client.add_cog(EverybodyCommands(client))
