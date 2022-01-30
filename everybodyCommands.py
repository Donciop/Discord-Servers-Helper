import discord
import asyncio
import random
import json
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
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
        channel_check_cog = self.client.get_cog("TftCommands")
        channel_check = False
        if channel_check_cog is not None:
            channel_check = await channel_check_cog.channel_check(ctx, ctx.channel.id)
        if not channel_check:
            return
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
                  Count all messages from specific user in channel where this command is sent.
                  If user isn't specified, it will count messages of person who send the command
                  **★ `poke [@user]`**
                  Moves user between voice channels to poke him.
                  **★ `online [@role]`**
                  Shows online users with this role
                  **★ `keyword [word: str]`**
                  Look for a specific word or words in last 1k messages and get jump URLs to them.
                  Keyword has to be longer than 5 letters.
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
        channel_check_cog = self.client.get_cog("TftCommands")
        channel_check = False
        if channel_check_cog is not None:
            channel_check = await channel_check_cog.channel_check(ctx, ctx.channel.id)
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
        channel_check_cog = self.client.get_cog("TftCommands")
        channel_check = False
        if channel_check_cog is not None:
            channel_check = await channel_check_cog.channel_check(ctx, ctx.channel.id)
        if not channel_check:
            return
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

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def wordle(self, ctx):
        """
        Command used to start the actual game of "Wordsy".
        """
        # getting server's information about dedicated channel for the bot
        with open("JsonData/guild_configs.json") as guild_configs_file:
            guild_config = guild_configs_file.read()
            guild_config_dict = json.loads(guild_config)
            guild_configs_file.close()

        # checking if we're getting response in right channel and from right person
        def check(message: discord.Message):
            # if bot channel's id exists in database, we check if the response is in that channel
            if guild_config_dict[str(ctx.guild.id)]:
                return message.channel.id == guild_config_dict[str(ctx.guild.id)] and message.author == ctx.author
            else:
                # if channel's not in database, we just accept it in any channel
                return message.channel == ctx.channel and message.author == ctx.author

        # initialize lists that will be used later to store information
        letters = ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
                   "a", "s", "d", "f", "g", "h", "j", "k", "l",
                   "z", "x", "c", "v", "b", "n", "m"]
        used_words = ['', '', '', '', '', '']
        final_string = [
            [':black_square_button:', ':black_square_button:', ':black_square_button:', ':black_square_button:',
             ':black_square_button:'],
            [':black_square_button:', ':black_square_button:', ':black_square_button:', ':black_square_button:',
             ':black_square_button:'],
            [':black_square_button:', ':black_square_button:', ':black_square_button:', ':black_square_button:',
             ':black_square_button:'],
            [':black_square_button:', ':black_square_button:', ':black_square_button:', ':black_square_button:',
             ':black_square_button:'],
            [':black_square_button:', ':black_square_button:', ':black_square_button:', ':black_square_button:',
             ':black_square_button:'],
            [':black_square_button:', ':black_square_button:', ':black_square_button:', ':black_square_button:',
             ':black_square_button:']
        ]
        winning_string = [':green_square:', ':green_square:', ':green_square:', ':green_square:', ':green_square:']
        with open('JsonData/words_dictionary.json') as wordle_file:  # getting our dictionary from .json file
            wordle_file_dict = wordle_file.read()
            wordle = json.loads(wordle_file_dict)
            wordle_file.close()
        wordle_word = random.choice(list(wordle.keys()))  # choosing random word from the dictionary
        iterator = 1
        while True:
            if iterator == 7:  # check if we still have tries
                await ctx.send(f"You didn't make it :( The word was: {wordle_word}")
                return
            if guild_config_dict[str(ctx.guild.id)] != ctx.channel.id:
                wordsy_ch = client.get_channel(int(guild_config_dict[str(ctx.guild.id)]))
                await ctx.send(f"Please use Discord Wordsy in {wordsy_ch.mention}")
                return
            await ctx.send(f"Guess the word! (5 letters) {iterator} / 6 tries")
            # wait for user's response and check channel and author of the command
            msg = await client.wait_for('message', check=check)
            if any(char.isdigit() for char in msg.content):  # check if passed string doesn't have any digits in it
                await ctx.send("Word cannot contain numbers!")
                continue
            if len(msg.content) < 5:  # check if passed string have correct length
                await ctx.send(f"Word's too short ({len(msg.content)} / 5 letters)")
                continue
            if len(msg.content) > 5:
                await ctx.send(f"Word's too long ({len(msg.content)} / 5 letters)")
                continue
            if msg.content in used_words:  # check if the word has been used before
                await ctx.send("You've already used that word!")
                continue
            typed_word = str(msg.content).lower()  # make sure we're working on lowercase letters
            if typed_word not in wordle:  # check if word from user's response is in dictionary
                await ctx.send("Word's not in dictionary")
                continue
            used_words[iterator - 1] = str(msg.content)  # store passed word in list to print it later
            for index, typed_letter in enumerate(typed_word):  # iterate over every letter in passed word
                # if the letter's and it's position is correct, we assign green square to this position
                if typed_letter == wordle_word[index]:
                    final_string[iterator - 1][index] = ':green_square:'
                    try:
                        letters[letters.index(typed_letter)] = f'**{typed_letter}**'  # here we bold the correct letter
                    except:
                        continue
                # if the letter's correct but in wrong position, we assign yellow square to this position
                elif typed_letter in wordle_word:
                    final_string[iterator - 1][index] = ':yellow_square:'
                    try:
                        letters[letters.index(typed_letter)] = f'**{typed_letter}**'
                    except:
                        continue
                # if the letter's wrong, we assign black square to this position
                else:
                    final_string[iterator - 1][index] = ':black_large_square:'
                    try:
                        letters[letters.index(typed_letter)] = f' '  # here we remove the letter from the keyboard
                    except:
                        continue
            # here we uppercase the letters to make them more readable
            final_letters = letters.copy()
            for lower_letter in final_letters:
                final_letters[final_letters.index(lower_letter)] = lower_letter.upper()
            # the final message that is sent every iteration of the while loop contains every square and whole keyboard
            await ctx.send(
                f"{final_string[0][0]} {final_string[0][1]} {final_string[0][2]} {final_string[0][3]} {final_string[0][4]}   {used_words[0].upper()}\n\n"
                f"{final_string[1][0]} {final_string[1][1]} {final_string[1][2]} {final_string[1][3]} {final_string[1][4]}   {used_words[1].upper()}\n\n"
                f"{final_string[2][0]} {final_string[2][1]} {final_string[2][2]} {final_string[2][3]} {final_string[2][4]}   {used_words[2].upper()}\n\n"
                f"{final_string[3][0]} {final_string[3][1]} {final_string[3][2]} {final_string[3][3]} {final_string[3][4]}   {used_words[3].upper()}\n\n"
                f"{final_string[4][0]} {final_string[4][1]} {final_string[4][2]} {final_string[4][3]} {final_string[4][4]}   {used_words[4].upper()}\n\n"
                f"{final_string[5][0]} {final_string[5][1]} {final_string[5][2]} {final_string[5][3]} {final_string[5][4]}   {used_words[5].upper()}\n\n"
                f"{final_letters[0]} {final_letters[1]} {final_letters[2]} {final_letters[3]} {final_letters[4]} {final_letters[5]} {final_letters[6]} {final_letters[7]} {final_letters[8]} {final_letters[9]}\n"
                f"    {final_letters[10]} {final_letters[11]} {final_letters[12]} {final_letters[13]} {final_letters[14]} {final_letters[15]} {final_letters[16]} {final_letters[17]} {final_letters[18]}\n"
                f"       {final_letters[19]} {final_letters[20]} {final_letters[21]} {final_letters[22]} {final_letters[23]} {final_letters[24]} {final_letters[25]}"
            )
            if winning_string in final_string:  # winning condition
                await ctx.send(f"You won! The word is: {wordle_word}")
                return
            iterator += 1


def setup(client):
    client.add_cog(EverybodyCommands(client))
