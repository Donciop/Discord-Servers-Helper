import discord  # main packages
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.utils.manage_commands import create_option
from tinydb import TinyDB, Query  # simple document based database
from riotwatcher import TftWatcher  # RIOT API wrapper
from main import client  # utility packages
import os
import asyncio
import json  # for storage


class TftCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """ Event handler. That event is called when bot becomes online. Used mainly to initialize variables. """
        self.leagueChannel = client.get_channel(910557144573673522)  # for channel check, to make sure commands are used in right channel
        self.penguFilepath = "Media/Pengu_TFT.png"  # filepaths for files send with Discord embeds
        self.tftIconFilepath = "Media/Teamfight_Tactics_icon.png"
        self.tftEmoji = "<:TFT:912917249923375114>"  # reference to custom Discord emoji
        self.region = 'eun1'  # used in Riotwatcher to determine which region we're looking for
        self.watcher = TftWatcher(os.getenv('APIKEYTFT'))  # RIOT API KEY
        self.purgeSeconds = 5
        self.db = TinyDB('JsonData/db.json')  # initialize TinyDB database

    @commands.command()
    async def rank_check(self, summoner_rank):
        """
        Function that checks player's rank and return specific information for further usage.

        :param summoner_rank: - dictionary from Riotwatcher containing information about player's ranking.
        :return tier_emoji: custom emoji based on player's ranking.
        :return rank: calculated rating for local leaderboard.
        """
        with open("JsonData/rankDict.json") as rank_dict:  # get data about custom emojis from external file
            rank_dict_json = rank_dict.read()
            rank_dict = json.loads(rank_dict_json)
        tier_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
        rank_list = ["IV", "III", "II", "I"]
        q_type = 0
        rank = 0
        if summoner_rank[0]['queueType'] == 'RANKED_TFT_TURBO':  # check if we're getting data from desired queue type
            q_type = 1
        for tier in tier_list:  # iterate over every tier until we find player's tier
            if summoner_rank[q_type]['tier'] != tier:
                rank += 400
            else:
                tier_emoji = rank_dict[tier]
                break
        for localRank in rank_list:  # iterate over every rank until we find player's rank
            if summoner_rank[q_type]['rank'] != localRank:
                rank += 100
            else:
                break
        rank += summoner_rank[q_type]['leaguePoints']  # calculate final rating for leaderboard
        return tier_emoji, rank

    @commands.command()
    async def channel_check(self, channel):
        """
        Function used to check if we're sending commands in right channel.

        :param channel: discord channel where message was sent
        :return channel_check: boolean, means we're in right channel if True
        """
        bot_channel = client.get_channel(888056072538042428)  # variables that store channels where we can send commands
        test_channel = client.get_channel(902710519646015498)
        if channel != bot_channel.id and channel != test_channel.id and channel != self.leagueChannel.id:  # check if we're sending command in right channel
            channel_check = False  # False if we're in wrong channel
            our_channel = client.get_channel(channel)
            await our_channel.send(f"Please, use bot commands in {self.leagueChannel.mention} channel to prevent spam")  # sends specific message when we're in wrong command
            await asyncio.sleep(self.purgeSeconds)  # waits specific amount of time
            await our_channel.purge(limit=2)  # deletes message after specific amount of time
        else:
            channel_check = True  # True if we're in right channel
        return channel_check

    @cog_ext.cog_slash(  # slash command decorator
        name="tft_rank",  # name that will be displayed in Discord
        description="Check a specific player's Teamfight Tactics rank",  # description of the command
        guild_ids=[218510314835148802],  # list of server (guilds) id's that have access to this slash command
        options=[
            create_option(  # parameters in slash command
                name="nickname",  # name of the variable
                description="Type in player's nickname",  # description of the parameter
                option_type=3,  # option_type refers to type of the variable ( 3 - STRING )
                required=True  # this parameter is required
            )
        ]
    )
    async def tft_rank(self, ctx, nickname: str):
        """
        Command used to check player's rank in Teamfight Tactics.

        :param ctx: passing context of the command
        :param nickname: nickname of the player we want to find
        """
        channel_check = await self.channel_check(ctx.channel.id)  # check if we're sending command in right channel
        if not channel_check:
            return
        summoner = self.watcher.summoner.by_name(self.region, nickname)  # access data about specific player from RIOT API
        if not summoner:  # check if the player actually exists
            await ctx.send(f"Can't find **{nickname}** on EUNE server.")
            return  # return if player's not found
        summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])  # acces data about player's rank
        if not summoner_tft_stats:  # check if player has rank on Teamfight Tactics
            await ctx.send(f"Player **{nickname}** is unranked on TFT")
            return  # return if player's unranked
        title_nickname = nickname.lower()  # nickname operations for accessing the lolchess.gg website
        title_nickname = title_nickname.replace(" ", "")
        embed = discord.Embed(  # styling Discord embed message
          color=0x11f80d,  # color of the embed message
          title=f"🎲 Teamfight Tactics {nickname}'s Rank 🎲",  # title of the embed message
          description="Click the title for advanced information",  # description of the embed message
          url=f"https://lolchess.gg/profile/eune/{title_nickname}"  # URL that leads to player's account on lolchess.gg for further analysis if needed
        )
        file = discord.File(  # creating file to send image along the embed message
            self.penguFilepath,  # file path to image
            filename="image.png"  # name of the file
        )
        embed.set_thumbnail(url="attachment://image.png")  # setting emebed's thumbnail
        tier_emoji, rank = await self.rank_check(summoner_tft_stats)  # get player's rank and rating for leaderboard
        q_type = 0
        if summoner_tft_stats[0]['queueType'] == 'RANKED_TFT_TURBO':  # check if we're processing right queue type
            q_type = 1
        embed.add_field(  # adding fields to embed message that contains rank , winrate, amounts of matches played and league points owned
          name="RANKED",
          value=f"""
        {tier_emoji} {summoner_tft_stats[q_type]['tier']} {summoner_tft_stats[q_type]['rank']} | {summoner_tft_stats[q_type]['leaguePoints']} LP
        **{round((summoner_tft_stats[q_type]['wins'] / (summoner_tft_stats[q_type]['wins'] + summoner_tft_stats[q_type]['losses'])) * 100)}%** top 1 ratio ({summoner_tft_stats[q_type]['wins'] + summoner_tft_stats[q_type]['losses']} Matches)
        """)
        await ctx.send(file=file, embed=embed)

    @cog_ext.cog_slash(
        name="tft_add_player",
        description="Add a Teamfight Tactic player to the leaderboard",
        guild_ids=[218510314835148802],
        options=[
            create_option(
                name="nickname",
                description="Type in player's nickname",
                option_type=3,
                required=True
            )
        ]
    )
    async def tft_add_player(self, ctx, nickname: str):
        """
        Command used to add players to the database for further usage in leaderboard.

        :param ctx: passing context of the command
        :param nickname: nickname of the player we want to add
        """
        channel_check = await self.channel_check(ctx.channel.id)
        if not channel_check:
            return
        summoner = self.watcher.summoner.by_name(self.region, nickname)
        if not summoner:
            await ctx.send(f"Can't find **{nickname}** on EUNE server.")
            return
        summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])
        if not summoner_tft_stats:
            await ctx.send(f"Player **{nickname}** is unranked")
            return
        q_type = 0
        if summoner_tft_stats[0]['queueType'] == 'RANKED_TFT_TURBO':
            q_type = 1
        if self.db.search(Query().nickname == nickname):  # searching database to check if player's already exists
            await ctx.send(f"Player **{nickname}** already exists in database")
            return  # return if player's already in the database
        else:
            tier_emoji, ranking = await self.rank_check(summoner_tft_stats)
            self.db.insert({'nickname': nickname, })  # sql insert player into database
            self.db.update_multiple([  # after inserting we update his statistic, including rank, tier, league points etc.
              ({'matchesPlayed': (summoner_tft_stats[q_type]['wins']+summoner_tft_stats[q_type]['losses'])}, Query().nickname == nickname),
              ({'rank': summoner_tft_stats[q_type]['rank']}, Query().nickname == nickname),
              ({'tier': summoner_tft_stats[q_type]['tier']}, Query().nickname == nickname),
              ({'leaguePoints': summoner_tft_stats[q_type]['leaguePoints']}, Query().nickname == nickname),
              ({'tierEmoji': tier_emoji}, Query().nickname == nickname),
              ({'wins': summoner_tft_stats[q_type]['wins']}, Query().nickname == nickname)
            ])
            await ctx.send(f"Added **{nickname}** to the database")

    @cog_ext.cog_slash(
        name="tft_remove_player",
        description="Removes a Teamfight Tactics player from the leaderboard",
        guild_ids=[218510314835148802],
        options=[
            create_option(
                name="nickname",
                description="Type in player's nickname",
                option_type=3,
                required=True
            )
        ]
    )
    async def tft_remove_player(self, ctx, nickname: str):
        """
        Command used to remove players from database on demand.

        :param ctx: passing context of the command
        :param nickname: nickname of the player we want to add
        """
        channel_check = await self.channel_check(ctx.channel.id)
        if not channel_check:
            return
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You don't have permission to delete users from database, ask administrators or moderators")
            return
        if self.db.search(Query().nickname == nickname):
            self.db.remove(Query().nickname == nickname)  # removing player from database
            await ctx.send(f"You have deleted **{nickname}** from database")
        else:
            await ctx.send(f"Can't find **{nickname}** in database")

    @cog_ext.cog_slash(
        name="tft_ranking",
        description="Show server's Teamfight Tactics leaderboard",
        guild_ids=[218510314835148802]
    )
    async def tft_ranking(self, ctx):
        """
        Command used to show local leaderboard of Teamfight Tactics player that are in our database.

        :param ctx: passing context of the command
        """
        channel_check = await self.channel_check(ctx.channel.id)
        if not channel_check:
            return
        embed = discord.Embed(
          color=0x11f80d,
          title="🏆 Teamfight Tactics Leaderboard 🏆",
          description="For advanced info use *tftStats or *tftRank"
        )
        file = discord.File(self.penguFilepath, filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        leaderboard_not_sorted = {}  # empty dictionary for collecting required data
        await ctx.defer()  # deffering a command due to long computing time and timeouts from slash commands
        for record in self.db:  # iterate over every record in database to access player's information
            q_type = 0
            try:
                summoner = self.watcher.summoner.by_name(self.region, record['nickname'])
            except:
                continue
            summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])
            if summoner_tft_stats[0]['queueType'] == 'RANKED_TFT_TURBO':
                q_type = 1
            tier_emoji, ranking = await self.rank_check(summoner_tft_stats)
            self.db.update_multiple([  # update database from RIOT API information to get up to date statistics
              ({'matchesPlayed': (summoner_tft_stats[q_type]['wins']+summoner_tft_stats[q_type]['losses'])}, Query().nickname == record['nickname']),
              ({'rank': summoner_tft_stats[q_type]['rank']}, Query().nickname == record['nickname']),
              ({'tier': summoner_tft_stats[q_type]['tier']}, Query().nickname == record['nickname']),
              ({'leaguePoints': summoner_tft_stats[q_type]['leaguePoints']}, Query().nickname == record['nickname']),
              ({'tierEmoji': tier_emoji}, Query().nickname == record['nickname']),
              ({'wins': summoner_tft_stats[q_type]['wins']}, Query().nickname == record['nickname'])
            ])
            leaderboard_not_sorted[f"{record['nickname']}"] = [ranking]  # adding local rank to every player for future leaderboard
        leaderboard_sorted = sorted(  # sorting dictionary by rank
          leaderboard_not_sorted.items(),
          key=lambda x: x[1],
          reverse=True
        )
        iterator = 1
        for player in leaderboard_sorted:  # iterate over every player in leaderboard to give him right place
            player_stats = self.db.search(Query().nickname == player[0])
            if iterator == 1:  # first, second and third place have custom emoji besides their nickname on leaderboard
                rank_emoji = ":first_place:"
            elif iterator == 2:
                rank_emoji = ":second_place:"
            elif iterator == 3:
                rank_emoji = ":third_place:"
            else:
                rank_emoji = None
            if rank_emoji is not None:
                embed.add_field(  # adding fields to embed message with player's statistics
                  name=f"{rank_emoji} {player_stats[0]['tierEmoji']} {player_stats[0]['nickname']} | {player_stats[0]['tier']} {player_stats[0]['rank']} ({player_stats[0]['leaguePoints']} LP)",
                  value=f"**{round((player_stats[0]['wins'] / player_stats[0]['matchesPlayed'])*100)}%** win ratio with {player_stats[0]['matchesPlayed']} matches played",
                  inline=False
                )
            else:
                embed.add_field(
                  name=f"{player_stats[0]['tierEmoji']} {player_stats[0]['nickname']} | {player_stats[0]['tier']} {player_stats[0]['rank']} ({player_stats[0]['leaguePoints']} LP)",
                  value=f"**{round((player_stats[0]['wins'] / player_stats[0]['matchesPlayed'])*100)}%** win ratio with {player_stats[0]['matchesPlayed']} matches played",
                  inline=False
                )
            iterator += 1
        await ctx.send(embed=embed, file=file)

    @cog_ext.cog_slash(
        name="tft_stats",
        description="Show user's Teamfight Tactics statistics",
        guild_ids=[218510314835148802],
        options=[
            create_option(
                name="nickname",
                description="Type in nickname!",
                option_type=3,
                required=True
            ),
            create_option(
                name="number_of_matches",
                description="Type in amount of games!",
                option_type=4,  # option_type refers to type of expected variable (4 - INTEGER)
                required=True
            )
        ]
    )
    async def tft_stats(self, ctx, nickname: str, number_of_matches: int):
        channel_check = await self.channel_check(ctx.channel.id)
        if not channel_check:
            return
        if number_of_matches >= 500 or number_of_matches <= 0:  # due to API limitations, we can't collecta data from more than 500 matches
            await ctx.send(f"Wrong number of matches! Try between 0 - 500")
            return  # return if wrong number of matches was specified
        summoner = self.watcher.summoner.by_name(self.region, nickname)
        if not summoner:
            await ctx.send(f"Can't find summoner **{nickname}**")
            return
        summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])
        count = number_of_matches
        match_list = self.watcher.match.by_puuid("europe", summoner['puuid'], count)  # access player's match history in form of list of match ids
        if not match_list:  # check if player played at least 1 match
            await ctx.send(f"**{nickname}** didn't played any Teamfight Tactics games")
            return  # return if player has no matches of Teamfight Tactics on their account

        # Getting data from .json files that are used to store information about Teamfight Tactics characters etc.

        with open("JsonData/allStats.json") as allStatsFile, open("JsonData/tftComps.json") as tftCompsFile:
            all_stats_json = allStatsFile.read()
            all_stats = json.loads(all_stats_json)
            comps_json = tftCompsFile.read()
            comps = json.loads(comps_json)
        await ctx.defer()
        for match in match_list:  # iterate over every match in match list
            match_detail = self.watcher.match.by_id("europe", match)  # getting match details for further analysis
            if match_detail['info']['tft_set_number'] != 6:  # check if we're getting matches only from current "set" in Teamfight Tactics
                break  # break if we don't find any more matches from set nr. 6
            for participant in match_detail['info']['participants']:  # iterave over every participant in match to find our player
                if participant['puuid'] == summoner['puuid']:  # check if player's 'puuid' matches participant 'puuid' to ensure we're collecting our player's data
                    for trait in participant['traits']:  # iterave over every 'trait' that player has on their board in Teamfight Tactics
                        if trait['tier_current'] > 0:  # if trait is active, we collect that to our dictionary for further analysis
                            comps[str(trait['name'])][0] += 1
                            if participant['placement'] <= 4:  # check if player was above 4th place to determine his performance with traits that he's using
                                comps[str(trait['name'])][1] += 1
                    if match_detail['info']['queue_id'] == 1090:  # check from what type of queue the match we're analyzing right now is
                        q_type = 'Normal'  # assing q_type variable based on queue type of the match
                    elif match_detail['info']['queue_id'] == 1100:
                        q_type = 'Ranked'
                    elif match_detail['info']['queue_id'] == 1150:
                        q_type = 'Double Up'
                    else:
                        q_type = 'Hyper Roll'
                    all_stats[str(q_type)]['hasPlayed'] = True  # boolean that tells us that player has played that queue type at least once
                    all_stats[str(q_type)]['played'] += 1  # increment number of matches played
                    all_stats[str(q_type)]['placements'] += participant['placement']  # information about placement in that match for further analysis
                    if participant['placement'] <= 4:
                        all_stats[str(q_type)]['top4'] += 1
                        if participant['placement'] == 1:
                            all_stats[str(q_type)]['winrate'] += 1
        comps_sorted = sorted(  # sort dictionary based on amount of times a trait has been played
          comps.items(),
          key=lambda x: x[1],
          reverse=True
        )
        title_nickname = nickname.lower()
        title_nickname = title_nickname.replace(" ", "")
        embed = discord.Embed(
          color=0x11f80d,
          title=f"{self.tftEmoji} Teamfight Tactics {nickname}'s Stats ",
          description="Click the title for advanced information on LolChess",
          url=f"https://lolchess.gg/profile/eune/{title_nickname}"
        )
        file = discord.File(self.penguFilepath, filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        if summoner_tft_stats:
            tier_emoji, ranking = await self.rank_check(summoner_tft_stats)
            embed.add_field(
              name="RANK",
              value=f"{tier_emoji} {summoner_tft_stats[0]['tier']} {summoner_tft_stats[0]['rank']} | {summoner_tft_stats[0]['leaguePoints']} LP",
              inline=False
            )
        else:
            embed.add_field(
              name="RANK",
              value="Unranked",
              inline=False
            )
        for key in all_stats.keys():  # iterate for every queue type that player has played
            if all_stats[key]['hasPlayed']:  # check if player has played at least one match in that queue type
                embed.add_field(  # adding field contains information about his performance in that queue type
                  name=f"{key}",
                  value=f"""
                  **{all_stats[key]['played']}** games played with avg. **{round(all_stats[key]['placements']/all_stats[key]['played'], 2)}** place
                  **{round((all_stats[key]['top4']/all_stats[key]['played'])*100, 2)}%** top 4 rate
                  **{round((all_stats[key]['winrate']/all_stats[key]['played'])*100, 2)}%** winrate
                  """,  # data contains his average placement, winrate etc.
                  inline=False
                )
        embed.add_field(  # adding field with favourite traits, so traits that player has played the most in specific amout of games
          name="FAVOURITE TRAITS",
          value=f"""
          **{comps_sorted[0][1][2]} {comps_sorted[0][0][5:]}** in {comps_sorted[0][1][0]} matches with **{round((comps_sorted[0][1][1]/comps_sorted[0][1][0])*100, 2)}%** top 4 ratio
          **{comps_sorted[1][1][2]} {comps_sorted[1][0][5:]}** in {comps_sorted[1][1][0]} matches with **{round((comps_sorted[1][1][1]/comps_sorted[1][1][0])*100, 2)}%** top 4 ratio
          **{comps_sorted[2][1][2]} {comps_sorted[2][0][5:]}** in {comps_sorted[2][1][0]} matches with **{round((comps_sorted[2][1][1]/comps_sorted[2][1][0])*100, 2)}**% top 4 ratio
          **{comps_sorted[3][1][2]} {comps_sorted[3][0][5:]}** in {comps_sorted[3][1][0]} matches with **{round((comps_sorted[3][1][1]/comps_sorted[3][1][0])*100, 2)}**% top 4 ratio
          **{comps_sorted[4][1][2]} {comps_sorted[4][0][5:]}** in {comps_sorted[4][1][0]} matches with **{round((comps_sorted[4][1][1]/comps_sorted[4][1][0])*100, 2)}**% top 4 ratio 
          """
        )
        await ctx.send(embed=embed, file=file)


def setup(client):  # adding cog to our main.py file
    client.add_cog(TftCommands(client))
