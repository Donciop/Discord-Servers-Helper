import discord  # main packages
from discord.ext import commands
from discord_slash import cog_ext  # for slash commands
from discord_slash.utils.manage_commands import create_option
from riotwatcher import LolWatcher  # RIOT API wrapper
import os
from pymongo import MongoClient

class LolCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.watcher = LolWatcher(os.getenv('APIKEYLOL'))  # RIOT API KEY
        self.region = 'eun1'  # used in Riotwatcher to determine which region we're looking for
        self.logoFilepath = "Media/LOL-logo.jpg"  # filepaths for files send with Discord embeds

    @commands.command()
    async def lol_rank_check(self, ctx, summoner_rank):
        """
        Function used to determine player's rank on League of Legends
        :param ctx: context of the command
        :param summoner_rank: dictionary from Riotwatcher containing information about player's ranking
        :return solo_emoji: custom emoji based on player's ranking on Ranked Solo Queue
        :return flex_emoji: custom emoji based on player's ranking on Ranked Flex Queue
        """

        settings_cog = self.client.get_cog("SettingsCommands")
        if settings_cog is not None:
            rank_dict = await settings_cog.load_json_dict("JsonData/rankDict.json")
        else:
            await ctx.send("Failed to load ranks dictionary :(")
            return
        tier_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
        flex_emoji = None
        solo_emoji = None
        for q_type in summoner_rank:  # iterate over every queue type
            # for some reason, in data about League of Legends,
            # there is a queue from Teamfight Tactics, so we dismiss that
            if q_type['queueType'] == 'RANKED_TFT_PAIRS':
                continue
            for tier in tier_list:  # iterate over every tier until we find player's tier
                if q_type['tier'] == tier:
                    if q_type['queueType'] == 'RANKED_FLEX_SR':
                        flex_emoji = rank_dict[tier]  # assign emoji based on player's tier and queue type
                    else:
                        solo_emoji = rank_dict[tier]
        return solo_emoji, flex_emoji

    @cog_ext.cog_slash(  # slash command decorator
        name="lol_rank",  # name that will be displayed in Discord
        description="Check a specific player's Teamfight Tactics rank",  # description of the command
        guild_ids=[218510314835148802],  # list of server (guilds) id's that have access to this slash command
        options=[
            create_option(  # parameters in slash command
                name="nickname",  # name of the variable
                description="Type in player's nickname",  # description of parameter
                option_type=3,  # option_type refers to type of the variable ( 3 - STRING )
                required=True  # this parameter is required
            )
        ]
    )
    async def lol_rank(self, ctx, nickname: str):
        """
        Command used to check player's rank and display information about it
        :param ctx: passing context of the command
        :param nickname: nickname of the player we want to find
        """
        channel_check = None
        settings_cog = self.client.get_cog("SettingsCommands")
        if settings_cog is not None:
            channel_check = await settings_cog.channel_check(ctx, ctx.channel.id)
        if not channel_check:
            return
        me = self.watcher.summoner.by_name(self.region, nickname)  # access data about specific player from RIOT API
        if not me:  # check if the player actually exists
            await ctx.send(f"Can't find summoner {nickname}")
            return  # return if player's not found
        me_ranked_stats = self.watcher.league.by_summoner(self.region, me['id'])  # access data about player's rank
        # check if player has rank on League of Legends that is not rank from Teamfight Tactics
        if not me_ranked_stats or (len(me_ranked_stats) == 1 and me_ranked_stats[0]['queueType'] == 'RANKED_TFT_PAIRS'):
            await ctx.send(f"{nickname} is unranked")
            return  # return if player's unranked
        embed = discord.Embed(  # styling Discord embed message
            color=0x11f80d,  # color of the embed message
            title="👨‍🦽 League of Legends Rank 👨‍🦽",  # title of the embed message
            description=f"{nickname}'s ranked stats"  # description of the embed message
        )
        file = discord.File(  # creating file to send image along the embed message
            self.logoFilepath,  # file path to image
            filename="image.jpg"  # name of the file
        )
        embed.set_thumbnail(url="attachment://image.jpg")  # setting emebed thumbnail
        solo_emoji, flex_emoji = await self.lol_rank_check(ctx, me_ranked_stats)  # get player's rank and rating for leaderboard
        for qType in me_ranked_stats:  # iterate over every queue type to change their names and assign custom emojis
            if qType['queueType'] == 'RANKED_TFT_PAIRS':
                continue
            if qType['queueType'] == "RANKED_FLEX_SR":
                qType['queueType'] = "RANKED FLEX"
                tier_emoji = flex_emoji
            elif qType['queueType'] == "RANKED_SOLO_5x5":
                qType['queueType'] = "RANKED SOLO/DUO"
                tier_emoji = solo_emoji
            if tier_emoji is None:
                embed.add_field(  # add field to embed message based on custom emoji
                    name="Unranked",
                    value="\u200B",
                    inline=False
                )
            else:
                winrate = round((qType['wins'] / (qType['wins'] + qType['losses'])) * 100)  # calculate player's win rate
                embed.add_field(
                    name=f"{qType['queueType']}",
                    value=f"{tier_emoji} {qType['tier']} {qType['rank']} | {qType['leaguePoints']} LP with {winrate}% winrate({qType['wins']}W {qType['losses']}L)",
                    inline=False
                )
        await ctx.send(  # send the embed message
            file=file,
            embed=embed
        )

    @cog_ext.cog_slash(
        name="lol_live_game",
        description="Check player's current League of Legends game!",
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
    async def lol_live_game(self, ctx, nickname: str):
        """
        Command used to check player's live game along with information about enemies and teammates
        :param ctx: passing context of the command
        :param nickname: nickname of the player we want to find
        """
        channel_check = None
        settings_cog = self.client.get_cog("SettingsCommands")
        if settings_cog is not None:
            channel_check = await settings_cog.channel_check(ctx, ctx.channel.id)
        if not channel_check:
            return
        team = team_champs = team_ranks = []  # initialize empty lists for further storage of players
        # check the latest version of League of Legends
        latest = self.watcher.data_dragon.versions_for_region('eune')['n']['champion']
        # access data from external file contains information about characters in League of Legends
        static_champ_list = self.watcher.data_dragon.champions(latest, False, 'en_US')
        champ_dict = {}  # initialize empty dictionary contains data about characters in League of Legends.
        # iterate over every champion to assign them to corresponding champion's ID
        for key in static_champ_list['data']:
            row = static_champ_list['data'][key]
            champ_dict[row['key']] = row['id']
        summoner = self.watcher.summoner.by_name(self.region, nickname)
        if not summoner:
            await ctx.send(f"Can't find summoner{nickname}")
            return
        # acces data about player's live game
        live_game = self.watcher.spectator.by_summoner(self.region, summoner['id'])
        if not live_game:  # check if the game exists
            await ctx.send(f"{nickname}'s not in game")
            return  # return if player's not in game
        for participant in live_game['participants']:  # iterate over every participant in match to access their data.
            # assign champion's name based on their ID using dictionary that we made
            participant['championId'] = champ_dict[str(participant['championId'])]
            summoner_in_game = self.watcher.summoner.by_name(self.region, participant['summonerName'])
            summoner_rank = self.watcher.league.by_summoner(self.region, summoner_in_game['id'])
            if summoner_rank:  # check if player has rank in League of Legends
                # check queue type of the live game to determine what rank to show
                if live_game['gameQueueConfigId'] == 440:
                    q_type = "RANKED_FLEX_SR"
                else:
                    q_type = "RANKED_SOLO_5x5"
                if summoner_rank[0]['queueType'] == q_type:
                    q_operator = 0
                elif summoner_rank[1]['queueType'] == q_type:
                    q_operator = 1
                flex_emoji, solo_emoji = await self.lol_rank_check(ctx, summoner_rank)
                rank = f"{solo_emoji} {summoner_rank[q_operator]['tier']} {summoner_rank[q_operator]['rank']} | {summoner_rank[q_operator]['leaguePoints']} LP"
                team_ranks.append(rank)  # add player's rank to the list of participants ranks
            else:
                rank = "Unranked"
                team_ranks.append(rank)
                # add player's champion to the list of participants champions
                team_champs.append(participant['championId'])
                team.append(participant['summonerName'])  # add player to the list of participants
        if q_type == "RANKED_FLEX_5x5":
            q_type = 'Ranked Flex'
        else:
            q_type = 'Ranked Solo/Duo'
        embed = discord.Embed(
            color=0x11f80d,
            title="👨‍🦽 League of Legends Live 👨‍🦽",
            description=f"{nickname}'s **{q_type}** live game"
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
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="lol_time",
        description="Show member's online time on League of Legends",
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
    async def lol_time(self, ctx, member):
        mongo_client = MongoClient(os.getenv('MONGOURL'))
        db = mongo_client['Discord_Bot_Database']
        collection = db['members']
        if not collection.count_documents({"_id": member.id}):
            await ctx.send(f"{member.mention} is a Bot, or isn't in our Database yet!")
            return
        time_online = collection.find_one({"_id": member.id}, {"league_time": 1})
        if time_online['league_time'].second <= 0 or time_online['league_time'] == 0:
            await ctx.send(f"{member.mention} hasn't played League of Legends")
        elif time_online['league_time'].second > 0 and time_online['league_time'].minute < 1:
            await ctx.send(
                f"{member.mention} was playing League of Legends for **{time_online['league_time'].second}** seconds so far! (from 07.02.2022)")
        elif time_online['league_time'].minute > 0 and time_online['league_time'].hour < 1:
            await ctx.send(
                f"{member.mention} was playing League of Legends for **{time_online['league_time'].minute}m {time_online['league_time'].second}s** so far! (from 07.02.2022)")
        elif time_online['league_time'].hour > 0 and time_online['league_time'].day < 2:
            await ctx.send(
                f"{member.mention} was playing League of Legends for **{time_online['league_time'].hour}h {time_online['league_time'].minute}m {time_online['league_time'].second}s** so far! (from 07.02.2022)")
        elif time_online['league_time'].day >= 2:
            await ctx.send(
                f"{member.mention} was playing League of Legends for **{time_online['league_time'].day}d {time_online['league_time'].hour}h {time_online['league_time'].minute}m {time_online['league_time'].second}s** so far! (from 07.02.2022)")


def setup(client):  # adding cog to our main.py file
    client.add_cog(LolCommands(client))
