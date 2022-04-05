import discord  # main packages
from pymongo import DESCENDING
from os import getenv
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.utils.manage_commands import create_option
from Cogs.settingsCommands import SettingsCommands
from riotwatcher import TftWatcher


class TftCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        """ Event handler. That event is called when bot becomes online. Used mainly to initialize variables. """
        self.penguFilepath = "Media/Pengu_TFT.png"  # filepaths for files send with Discord embeds
        self.tftIconFilepath = "Media/Teamfight_Tactics_icon.png"
        self.tftEmoji = "<:TFT:912917249923375114>"  # reference to custom Discord emoji

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

        # access data about specific player from RIOT API for later operations
        summoner, summoner_stats = await SettingsCommands.get_riot_stats(ctx, stats_type='TFT', nickname=nickname)

        if not summoner_stats:
            return

        # nickname operations to access lolchess.gg
        title_nickname = nickname.lower()
        title_nickname = title_nickname.replace(" ", "")

        # styling Discord embed message
        embed = discord.Embed(
            color=0x11f80d,  # color of the embed message
            title=f"🎲 Teamfight Tactics {nickname}'s Rank 🎲",  # title of the embed message
            description="Click the title for advanced information",  # description of the embed message
            url=f"https://lolchess.gg/profile/eune/{title_nickname}"
        )

        # creating file to send image along the embed message
        file = discord.File(
            self.penguFilepath,  # file path to image
            filename="image.png"  # name of the file
        )

        # setting embed message thumbnail
        embed.set_thumbnail(url="attachment://image.png")

        # get player's rating to print out
        tier_emoji = await SettingsCommands.riot_rank_check(summoner_stats, rank=False)

        # basic math to calculate player's win ratio and amount of matches played, that are going to be printed out
        win_ratio = round((summoner_stats['wins']/(summoner_stats['wins']+summoner_stats['losses']))*100)
        amount_of_matches = summoner_stats['wins'] + summoner_stats['losses']

        # adding fields to embed message that contains rank, win rate,
        # amounts of matches played and league points currently owned
        embed.add_field(
            name="RANKED",
            value=f"{tier_emoji} {summoner_stats['tier']} {summoner_stats['rank']} | "
                  f"{summoner_stats['leaguePoints']} LP\n"
                  f"**{win_ratio}%** top 1 ratio ({amount_of_matches}) Matches")
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
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'tft_players', ctx=ctx)
        if collection is None or not channel_check:
            return

        summoner_stats, tier_emoji = await SettingsCommands.get_riot_stats(ctx, stats_type='TFT', nickname=nickname)

        # searching database to check if player's already exists
        tft_player = collection.find_one({'nickname': nickname})
        if tft_player:
            await ctx.send(f'Player **{nickname}** already exists in database')
            return

        tier_emoji, ranking = await SettingsCommands.riot_rank_check(summoner_stats)
        query = {
            '_id': summoner_stats['summonerId'],
            'nickname': nickname,
            'matchesPlayed': (summoner_stats['wins'] + summoner_stats['losses']),
            'rank': summoner_stats['rank'],
            'tier': summoner_stats['tier'],
            'leaguePoints': summoner_stats['leaguePoints'],
            'tierEmoji': tier_emoji,
            'wins': summoner_stats['wins'],
            'ranking': ranking
        }
        collection.insert_one(query)
        await ctx.send(f'Added **{nickname}** to the database')

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
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'tft_players', ctx=ctx)

        if not channel_check or collection is None:
            return

        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send('You don\'t have permission to delete users from database, ask administrators or moderators')
            return

        tft_player = collection.find_one({'nickname': nickname})
        if tft_player:
            collection.delete_one({'nickname': nickname})  # removing player from database
            await ctx.send(f'You have deleted **{nickname}** from database')
        else:
            await ctx.send(f'Can\'t find **{nickname}** in database')

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
        collection = await SettingsCommands.db_connection('Discord_Bot_Database', 'tft_players', ctx=ctx)

        if not channel_check or collection is None:
            return

        embed = discord.Embed(
          color=0x11f80d,
          title="🏆 Teamfight Tactics Leaderboard 🏆",
          description="For advanced info use *tftStats or *tftRank"
        )
        file = discord.File(self.penguFilepath, filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")

        await ctx.defer()  # defer a command due to long computing time and timeouts from slash commands
        for old_tft_player in collection.find():
            summoner, summoner_stats = await SettingsCommands.get_riot_stats(ctx,
                                                                             stats_type='TFT',
                                                                             nickname=old_tft_player['nickname'])
            tier_emoji, ranking = await SettingsCommands.riot_rank_check(summoner_stats)
            collection.update_one({"nickname": old_tft_player['nickname']},
                                  {"$set": {"matchesPlayed":
                                            (summoner_stats['wins']+summoner_stats['losses']),
                                            "rank": summoner_stats['rank'],
                                            "tier": summoner_stats['tier'],
                                            "leaguePoints": summoner_stats['leaguePoints'],
                                            "tierEmoji": tier_emoji, "wins": summoner_stats['wins'],
                                            "ranking": ranking
                                            }})
        # iterate over every player in leaderboard to give him right place
        for iterator, tft_player in enumerate(collection.find().sort("ranking", DESCENDING)):
            if iterator == 0:  # first, second and third place have custom emoji besides their nickname on leaderboard
                rank_emoji = ":first_place:"
            elif iterator == 1:
                rank_emoji = ":second_place:"
            elif iterator == 2:
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
        watcher = TftWatcher(getenv('APIKEYTFT'))
        channel_check = await SettingsCommands.channel_check(ctx)
        if not channel_check:
            return

        # due to API limitations, we can't collect data from more than 500 matches
        if number_of_matches >= 500 or number_of_matches <= 0:
            await ctx.send(f"Wrong number of matches! Try between 0 - 500")
            return

        summoner, summoner_stats = await SettingsCommands.get_riot_stats(ctx, stats_type='TFT', nickname=nickname,
                                                                         all_stats=True)
        # access player's match history in form of list of match ids
        match_list = watcher.match.by_puuid("europe", summoner['puuid'], number_of_matches)
        if not match_list:  # check if player played at least 1 match
            await ctx.send(f"**{nickname}** didn't played any Teamfight Tactics games")
            return

        # Getting data from .json files that are used to store information about Teamfight Tactics characters etc.
        all_stats = await SettingsCommands.load_json_dict("JsonData/allStats.json")
        comps = await SettingsCommands.load_json_dict("JsonData/tft6.json")

        await ctx.defer()

        for match in match_list:  # iterate over every match in match list
            match_detail = watcher.match.by_id("europe", match)  # getting match details for further analysis

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

                    # check from what type of queue the match we're analyzing right now and
                    # assign q_type variable based on queue type of the match
                    if match_detail['info']['queue_id'] == 1090:
                        q_type = 'Normal'
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

        # sort dictionary based on amount of times a trait has been played
        comps_sorted = sorted(
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

        if summoner_stats:
            tier_emoji, ranking = await SettingsCommands.riot_rank_check(summoner_stats)
            embed.add_field(
                name=":trophy: RANK",
                value=f"{tier_emoji} {summoner_stats[0]['tier']} {summoner_stats[0]['rank']} | "
                      f"{summoner_stats[0]['leaguePoints']} LP",
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
                average_place = round(all_stats[key]['placements']/all_stats[key]['played'], 2)
                embed.add_field(  # adding field contains information about his performance in that queue type
                    name=f"{self.tftEmoji} {key}",
                    value=f"""
                    **{all_stats[key]['played']}** games played with avg. **{average_place}** place
                    **{round((all_stats[key]['top4']/all_stats[key]['played'])*100, 2)}%** top 4 rate
                    **{round((all_stats[key]['winrate']/all_stats[key]['played'])*100, 2)}%** winrate
                    """,  # data contains his average placement, winrate etc.
                    inline=False
                )
        # adding field with favourite traits that player has played the most in his games
        embed.add_field(
            name=":heart: FAVOURITE TRAITS",
            value=f'**{comps_sorted[0][0][5:]}** in {comps_sorted[0][1][0]} matches '
            f'with **{round((comps_sorted[0][1][1]/comps_sorted[0][1][0])*100, 2)}%** top 4 ratio\n'
            f'**{comps_sorted[1][0][5:]}** in {comps_sorted[1][1][0]} matches '
            f'with **{round((comps_sorted[1][1][1]/comps_sorted[1][1][0])*100, 2)}%** top 4 ratio\n'
            f'**{comps_sorted[2][0][5:]}** in {comps_sorted[2][1][0]} matches '
            f'with **{round((comps_sorted[2][1][1]/comps_sorted[2][1][0])*100, 2)}**% top 4 ratio\n'
            f'**{comps_sorted[3][0][5:]}** in {comps_sorted[3][1][0]} matches '
            f'with **{round((comps_sorted[3][1][1]/comps_sorted[3][1][0])*100, 2)}**% top 4 ratio\n'
            f'**{comps_sorted[4][0][5:]}** in {comps_sorted[4][1][0]} matches '
            f'with **{round((comps_sorted[4][1][1]/comps_sorted[4][1][0])*100, 2)}**% top 4 ratio\n')
        embed.set_footer(text=f'Statistics provided by {self.client.user.name}')
        await ctx.send(embed=embed, file=file)


def setup(client):  # adding cog to our main.py file
    client.add_cog(TftCommands(client))
