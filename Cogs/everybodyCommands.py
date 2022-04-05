import discord
from pymongo import DESCENDING
from asyncio import sleep
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.utils.manage_commands import create_option
from Cogs.settingsCommands import SettingsCommands


class EverybodyCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="help",
        description="Show information about commands",
        guild_ids=[218510314835148802]
    )
    async def help(self, ctx):
        """
        Basic help command, shows information about all the available commands

            Args:
                ctx: Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        embed = discord.Embed(
            color=0x11f80d,
            title="📜 COMMANDS",
            description="**Use `/` or `*` before every command**"
        )
        embed.add_field(
            name="📜 EVERYBODY",
            value="""   
                  **★ `/dc_poke [@user]`**
                  
                  Moves user between voice channels to imitate TeamSpeak3's poke.
                  
                  **★ `/dc_online [@role]`**
                  
                  Shows online users with this role
                  
                  **★ `/dc_bans`**
                  
                  Show banned users on this server
                  
                  **★ `dc_stats_messages [@user]`**
                  
                  Shows how many messages has this Member sent
                  
                  **★ `dc_stats_online [@user]`**
                  
                  Shows for how long member has been online
                  
                  **★ `/top_members`**
                  
                  Show top members of this server based on messages sent
                  """,
            inline=False
        )
        embed.add_field(
            name="📜 MANAGE CHANNELS",
            value="""
                **★ `mute [@user] [Optional(time: min)] [Optional(reason: str)]`**
                
                Mute user for certain amount of time (permanently if no time specified).
                You can provide a reason or leave it blank.
                
                **★ `deaf [@user] [Optional(time: min)] [Optional(reason: str)]`**
                
                Deafen user for certain amount of time (permanently if no time specified).
                You can provide a reason or leave it blank.
                
                **★ `mute_cf [@user]`**
                
                50% chance to mute user for 1 minute, but 50% chance to mute yourself for 3 minutes instead.
                
                """,
            inline=False
        )
        embed.add_field(
            name="📜 MANAGE MESSAGES",
            value="""
                **★ `clear [amount: int]`**
                
                Delete specified amount of messages from channel
                
                **★ `dc_count_messages [#channel] [Optional(@user)]`**
                  
                Count all messages from specific user in specific channel.
                If user isn't specified, it will count all messages in that channel.
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
                  
                  Shows leaderboard of messages in specific channel. 
                  Only available for administrator because of long computing time
                  """,
            inline=False
        )
        embed.set_footer(text=f"Copyrighted by {ctx.guild.owner.name} #{ctx.guild.owner.discriminator}")
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
        """
        Command used to display a list of online members that has selected role

            Args:
                ctx: Context of the command
                role (discord.Role): We want to search for users that has this Discord Role

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
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
    async def poke(self, ctx, member: discord.Member):
        """
        Command used to imitate TeamSpeak3's 'poke' function

            Args:
                ctx: Context of the command
                member (discord.Member): Discord Member that we want to poke

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
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
            if member.voice.channel == ctx.guild.afk_channel:
                await member.move_to(user_channel)
                await sleep(2)
                await member.move_to(ctx.guild.afk_channel)
            else:
                await member.move_to(ctx.guild.afk_channel)
                await sleep(2)
                await member.move_to(user_channel)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="dc_bans",
        description="Show banned users",
        guild_ids=[218510314835148802]
    )
    async def bans(self, ctx):
        """
        Command used to show banned members in Discord's server

            Args:
                ctx: Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        banned_users = await ctx.guild.bans()
        embed = discord.Embed(
          color=0xeb1414,
          title="👮‍♂ BANNED USERS 👮‍♂",
          description="For advanced information, ask administration or moderators."
        )
        audit_logs = {}
        async for entry in ctx.guild.audit_logs(action=discord.AuditLogAction.ban, limit=None):
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
        name="dc_stats_messages",
        description="Show member's message statistics",
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
    async def dc_stats_messages(self, ctx, member: discord.Member):
        """
        Command used to show how many messages the member has sent

            Args:
                ctx: Context of the command
                member (discord.Member): Discord Member from whom we want to collect amount of messages

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'members', ctx=ctx)
        if collection is None:
            return
        if not collection.count_documents({"_id": member.id}):
            await ctx.send(f"{member.mention} is a Bot, or isn't in our Database yet!")
            return
        if collection.find_one({"_id": member.id}):
            messages_sent = collection.find_one({"_id": member.id}, {"messages_sent": 1})
            await ctx.send(f"{member.mention} had written **{messages_sent['messages_sent']}** messages so far!")
        else:
            await ctx.send(f"{member.mention} had not written any messages so far (from 07.02.2022).")

    @cog_ext.cog_slash(
        name="dc_stats_online",
        description="Show member's time online statistics",
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
    async def dc_stats_online(self, ctx, member):
        """
        Command used to show for how long the member has been online

            Args:
                Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'members', ctx=ctx)
        if collection is None:
            return
        if not collection.count_documents({"_id": member.id}):
            await ctx.send(f"{member.mention} is a Bot, or isn't in our Database yet!")
            return
        time_online = collection.find_one({"_id": member.id}, {"time_online": 1})
        if time_online['time_online'].second <= 0 or time_online['time_online'] == 0:
            await ctx.send(f"{member.mention} wasn't online yet")
            return
        elif time_online['time_online'].second > 0 and time_online['time_online'].minute < 1:
            await ctx.send(
                f"{member.mention} was online for **{time_online['time_online'].second}** seconds so far!")
            return
        elif time_online['time_online'].minute > 0 and time_online['time_online'].hour < 1:
            await ctx.send(
                f"{member.mention} was online for **{time_online['time_online'].minute}m "
                f"{time_online['time_online'].second}s** so far!")
            return
        elif time_online['time_online'].hour > 0 and time_online['time_online'].day < 2:
            await ctx.send(
                f"{member.mention} was online for **{time_online['time_online'].hour}h "
                f"{time_online['time_online'].minute}m "
                f"{time_online['time_online'].second}s** so far!")
            return
        elif time_online['time_online'].day >= 2:
            await ctx.send(
                f"{member.mention} was online for **{time_online['time_online'].day}d "
                f"{time_online['time_online'].hour}h "
                f"{time_online['time_online'].minute}m "
                f"{time_online['time_online'].second}s** so far!")
            return

    @cog_ext.cog_slash(
        name="top_members",
        description="Show who's the most active member on this Server!",
        guild_ids=[218510314835148802]
    )
    async def top_members(self, ctx):
        """
        Command used to show top members based on messages sent

            Args:
                ctx: Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return
        file = discord.File(  # creating file to send image along the embed message
            "Media/trophy.png",  # file path to image
            filename="image.png"  # name of the file
        )
        embed = discord.Embed(
            color=0x11f80d,
            description=f'Leaderboard of the most active users in {ctx.guild.name}',
            title="🏆 Leaderboard 🏆"
        )
        embed.set_thumbnail(url="attachment://image.png")
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'new_members', ctx=ctx)
        if collection is None:
            return
        for iterator, user in enumerate(collection.find().sort('messages_sent', DESCENDING).limit(10)):
            member = self.client.get_user(user['_id'])
            if iterator <= 10 and user['messages_sent'] > 0:
                if iterator == 0:
                    embed.add_field(
                        name=f"🥇 {iterator + 1}. {member.display_name}",
                        value=f"{user['messages_sent']} messages",
                        inline=False
                    )
                elif iterator == 1:
                    embed.add_field(
                        name=f"🥈 {iterator + 1}. {member.display_name}",
                        value=f"{user['messages_sent']} messages",
                        inline=False
                    )
                elif iterator == 2:
                    embed.add_field(
                        name=f"🥉 {iterator + 1}. {member.display_name}",
                        value=f"{user['messages_sent']} messages",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=f"{iterator + 1}. {member.display_name}",
                        value=f"{user['messages_sent']} messages",
                        inline=False
                    )
        await ctx.send(file=file, embed=embed)


def setup(client):
    client.add_cog(EverybodyCommands(client))
