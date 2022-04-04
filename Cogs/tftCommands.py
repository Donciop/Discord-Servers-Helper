import discord  # main packages
import pymongo
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.utils.manage_commands import create_option
from riotwatcher import TftWatcher  # RIOT API wrapper
from Cogs.settingsCommands import SettingsCommands
import os


class TftCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """ Event handler. That event is called when bot becomes online. Used mainly to initialize variables. """
        self.penguFilepath = "Media/Pengu_TFT.png"  # filepaths for files send with Discord embeds
        self.tftIconFilepath = "Media/Teamfight_Tactics_icon.png"
        self.tftEmoji = "<:TFT:912917249923375114>"  # reference to custom Discord emoji
        self.region = 'eun1'  # used in Riotwatcher to determine which region we're looking for
        self.watcher = TftWatcher(os.getenv('APIKEYTFT'))  # RIOT API KEY

    @staticmethod
    async def rank_check(summoner_rank: dict):
        """
        Method that checks player's rank and return specific information for further usage

            Args:
                summoner_rank (dict): Dictionary from RiotWatcher containing information about player's ranking

            Returns:
                tier_emoji: custom emoji based on player's rank
                rank (int): calculated rating for local leaderboard
        """
        rank_dict = await SettingsCommands.load_json_dict("JsonData/rankDict.json")
        tier_emoji = ''
        tier_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
        rank_list = ["IV", "III", "II", "I"]
        q_type = rank = 0
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

    @cog_ext.cog_slash(  # slash command decorator in cog
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
        Command used to check player's rank in Teamfight Tactics

            Args:
                ctx: Context of the command
                nickname (str): Nickname of the player we want to find

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return

        # access data about specific player from RIOT API
        summoner = self.watcher.summoner.by_name(self.region, nickname)
        if not summoner:  # check if the player actually exists
            await ctx.send(f"Can't find **{nickname}** on EUNE server.")
            return  # return if player's not found

        # access data about player's rank
        summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])
        if not summoner_tft_stats:  # check if player has rank on Teamfight Tactics
            await ctx.send(f"Player **{nickname}** is unranked on TFT")
            return  # return if player's unranked

        title_nickname = nickname.lower()  # nickname operations for accessing the lolchess.gg website
        title_nickname = title_nickname.replace(" ", "")
        embed = discord.Embed(  # styling Discord embed message
            color=0x11f80d,  # color of the embed message
            title=f"🎲 Teamfight Tactics {nickname}'s Rank 🎲",  # title of the embed message
            description="Click the title for advanced information",  # description of the embed message
            url=f"https://lolchess.gg/profile/eune/{title_nickname}"
        )

        file = discord.File(  # creating file to send image along the embed message
            self.penguFilepath,  # file path to image
            filename="image.png"  # name of the file
        )

        embed.set_thumbnail(url="attachment://image.png")  # setting emebed's thumbnail

        # get player's rank and rating for leaderboard
        tier_emoji, rank = await self.rank_check(summoner_tft_stats)
        q_type = 0
        if summoner_tft_stats[0]['queueType'] == 'RANKED_TFT_TURBO':  # check if we're processing right queue type
            q_type = 1
        # adding fields to embed message that contains rank , winrate, amounts of matches played and league points owned
        embed.add_field(
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
        Command used to add players to the database for further usage in leaderboard

            Args:
                ctx: Context of the command
                nickname (str): Nickname of the player we want to add

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        collection = await SettingsCommands.db_connection("Discord_Bot_Database", "tft_players")
        if not channel_check:
            return
        if collection is None:
            await ctx.send("Failed to connect to Database :(")
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

        tft_player = collection.find_one({"nickname": nickname})
        if tft_player:  # searching database to check if player's already exists
            await ctx.send(f"Player **{nickname}** already exists in database")
            return  # return if player's already in the database
        else:
            tier_emoji, ranking = await self.rank_check(ctx)
            query = {
                '_id': summoner_tft_stats[q_type]['summonerId'],
                'nickname': nickname,
                'matchesPlayed': (summoner_tft_stats[q_type]['wins'] + summoner_tft_stats[q_type]['losses']),
                'rank': summoner_tft_stats[q_type]['rank'],
                'tier': summoner_tft_stats[q_type]['tier'],
                'leaguePoints': summoner_tft_stats[q_type]['leaguePoints'],
                'tierEmoji': tier_emoji,
                'wins': summoner_tft_stats[q_type]['wins'],
                'ranking': ranking
            }
            collection.insert_one(query)
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
        Command used to remove players from database on demand

            Args:
                ctx: Context of the command
                nickname (str): Nickname of the player we want to add'

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        collection = await SettingsCommands.db_connection("Discord_Bot_Database", "tft_players")
        if not channel_check:
            return

        if collection is None:
            await ctx.send("Failed to connect to Database :(")
            return

        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You don't have permission to delete users from database, ask administrators or moderators")
            return

        tft_player = collection.find_one({"nickname": nickname})
        if tft_player:
            collection.delete_one({"nickname": nickname})  # removing player from database
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
        Command used to show local leaderboard of Teamfight Tactics player that are in our database

            Args:
                ctx: Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        collection = await SettingsCommands.db_connection("Discord_Bot_Database", "tft_players")
        if not channel_check:
            return
        if collection is None:
            await ctx.send("Failed to connect to Database :(")
            return
        embed = discord.Embed(
          color=0x11f80d,
          title="🏆 Teamfight Tactics Leaderboard 🏆",
          description="For advanced info use *tftStats or *tftRank"
        )
        file = discord.File(self.penguFilepath, filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        await ctx.defer()  # defer a command due to long computing time and timeouts from slash commands
        iterator = 1
        for old_tft_player in collection.find():

            summoner = self.watcher.summoner.by_name(self.region, old_tft_player['nickname'])
            if not summoner:
                await ctx.send(f"Can't find **{old_tft_player['nickname']}** on EUNE server.")
                return

            summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])
            if not summoner_tft_stats:
                await ctx.send(f"Player **{old_tft_player['nickname']}** is unranked")
                return

            q_type = 0
            if summoner_tft_stats[0]['queueType'] == 'RANKED_TFT_TURBO':
                q_type = 1

            tier_emoji, ranking = await self.rank_check(ctx)
            collection.update_one({"nickname": old_tft_player['nickname']},
                                  {"$set": {"matchesPlayed":
                                            (summoner_tft_stats[q_type]['wins']+summoner_tft_stats[q_type]['losses']),
                                            "rank": summoner_tft_stats[q_type]['rank'],
                                            "tier": summoner_tft_stats[q_type]['tier'],
                                            "leaguePoints": summoner_tft_stats[q_type]['leaguePoints'],
                                            "tierEmoji": tier_emoji, "wins": summoner_tft_stats[q_type]['wins'],
                                            "ranking": ranking
                                            }})
        # iterate over every player in leaderboard to give him right place
        for tft_player in collection.find().sort("ranking", pymongo.DESCENDING):
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
                    name=f"{rank_emoji} {tft_player['tierEmoji']}{tft_player['nickname']} | "
                         f"{tft_player['tier']} {tft_player['rank']} ({tft_player['leaguePoints']} LP)",
                    value=f"**{round((tft_player['wins']/tft_player['matchesPlayed'])*100)}**% winrate"
                          f" with **{tft_player['matchesPlayed']}** matches played",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{tft_player['tierEmoji']}{tft_player['nickname']} | "
                         f"{tft_player['tier']} {tft_player['rank']} ({tft_player['leaguePoints']} LP)",
                    value=f"**{round((tft_player['wins'] / tft_player['matchesPlayed']) * 100)}**% winrate"
                          f" with **{tft_player['matchesPlayed']}** matches played",
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
        """
        Command used to gather and analyze data from Teamfight Tactics match history

            Args:
                ctx: Context of the command
                nickname (str): Nickname of the player we want to find
                number_of_matches (int): Number of matches we want to search for

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return

        # due to API limitations, we can't collect data from more than 500 matches
        if number_of_matches >= 500 or number_of_matches <= 0:
            await ctx.send(f"Wrong number of matches! Try between 0 - 500")
            return  # return if wrong number of matches was specified

        summoner = self.watcher.summoner.by_name(self.region, nickname)
        if not summoner:
            await ctx.send(f"Can't find summoner **{nickname}**")
            return

        summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])
        count = number_of_matches

        # access player's match history in form of list of match ids
        match_list = self.watcher.match.by_puuid("europe", summoner['puuid'], count)
        if not match_list:  # check if player played at least 1 match
            await ctx.send(f"**{nickname}** didn't played any Teamfight Tactics games")
            return  # return if player has no matches of Teamfight Tactics on their account

        # Getting data from .json files that are used to store information about Teamfight Tactics characters etc.
        all_stats = await SettingsCommands.load_json_dict("JsonData/allStats.json")
        comps = await SettingsCommands.load_json_dict("JsonData/tftComps.json")
        await ctx.defer()
        for match in match_list:  # iterate over every match in match list
            match_detail = self.watcher.match.by_id("europe", match)  # getting match details for further analysis
            # check if we're getting matches only from current "set" in Teamfight Tactics
            if match_detail['info']['tft_set_number'] != 6:
                break
            # iterate over every participant in match to find our player
            for participant in match_detail['info']['participants']:
                # check if player's 'puuid' matches participant 'puuid' to ensure we're collecting our player's data
                if participant['puuid'] == summoner['puuid']:
                    # iterate over every 'trait' that player has on their board
                    for trait in participant['traits']:
                        # if trait is active, we collect that to our dictionary for further analysis
                        if trait['tier_current'] > 0:
                            comps[str(trait['name'])][0] += 1
                            # check if player was above 4th place for further performance analysis
                            if participant['placement'] <= 4:
                                comps[str(trait['name'])][1] += 1
                    # check from what type of queue the match we're analyzing right now is
                    if match_detail['info']['queue_id'] == 1090:
                        q_type = 'Normal'  # assign q_type variable based on queue type of the match
                    elif match_detail['info']['queue_id'] == 1100:
                        q_type = 'Ranked'
                    elif match_detail['info']['queue_id'] == 1150:
                        q_type = 'Double Up'
                    else:
                        q_type = 'Hyper Roll'
                    # boolean that tells us that player has played that queue type at least once
                    all_stats[str(q_type)]['hasPlayed'] = True
                    all_stats[str(q_type)]['played'] += 1  # increment number of matches played
                    # information about placement in that match for further analysis
                    all_stats[str(q_type)]['placements'] += participant['placement']
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
            tier_emoji, ranking = await self.rank_check(ctx)
            embed.add_field(
                name="RANK",
                value=f"{tier_emoji} {summoner_tft_stats[0]['tier']} {summoner_tft_stats[0]['rank']} | "
                      f"{summoner_tft_stats[0]['leaguePoints']} LP",
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
        # adding field with favourite traits that player has played the most in his games
        print(comps_sorted[0][1][2])
        embed.add_field(
            name="FAVOURITE TRAITS",
            value=f"""
            **{str(comps_sorted[0][1][2])} {comps_sorted[0][0][5:]}** in {comps_sorted[0][1][0]} matches with **{round((comps_sorted[0][1][1]/comps_sorted[0][1][0])*100, 2)}%** top 4 ratio
            **{str(comps_sorted[1][1][2])} {comps_sorted[1][0][5:]}** in {comps_sorted[1][1][0]} matches with **{round((comps_sorted[1][1][1]/comps_sorted[1][1][0])*100, 2)}%** top 4 ratio
            **{str(comps_sorted[2][1][2])} {comps_sorted[2][0][5:]}** in {comps_sorted[2][1][0]} matches with **{round((comps_sorted[2][1][1]/comps_sorted[2][1][0])*100, 2)}**% top 4 ratio
            **{str(comps_sorted[3][1][2])} {comps_sorted[3][0][5:]}** in {comps_sorted[3][1][0]} matches with **{round((comps_sorted[3][1][1]/comps_sorted[3][1][0])*100, 2)}**% top 4 ratio
            **{str(comps_sorted[4][1][2])} {comps_sorted[4][0][5:]}** in {comps_sorted[4][1][0]} matches with **{round((comps_sorted[4][1][1]/comps_sorted[4][1][0])*100, 2)}**% top 4 ratio 
            """
        )
        await ctx.send(embed=embed, file=file)


def setup(client):  # adding cog to our main.py file
    client.add_cog(TftCommands(client))
