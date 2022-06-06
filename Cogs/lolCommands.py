import nextcord  # main packages
from nextcord.ext import commands
from riotwatcher import LolWatcher  # RIOT API wrapper
import os
from Cogs.settingsCommands import SettingsCommands, LolUtilityFunctions, RiotUtilityFunctions, DatabaseManager
import config


class LolCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(name='lol_rank', guild_ids=[218510314835148802])
    async def lol_rank(self, interaction: nextcord.Interaction,
                       nickname: str = nextcord.SlashOption(required=True)):
        """
        Command used to check player's rank and display information about it

            Args:
                interaction (nextcord.Interaction): Context of the command
                nickname (str): Nickname of the player we want to find

            Returns:
                None
        """
        # checking if command was sent in allowed channel
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return

        # getting summoner data from RIOT API
        summoner = await LolUtilityFunctions.get_summoner(interaction, nickname)
        if not summoner:
            return

        # getting data about summoner solo and flex rank
        solo_summoner_stats = await LolUtilityFunctions.get_soloq_ranked_stats(interaction, summoner)
        flex_summoner_stats = await LolUtilityFunctions.get_flex_ranked_stats(interaction, summoner)
        if not solo_summoner_stats and not flex_summoner_stats:
            return

        # getting emoji associated with specific rank
        solo_emoji = await RiotUtilityFunctions.get_rank_emoji(solo_summoner_stats)
        flex_emoji = await RiotUtilityFunctions.get_rank_emoji(flex_summoner_stats)

        # setting embed message
        embed = nextcord.Embed(  # styling Discord embed message
            color=0x11f80d,  # color of the embed message
            title="👨‍🦽 League of Legends Rank 👨‍🦽",  # title of the embed message
            description=f"{nickname}'s ranked stats"  # description of the embed message
        )

        # creating file to send image along the embed message
        file = nextcord.File(
            config.LOL_THUMBNAIL_FILEPATH,  # file path to image
            filename="image.jpg"  # name of the file
        )

        # adding thumbnail to the embed message
        embed.set_thumbnail(url="attachment://image.jpg")

        if solo_summoner_stats:

            # calculate player's win rate
            winrate = round((solo_summoner_stats['wins'] / (solo_summoner_stats['wins'] + solo_summoner_stats['losses'])) * 100)

            # add fields to embed
            embed.add_field(
                name=f"{solo_summoner_stats['queueType']}",
                value=f"{solo_emoji} {solo_summoner_stats['tier']} {solo_summoner_stats['rank']} | "
                      f"{solo_summoner_stats['leaguePoints']} LP with {winrate}% winrate({solo_summoner_stats['wins']}W "
                      f"{solo_summoner_stats['losses']}L)",
                inline=False
            )

        if flex_summoner_stats:

            winrate = round(
                (solo_summoner_stats['wins'] / (solo_summoner_stats['wins'] + solo_summoner_stats['losses'])) * 100)

            embed.add_field(
                name=f"{solo_summoner_stats['queueType']}",
                value=f"{flex_emoji} {solo_summoner_stats['tier']} {solo_summoner_stats['rank']} | "
                      f"{solo_summoner_stats['leaguePoints']} LP with {winrate}% winrate({solo_summoner_stats['wins']}W "
                      f"{solo_summoner_stats['losses']}L)",
                inline=False
            )

        # send the embed message
        await interaction.response.send_message(
            file=file,
            embed=embed
        )

    @nextcord.slash_command(name='lol_live_game', guild_ids=[218510314835148802])
    async def lol_live_game(self,
                            interaction: nextcord.Interaction,
                            nickname: str = nextcord.SlashOption(required=True)):
        """
        Command used to check player's live game along with information about enemies and teammates

            Args:
                interaction (nextcord.Interaction): Context of the command
                nickname (str): Nickname of the player we want to find

            Returns:
                None
        """
        watcher = LolWatcher(os.getenv('APIKEYLOL'))
        channel_check = await SettingsCommands.channel_check(interaction)
        if not channel_check:
            return
        team = team_champs = team_ranks = []

        # check the latest version of League of Legends
        latest = watcher.data_dragon.versions_for_region('eune')['n']['champion']

        # access data from external file contains information about characters in League of Legends
        static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')

        # iterate over every champion to assign them to corresponding champion's ID
        champ_dict = {}
        for key in static_champ_list['data']:
            row = static_champ_list['data'][key]
            champ_dict[row['key']] = row['id']

        summoner = await LolUtilityFunctions.get_summoner(interaction, nickname)
        if not summoner:
            return

        # access data about player's live game
        live_game = watcher.spectator.by_summoner('eun1', summoner['id'])
        if not live_game:
            await interaction.response.send_message(f"{nickname}'s not in game")
            return

        for participant in live_game['participants']:  # iterate over every participant in match to access their data.

            # assign champion's name based on their ID using dictionary that we made
            participant['championId'] = champ_dict[str(participant['championId'])]

            summoner = await LolUtilityFunctions.get_summoner(interaction, nickname)
            summoner_stats = await LolUtilityFunctions.get_soloq_ranked_stats(interaction, summoner)

            if not summoner_stats:  # check if player has rank in League of Legends

                # check queue type of the live game to determine what rank to show
                rank = "Unranked"
                team_ranks.append(rank)

                # add player's champion to the list of participants champions
                team_champs.append(participant['championId'])
                team.append(participant['summonerName'])  # add player to the list of participants
            else:
                rank_emoji = await RiotUtilityFunctions.get_rank_emoji(summoner_stats)
                rank = f"{rank_emoji} {summoner_stats['tier']} {summoner_stats['rank']} | " \
                       f"{summoner_stats['leaguePoints']} LP"
                team_ranks.append(rank)  # add player's rank to the list of participants ranks

        embed = nextcord.Embed(
            color=0x11f80d,
            title="👨‍🦽 League of Legends Live 👨‍🦽",
            description=f"{nickname}'s live game"
        )
        embed.add_field(  # add fields based on teams in League of Legends
            name="💙 Blue Team",
            value=f"\n{team[0]}\n\n{team[1]}\n\n{team[2]}\n\n{team[3]}\n\n{team[4]}",
            inline=True
        )
        embed.add_field(
            name="Champs",
            value=f"{team_champs[0]}\n\n{team_champs[1]}\n\n{team_champs[2]}\n\n{team_champs[3]}\n\n{team_champs[4]}",
            inline=True
        )
        embed.add_field(
            name="Ranks",
            value=f"{team_ranks[0]}\n\n{team_ranks[1]}\n\n{team_ranks[2]}\n\n{team_ranks[3]}\n\n{team_ranks[4]}",
            inline=True
        )
        embed.add_field(
            name="❤ Red Team",
            value=f"{team[5]}\n\n{team[6]}\n\n{team[7]}\n\n{team[8]}\n\n{team[9]}",
            inline=True
        )
        embed.add_field(
            name="Champs",
            value=f"{team_champs[5]}\n\n{team_champs[6]}\n\n{team_champs[7]}\n\n{team_champs[8]}\n\n{team_champs[9]}",
            inline=True
        )
        embed.add_field(
            name="Ranks",
            value=f"{team_ranks[5]}\n\n{team_ranks[6]}\n\n{team_ranks[7]}\n\n{team_ranks[8]}\n\n{team_ranks[9]}",
            inline=True
        )
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command(name='lol_time', guild_ids=[218510314835148802])
    async def lol_time(self, interaction: nextcord.Interaction,
                       member: nextcord.Member = nextcord.SlashOption(required=True)):
        """
        Command used to check how long the user was playing League of Legends

            Args:
                interaction (nextcord.Interaction): Context of the command
                member (nextcord.Member): Player that we want to check

            Returns:
                None
        """
        collection = await DatabaseManager.get_db_collection('Discord_Bot_Database', 'members')

        if not collection.count_documents({'_id': member.id}):
            await interaction.response.send_message(f'{member.mention} is a Bot, or isn\'t in our Database yet!')
            return

        time_online = collection.find_one({'_id': member.id}, {'league_time': 1})

        if time_online['league_time'].second <= 0 or time_online['league_time'] == 0:
            await interaction.response.send_message(f'{member.mention} has not played League of Legends')

        elif time_online['league_time'].second > 0 and time_online['league_time'].minute < 1:
            await interaction.response.send_message(
                f'{member.mention} was playing League of Legends for '
                f"**{time_online['league_time'].second}** seconds so far!")

        elif time_online['league_time'].minute > 0 and time_online['league_time'].hour < 1:
            await interaction.response.send_message(
                f'{member.mention} was playing League of Legends for '
                f"**{time_online['league_time'].minute}m {time_online['league_time'].second}s** so far!")

        elif time_online['league_time'].hour > 0 and time_online['league_time'].day < 2:
            await interaction.response.send_message(
                f'{member.mention} was playing League of Legends for '
                f"**{time_online['league_time'].hour}h {time_online['league_time'].minute}m "
                f"{time_online['league_time'].second}s** so far!")

        elif time_online['league_time'].day >= 2:
            await interaction.response.send_message(
                f'{member.mention} was playing League of Legends for '
                f"**{time_online['league_time'].day}d {time_online['league_time'].hour}h "
                f"{time_online['league_time'].minute}m {time_online['league_time'].second}s** so far!")

    @nextcord.slash_command(name='mmr_aram', guild_ids=[218510314835148802])
    async def aram_mmr(self, interaction: nextcord.Interaction,
                       nickname: str = nextcord.SlashOption(required=True)):
        # setting parameters for api request
        parameters = {'name': nickname}

        # get API response from whatismymrr.com site
        request = await SettingsCommands.get_json_response('https://eune.whatismymmr.com/api/v1/summoner', parameters,
                                                           interaction)

        if request:  # check if we got proper response from api
            await interaction.response.send_message(
                f'{nickname}, Your average ARAM MMR is **{request["ARAM"]["avg"]}**,'
                f' which is around **{request["ARAM"]["closestRank"]}**')
            return

    @nextcord.slash_command(name='mmr_ranked', guild_ids=[218510314835148802])
    async def ranked_mmr(self, interaction: nextcord.Interaction,
                         nickname: str = nextcord.SlashOption(required=True)):
        parameters = {'name': nickname}
        request = await SettingsCommands.get_json_response('https://eune.whatismymmr.com/api/v1/summoner', parameters,
                                                           interaction)
        if request:
            await interaction.response.send_message(
                f'{nickname}, Your average Ranked MMR is **{request["ranked"]["avg"]}**,'
                f' which is around **{request["ranked"]["closestRank"]}**')
            return


def setup(client):  # adding cog to our main.py file
    client.add_cog(LolCommands(client))
