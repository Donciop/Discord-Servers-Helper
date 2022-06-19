import nextcord  # main packages
import pymongo
from nextcord.ext import commands, application_checks
from Cogs.settingsCommands import SettingsCommands, TftUtilityFunctions, RiotUtilityFunctions, DatabaseManager
from riotwatcher import TftWatcher
import os
import config


class TftCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='tft_rank', guild_ids=[218510314835148802])
    async def tft_rank(self, interaction: nextcord.Interaction,
                       nickname: str = nextcord.SlashOption(required=True)):
        """
        Command used to check player's rank in Teamfight Tactics

            Args:
                interaction: (nextcord.Interaction): Context of the command
                nickname (str): Nickname of the player we want to find

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        # access data about specific player from RIOT API for later operations
        summoner = await TftUtilityFunctions.get_summoner(interaction, nickname)
        summoner_stats = await TftUtilityFunctions.get_tft_ranked_stats(interaction, summoner)

        if not summoner or not summoner_stats:
            return

        # nickname operations to access lolchess.gg
        title_nickname = nickname.lower()
        title_nickname = title_nickname.replace(" ", "")

        # styling Discord embed message
        embed = nextcord.Embed(
            color=0x11f80d,  # color of the embed message
            title=f"🎲 Teamfight Tactics {nickname}'s Rank 🎲",  # title of the embed message
            description="Click the title for advanced information",  # description of the embed message
            url=f"https://lolchess.gg/profile/eune/{title_nickname}"
        )

        # creating file to send image along the embed message
        file = nextcord.File(
            config.TFT_THUMBNAIL_FILEPATH,  # file path to image
            filename="image.png"  # name of the file
        )

        # setting embed message thumbnail
        embed.set_thumbnail(url="attachment://image.png")

        # get player's rating to print out
        tier_emoji = await RiotUtilityFunctions.get_rank_emoji(summoner_stats)

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
        await interaction.response.send_message(file=file, embed=embed)

    @nextcord.slash_command(name='tft_add_player', guild_ids=[218510314835148802])
    async def tft_add_player(self, interaction: nextcord.Interaction,
                             nickname: str = nextcord.SlashOption(required=True)):
        """
        Command used to add players to the database for further usage in leaderboard

            Args:
                interaction: (nextcord.Interaction): Context of the command
                nickname (str): Nickname of the player we want to add

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'set7_tft_players',
                                                             interaction=interaction)
        if collection is None or not channel_check:
            return

        summoner = await TftUtilityFunctions.get_summoner(interaction, nickname)
        summoner_stats = await TftUtilityFunctions.get_tft_ranked_stats(interaction, summoner)

        # searching database to check if player's already exists
        tft_player = collection.find_one({'nickname': nickname})
        if tft_player:
            await interaction.response.send_message(f'Player **{nickname}** already exists in database',
                                                    ephemeral=True)
            return

        # checking user's rank
        if not summoner_stats:
            await interaction.response.send_message(f'Player **{nickname}** is unranked',
                                                    ephemeral=True)
            return

        # calculating local ranking and corresponding tier emoji to display on leaderboard
        tier_emoji = await RiotUtilityFunctions.get_rank_emoji(summoner_stats)
        ranking = await RiotUtilityFunctions.get_local_rank(summoner_stats)

        # preparing query that will be inserted to the database
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
        await interaction.response.send_message(f'Added **{nickname}** to the database', ephemeral=True)

    @nextcord.slash_command(name='tft_remove_player', guild_ids=[218510314835148802])
    @application_checks.has_permissions(manage_channels=True)
    async def tft_remove_player(self, interaction: nextcord.Interaction,
                                nickname: str = nextcord.SlashOption(required=True)):
        """
        Command used to remove players from database on demand

            Args:
                interaction: (nextcord.Interaction): Context of the command
                nickname (str): Nickname of the player we want to add'

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'set7_tft_players')

        if not channel_check or collection is None:
            return

        # searching database to check if player's already exists
        tft_player = collection.find_one({'nickname': nickname})
        if tft_player:
            collection.delete_one({'nickname': nickname})  # removing player from database
            await interaction.response.send_message(f'You have deleted **{nickname}** from database', ephemeral=True)
        else:
            await interaction.response.send_message(f'Can\'t find **{nickname}** in the database', ephemeral=True)

    @nextcord.slash_command(name='tft_ranking', guild_ids=[218510314835148802])
    async def tft_ranking(self, interaction: nextcord.Interaction):
        """
        Command used to show local leaderboard of Teamfight Tactics player that are in our database

            Args:
                interaction: (nextcord.Interaction): Context of the command

            Returns:
                None
        """
        channel_check = await SettingsCommands.channel_check(interaction)
        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'tft_players')

        if not channel_check or collection is None:
            return

        embed = nextcord.Embed(
          color=0x11f80d,
          title="🏆 Teamfight Tactics Leaderboard 🏆",
          description="For advanced info use *tftStats or *tftRank"
        )
        file = nextcord.File(config.TFT_THUMBNAIL_FILEPATH, filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")

        # defer a command due to long computing time and timeouts from slash commands
        await interaction.response.defer()

        for old_tft_player in collection.find():

            summoner = await TftUtilityFunctions.get_summoner(interaction, old_tft_player['nickname'])
            summoner_stats = await TftUtilityFunctions.get_tft_ranked_stats(interaction, summoner)

            tier_emoji = await RiotUtilityFunctions.get_rank_emoji(summoner_stats)
            ranking = await RiotUtilityFunctions.get_local_rank(summoner_stats)
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
        for iterator, tft_player in enumerate(collection.find().sort("ranking", pymongo.DESCENDING)):
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
        await interaction.followup.send(embed=embed, file=file)

    @nextcord.slash_command(name='tft_stats', guild_ids=[218510314835148802, 913168099241504890])
    async def tft_stats(self, interaction: nextcord.Interaction,
                        nickname: str = nextcord.SlashOption(required=True),
                        number_of_matches: int = nextcord.SlashOption(required=True),
                        search_queue_type: str = nextcord.SlashOption(required=True,
                                                                      choices={
                                                                          'all': 'all',
                                                                          'normal': 'Normal',
                                                                          'ranked': 'Ranked',
                                                                          'double_up': 'Double Up',
                                                                          'hyper_roll': 'Hyper Roll'}
                                                                      )):
        """
        Command used to gather and analyze data from Teamfight Tactics match history

            Args:
                interaction: (nextcord.Interaction): Context of the command
                nickname (str): Nickname of the player we want to find
                number_of_matches (int): Number of matches we want to search for
                search_queue_type (str): Type of queue that You want to collect stats for

            Returns:
                None
        """
        watcher = TftWatcher(os.getenv('APIKEYTFT'))
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        # due to API limitations, we can't collect data from more than 500 matches
        if number_of_matches >= 500 or number_of_matches <= 0:
            await interaction.send(f"Wrong number of matches! Try between 0 - 500")
            return

        summoner = await TftUtilityFunctions.get_summoner(interaction, nickname)
        if not summoner:
            return

        summoner_stats = await TftUtilityFunctions.get_tft_ranked_stats(interaction, summoner)

        # access player's match history in form of list of match ids
        match_list = watcher.match.by_puuid("europe", summoner['puuid'], number_of_matches)

        # check if player played at least 1 match
        if not match_list:
            await interaction.response.send_message(f"**{nickname}** didn't played any Teamfight Tactics games",
                                                    ephemeral=True)
            return

        # Getting data from .json files that are used to store information about Teamfight Tactics characters etc.
        all_stats = await SettingsCommands.load_json_dict("JsonData/allStats.json")
        queue_ids = await SettingsCommands.load_json_dict("JsonData/queue_numbers_dict.json")
        comps = await SettingsCommands.load_json_dict("JsonData/TFT_SET_7/SET_7_TRAITS.json")
        champs = await SettingsCommands.load_json_dict("JsonData/TFT_SET_7/SET_7_CHAMPIONS.json")

        await interaction.response.defer()

        # iterate over every match in match list
        for match in match_list:

            # getting match details for further analysis
            match_detail = watcher.match.by_id("europe", match)

            if search_queue_type != 'all':
                if match_detail['info']['queue_id'] != queue_ids[search_queue_type]:
                    continue

            # check if we're getting matches only from current "set" in Teamfight Tactics
            if match_detail['info']['tft_set_number'] != config.CURRENT_TFT_SET:
                break

            # iterate over every participant in match to find our player
            for participant in match_detail['info']['participants']:

                # check if player's 'puuid' matches participant 'puuid' to ensure we're collecting our player's data
                if participant['puuid'] != summoner['puuid']:
                    continue

                # iterate over every 'trait' that player has on their board
                for trait in participant['traits']:

                    # if trait is active, we collect that to our dictionary for further analysis
                    if trait['tier_current'] > 0:
                        comps[str(trait['name'])][0] += 1

                        # check if player was above 4th place for further performance analysis
                        if participant['placement'] <= 4:
                            comps[str(trait['name'])][1] += 1

                for champion in participant['units']:
                    champs[str(champion['character_id'])][0] += 1

                    if participant['placement'] <= 4:
                        champs[str(champion['character_id'])][1] += 1

                # check from what type of queue the match we're analyzing right now and
                # assign q_type variable based on queue type of the match
                if match_detail['info']['queue_id'] == 1090:
                    q_type = 'Normal'
                elif match_detail['info']['queue_id'] == 1100:
                    q_type = 'Ranked'
                elif match_detail['info']['queue_id'] == 1160:
                    q_type = 'Double Up'
                else:
                    q_type = 'Hyper Roll'

                # saving that user has played this type of queue
                all_stats[str(q_type)]['hasPlayed'] = True

                # incrementing number of games that player has played in this game mode
                all_stats[str(q_type)]['played'] += 1

                # saving information about placements
                if match_detail['info']['queue_id'] == 1160:
                    all_stats[str(q_type)]['placements'] += int(participant['placement'] / 2)
                else:
                    all_stats[str(q_type)]['placements'] += participant['placement']

                # checking if player managed to be in top4 players
                if participant['placement'] <= 4:
                    all_stats[str(q_type)]['top4'] += 1
                    if match_detail['info']['queue_id'] == 1160:
                        if participant['placement'] == 1 or participant['placement'] == 2:
                            all_stats[str(q_type)]['winrate'] += 1
                    else:
                        if participant['placement'] == 1:
                            all_stats[str(q_type)]['winrate'] += 1

        # sort dictionary based on amount of times a trait has been played
        comps_sorted = sorted(
            comps.items(),
            key=lambda x: x[1],
            reverse=True
        )
        champs_sorted = sorted(
            champs.items(),
            key=lambda x: x[1],
            reverse=True
        )

        title_nickname = nickname.lower()
        title_nickname = title_nickname.replace(" ", "")

        embed = nextcord.Embed(
            color=0x11f80d,
            title=f"{config.TFT_DISCORD_EMOJI} Teamfight Tactics {nickname}'s Stats ",
            description="Click the title for advanced information on LolChess",
            url=f"https://lolchess.gg/profile/eune/{title_nickname}"
        )
        file = nextcord.File(config.TFT_THUMBNAIL_FILEPATH, filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")

        if summoner_stats:
            tier_emoji = await RiotUtilityFunctions.get_rank_emoji(summoner_stats)
            embed.add_field(
                name=":trophy: RANK",
                value=f"{tier_emoji} {summoner_stats['tier']} {summoner_stats['rank']} | "
                      f"{summoner_stats['leaguePoints']} LP",
                inline=False
            )
        else:
            embed.add_field(
                name="RANK",
                value="Unranked",
                inline=False
            )
        if search_queue_type == 'all':
            for key in all_stats.keys():  # iterate for every queue type that player has played
                if all_stats[key]['hasPlayed']:  # check if player has played at least one match in that queue type
                    average_place = round(all_stats[key]['placements']/all_stats[key]['played'], 2)
                    embed.add_field(  # adding field contains information about his performance in that queue type
                        name=f"{config.TFT_DISCORD_EMOJI} {key}",
                        value=f"""
                        **{all_stats[key]['played']}** games played with avg. **{average_place}** place
                        **{round((all_stats[key]['top4']/all_stats[key]['played'])*100)}%** top 4 rate
                        **{round((all_stats[key]['winrate']/all_stats[key]['played'])*100)}%** winrate
                        """,  # data contains his average placement, winrate etc.
                        inline=False
                    )
        else:
            # check if player has played at least one match in that queue type
            if all_stats[search_queue_type]['hasPlayed']:
                average_place = round(
                    all_stats[search_queue_type]['placements'] / all_stats[search_queue_type]['played'], 2)

                # adding field contains information about his performance in that queue type
                embed.add_field(
                    name=f"{config.TFT_DISCORD_EMOJI} {search_queue_type}",
                    value=f'**{all_stats[search_queue_type]["played"]}** games played with avg.'
                          f' **{average_place}** place'
                    f'**{round((all_stats[search_queue_type]["top4"]/all_stats[search_queue_type]["played"]) * 100)}'
                          f'%** top 4 rate'
                    f'**{round((all_stats[search_queue_type]["winrate"]/all_stats[search_queue_type]["played"]) * 100)}'
                          f'%** winrate',
                    # data contains his average placement, winrate etc.
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{config.TFT_DISCORD_EMOJI} {search_queue_type}",
                    value="No games in this game mode during this SET",
                    inline=False
                )
                embed.set_footer(text=f'Statistics provided by {self.client.user.name}™')
                await interaction.followup.send(embed=embed, file=file)

        # adding field with favourite traits that player has played the most in his games
        embed.add_field(
            name=":heart: FAVOURITE TRAITS",
            value=f'**{comps_sorted[0][1][2]} {comps_sorted[0][0][5:]}** in {comps_sorted[0][1][0]} matches '
            f'with **{round((comps_sorted[0][1][1]/comps_sorted[0][1][0])*100)}%** top 4 ratio\n'
            f'**{comps_sorted[1][1][2]} {comps_sorted[1][0][5:]}** in {comps_sorted[1][1][0]} matches '
            f'with **{round((comps_sorted[1][1][1]/comps_sorted[1][1][0])*100)}%** top 4 ratio\n'
            f'**{comps_sorted[2][1][2]} {comps_sorted[2][0][5:]}** in {comps_sorted[2][1][0]} matches '
            f'with **{round((comps_sorted[2][1][1]/comps_sorted[2][1][0])*100)}**% top 4 ratio\n'
            f'**{comps_sorted[3][1][2]} {comps_sorted[3][0][5:]}** in {comps_sorted[3][1][0]} matches '
            f'with **{round((comps_sorted[3][1][1]/comps_sorted[3][1][0])*100)}**% top 4 ratio\n'
            f'**{comps_sorted[4][1][2]} {comps_sorted[4][0][5:]}** in {comps_sorted[4][1][0]} matches '
            f'with **{round((comps_sorted[4][1][1]/comps_sorted[4][1][0])*100)}**% top 4 ratio\n'
        )

        # adding field with player's favourite champions which he played the most
        embed.add_field(
            name=":heart: FAVOURITE CHAMPIONS",
            value=f'**{champs_sorted[0][0][5:]}** in {champs_sorted[0][1][0]} matches '
            f'with **{round((champs_sorted[0][1][1] / champs_sorted[0][1][0]) * 100)}%** top 4 ratio\n'
            f'**{champs_sorted[1][0][5:]}** in {champs_sorted[1][1][0]} matches '
            f'with **{round((champs_sorted[1][1][1] / champs_sorted[1][1][0]) * 100)}%** top 4 ratio\n'
            f'**{champs_sorted[2][0][5:]}** in {champs_sorted[2][1][0]} matches '
            f'with **{round((champs_sorted[2][1][1] / champs_sorted[2][1][0]) * 100)}%** top 4 ratio\n'
            f'**{champs_sorted[3][0][5:]}** in {champs_sorted[3][1][0]} matches '
            f'with **{round((champs_sorted[3][1][1] / champs_sorted[3][1][0]) * 100)}%** top 4 ratio\n'
            f'**{champs_sorted[4][0][5:]}** in {champs_sorted[4][1][0]} matches '
            f'with **{round((champs_sorted[4][1][1] / champs_sorted[4][1][0]) * 100)}%** top 4 ratio\n'
        )

        embed.set_footer(text=f'Statistics provided by {self.client.user.name}™')
        await interaction.followup.send(embed=embed, file=file)


def setup(client):  # adding cog to our main.py file
    client.add_cog(TftCommands(client))
