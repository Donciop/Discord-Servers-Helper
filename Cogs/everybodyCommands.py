import nextcord
from pymongo import DESCENDING
from asyncio import sleep
from nextcord.ext import commands
from nextcord.abc import GuildChannel
from nextcord import SlashOption
from Cogs.settingsCommands import SettingsCommands, DatabaseManager


class OnlineDropdown(nextcord.ui.Select):
    def __init__(self, interaction: nextcord.Interaction):
        options = []
        for single_role in interaction.guild.roles:
            if single_role.is_bot_managed():
                continue
            options.append(nextcord.SelectOption(label=f'{single_role.name}', value=f'{single_role.id}'))
        super().__init__(placeholder='Choose role...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        members_online = []
        role = interaction.guild.get_role(int(self.values[0]))
        for member in interaction.guild.members:
            if member.get_role(role.id):
                members_online.append(member.display_name)
        await interaction.response.send_message(f'There is {len(members_online)} members online with that role',
                                                ephemeral=True)


class EverybodyCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='help', guild_ids=[218510314835148802])
    async def help(self, interaction: nextcord.Interaction):
        """
        Basic help command, shows information about all the available commands

            Args:
                interaction: (nextcord.Interaction): Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return
        embed = nextcord.Embed(
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
        embed.set_footer(text=f"Copyrighted by {interaction.guild.owner.name} #{interaction.guild.owner.discriminator}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @nextcord.slash_command(name='dc_who_online', guild_ids=[218510314835148802])
    async def dc_who_online(self, interaction: nextcord.Interaction):
        """
        Display a list of online members that has selected role

            Args:
                interaction: (nextcord.Interaction): Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return
        view = nextcord.ui.View()
        view.add_item(OnlineDropdown(interaction))

        await interaction.response.send_message('Pick a role', view=view)

    @nextcord.slash_command(name='dc_poke', guild_ids=[218510314835148802])
    async def dc_poke(self, interaction: nextcord.Interaction,
                      member: nextcord.Member = SlashOption(required=True)):
        """
        Imitate TeamSpeak3's 'poke' function

            Args:
                interaction: (nextcord.Interaction): Context of the command
                member (nextcord.Member): Discord Member that we want to poke

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        if interaction.user == member:
            await interaction.response.send_message(f'You can\'t poke yourself', ephemeral=True)
            return

        if member.bot:
            await interaction.response.send_message(f'Cannot poke Bots', ephemeral=True)
            return

        if str(member.status) == 'offline':
            await interaction.response.send_message(f'User is offline', ephemeral=True)
            return

        if not member.voice:
            await interaction.response.send_message(f'User\'s not in Voice Channel', ephemeral=True)
            return

        await interaction.response.defer()

        if member.voice.channel == interaction.guild.afk_channel:
            await member.move_to(interaction.guild.afk_channel)
            await sleep(1)
            await member.move_to(member.voice.channel)
        else:
            await member.move_to(member.voice.channel)
            await sleep(1)
            await member.move_to(interaction.guild.afk_channel)

        await interaction.followup.send(f"✅ Poke Successful\n"
                                        f"You've poked {member.display_name}")
        return

    @nextcord.slash_command(name='dc_bans', guild_ids=[218510314835148802])
    async def dc_bans(self, interaction: nextcord.Interaction):
        """
        Show banned members in Discord's server

            Args:
                interaction (nextcord.Interaction): Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)

        if not channel_check:
            return

        banned_users = await interaction.guild.bans()

        embed = nextcord.Embed(
          color=0xeb1414,
          title="👮‍♂ BANNED USERS 👮‍♂",
          description="For advanced information, ask administration or moderators."
        )

        audit_logs = {}

        async for entry in interaction.guild.audit_logs(action=nextcord.AuditLogAction.ban):
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

        file = nextcord.File("Media/jail.png", filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")

        await interaction.response.send_message(embed=embed, file=file)

    @nextcord.slash_command(name='dc_count_messages', guild_ids=[218510314835148802])
    async def dc_count_messages(self,
                                interaction: nextcord.Interaction,
                                channel: GuildChannel = nextcord.SlashOption(required=True,
                                                                             channel_types=[nextcord.ChannelType.text]),
                                member: nextcord.Member = nextcord.SlashOption(required=False)):
        """
        Count all messages in specific channel. You can also count all messages from specific user.

            Args:
                interaction (nextcord.Interaction): Context of the command
                channel (nextcord.GuildChannel): Discord Channel in which we want to count messages
                member (:obj:nextcord.Member, optional): Discord Member from whom we want to count messages

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        await interaction.response.defer()

        count = 0
        if member:
            async for msg in channel.history(limit=None):  # iterate over every message in channel's history
                if msg.author == member:
                    count += 1  # increment count for every message
            # display amount of messages in channel
            await interaction.followup.send(f"There were {count} messages in {channel.mention} from {member.mention}")
        else:
            async for _ in channel.history(limit=None):
                count += 1
            await interaction.followup.send(f"There were {count} messages in {channel.mention}")

    @nextcord.slash_command(name='dc_stats_messages', guild_ids=[218510314835148802])
    async def dc_stats_messages(self, interaction: nextcord.Interaction,
                                member: nextcord.Member = SlashOption(required=True)):
        """
        Shows how many messages the member has sent

            Args:
                interaction (nextcord.Interaction): Context of the command
                member (nextcord.Member): Discord Member from whom we want to collect amount of messages

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'new_members')
        if collection is None:
            return

        if not collection.count_documents({"_id": member.id}):
            await interaction.response.send_message(f"{member.mention} is a Bot, or isn't in our Database yet!")
            return

        if collection.find_one({"_id": member.id}):
            messages_sent = collection.find_one({'_id': member.id}, {'messages_sent': 1})
            await interaction.response.send_message(f"{member.mention} had written"
                                                    f" **{messages_sent['messages_sent']}** messages so far!")
        else:
            await interaction.response.send_message(f"{member.mention}"
                                                    f" had not written any messages so far.")

    @nextcord.slash_command(name='dc_stats_online', guild_ids=[218510314835148802])
    async def dc_stats_online(self, interaction: nextcord.Interaction,
                              member: nextcord.Member = SlashOption(required=True)):
        """
        Show for how long the member has been online

            Args:
                interaction (nextcord.Interaction): Context of the command
                member (nextcord.Member): Member that we want to check

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'members')
        if collection is None:
            return

        if not collection.count_documents({"_id": member.id}):
            await interaction.response.send_message(f"{member.mention} is a Bot, or isn't in our Database yet!")
            return

        time_online = collection.find_one({"_id": member.id}, {"time_online": 1})
        if time_online['time_online'].second <= 0 or time_online['time_online'] == 0:
            await interaction.response.send_message(f"{member.mention} wasn't online yet")
            return

        elif time_online['time_online'].second > 0 and time_online['time_online'].minute < 1:
            await interaction.response.send_message(
                f"{member.mention} was online for **{time_online['time_online'].second}** seconds so far!")
            return

        elif time_online['time_online'].minute > 0 and time_online['time_online'].hour < 1:
            await interaction.response.send_message(
                f"{member.mention} was online for **{time_online['time_online'].minute}m "
                f"{time_online['time_online'].second}s** so far!")
            return

        elif time_online['time_online'].hour > 0 and time_online['time_online'].day < 2:
            await interaction.response.send_message(
                f"{member.mention} was online for **{time_online['time_online'].hour}h "
                f"{time_online['time_online'].minute}m "
                f"{time_online['time_online'].second}s** so far!")
            return

        elif time_online['time_online'].day >= 2:
            await interaction.response.send_message(
                f"{member.mention} was online for **{time_online['time_online'].day}d "
                f"{time_online['time_online'].hour}h "
                f"{time_online['time_online'].minute}m "
                f"{time_online['time_online'].second}s** so far!")
            return

    @nextcord.slash_command(name='dc_msg_leaderboard', guild_ids=[218510314835148802])
    async def dc_msg_leaderboard(self, interaction: nextcord.Interaction,
                                 channel: GuildChannel = nextcord.SlashOption(required=True,
                                                                              channel_types=[
                                                                                  nextcord.ChannelType.text])):
        """
        Leaderboard of sent messages in specific channel

            Args:
                interaction (nextcord.Interaction): Context of the command
                channel (nextcord.TextChannel): Discord Text Channel in which we want to count messages

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        await interaction.response.defer()

        leaderboard_not_sorted = {}

        async for msg in channel.history(limit=None):
            if str(msg.author.name) in leaderboard_not_sorted:
                leaderboard_not_sorted[str(msg.author.name)] += 1
            else:
                leaderboard_not_sorted[str(msg.author.name)] = 1

        leaderboard_sorted = sorted(leaderboard_not_sorted.items(), key=lambda x: x[1], reverse=True)
        iterator = 1
        file = nextcord.File(  # creating file to send image along the embed message
            "Media/trophy.png",  # file path to image
            filename="image.png"  # name of the file
        )
        embed = nextcord.Embed(
            color=0x11f80d,
            description=f'Leaderboard of the most active users in {channel.mention}',
            title="🏆 Leaderboard 🏆"
        )
        embed.set_thumbnail(url="attachment://image.png")
        for k, v in leaderboard_sorted:
            if iterator <= 10 and v > 0:
                if iterator == 1:
                    embed.add_field(
                        name=f"🥇 {iterator}. {k}",
                        value=f"{v} messages",
                        inline=False
                    )
                elif iterator == 2:
                    embed.add_field(
                        name=f"🥈 {iterator}. {k}",
                        value=f"{v} messages",
                        inline=False
                    )
                elif iterator == 3:
                    embed.add_field(
                        name=f"🥉 {iterator}. {k}",
                        value=f"{v} messages",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=f"{iterator}. {k}",
                        value=f"{v} messages",
                        inline=False
                    )
            iterator += 1
        await interaction.followup.send(file=file, embed=embed)

    @nextcord.slash_command(name='dc_global_msg_leaderboard', guild_ids=[218510314835148802])
    async def dc_global_msg_leaderboard(self, interaction: nextcord.Interaction):
        """
        Show global leaderboard based on messages sent

            Args:
                interaction: (nextcord.Interaction): Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'new_members')
        if collection is None:
            return

        file = nextcord.File(  # creating file to send image along the embed message
            "Media/trophy.png",  # file path to image
            filename="image.png"  # name of the file
        )

        embed = nextcord.Embed(
            color=0x11f80d,
            description=f'Leaderboard of the most active users in {interaction.guild.name}',
            title="🏆 Leaderboard 🏆"
        )

        embed.set_thumbnail(url="attachment://image.png")

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
        await interaction.response.send_message(file=file, embed=embed)


def setup(client):
    client.add_cog(EverybodyCommands(client))
