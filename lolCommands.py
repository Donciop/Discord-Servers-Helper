import discord
import os
import typing
import json
from riotwatcher import LolWatcher
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
from main import client


class LolCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.newsChannel = client.get_channel(748120165001986128)
        self.botChannel = client.get_channel(888056072538042428)
        self.testChannel = client.get_channel(902710519646015498)
        self.owner = client.get_user(198436287848382464)
        self.guild = client.get_guild(218510314835148802)
        self.watcher = LolWatcher(os.getenv('APIKEYLOL'))
        self.region = 'eun1'
        self.logoFilepath = "Media/LOL-logo.jpg"

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lol_rank_check(self, summoner_rank):
        with open("JsonData/rankDict.json") as rankDict:
            rank_dict_json = rankDict.read()
            rank_dict = json.loads(rank_dict_json)
        tier_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
        flex_emoji = None
        solo_emoji = None
        for q_type in summoner_rank:
            if q_type['queueType'] == 'RANKED_TFT_PAIRS':
                continue
            for tier in tier_list:
                if q_type['tier'] == tier:
                    if q_type['queueType'] == 'RANKED_FLEX_SR':
                        flex_emoji = rank_dict[tier]
                    else:
                        solo_emoji = rank_dict[tier]
        return solo_emoji, flex_emoji

    @cog_ext.cog_slash(
        name="lol_rank",
        description="Check a specific player's Teamfight Tactics rank",
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
    async def lol_rank(self, ctx, nickname: str):
        me = self.watcher.summoner.by_name(self.region, nickname)
        if not me:
            await ctx.send(f"Can't find summoner {nickname}")
            return
        me_ranked_stats = self.watcher.league.by_summoner(self.region, me['id'])
        if not me_ranked_stats or (len(me_ranked_stats) == 1 and me_ranked_stats[0]['queueType'] == 'RANKED_TFT_PAIRS'):
            await ctx.send(f"{nickname} is unranked")
            return
        embed = discord.Embed(
            color=0x11f80d,
            title="👨‍🦽 League of Legends Rank 👨‍🦽",
            description=f"{nickname}'s ranked stats"
        )
        file = discord.File(
            self.logoFilepath,
            filename="image.jpg"
        )
        embed.set_thumbnail(url="attachment://image.jpg")
        solo_emoji, flex_emoji = await self.lol_rank_check(me_ranked_stats)
        for qType in me_ranked_stats:
            if qType['queueType'] == 'RANKED_TFT_PAIRS':
                continue
            if qType['queueType'] == "RANKED_FLEX_SR":
                qType['queueType'] = "RANKED FLEX"
                tier_emoji = flex_emoji
            elif qType['queueType'] == "RANKED_SOLO_5x5":
                qType['queueType'] = "RANKED SOLO/DUO"
                tier_emoji = solo_emoji
            if tier_emoji is None:
                embed.add_field(
                    name="Unranked",
                    value="\u200B",
                    inline=False
                )
            else:
                winrate = round((qType['wins'] / (qType['wins'] + qType['losses'])) * 100)
                embed.add_field(
                    name=f"{qType['queueType']}",
                    value=f"{tier_emoji} {qType['tier']} {qType['rank']} | {qType['leaguePoints']} LP with {winrate}% winrate({qType['wins']}W {qType['losses']}L)",
                    inline=False
                )
        await ctx.send(
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
        if nickname:
            team = []
            team_champs = []
            team_ranks = []
            latest = self.watcher.data_dragon.versions_for_region('eune')['n']['champion']
            static_champ_list = self.watcher.data_dragon.champions(latest, False, 'en_US')
            champ_dict = {}
            for key in static_champ_list['data']:
                row = static_champ_list['data'][key]
                champ_dict[row['key']] = row['id']
            summoner = self.watcher.summoner.by_name(self.region, nickname)
            if not summoner:
                await ctx.send(f"Can't find summoner{nickname}")
                return
            print("Here!")
            live_game = self.watcher.spectator.by_summoner(self.region, summoner['id'])
            if not live_game:
                await ctx.send(f"{nickname}'s not in game")
                return
            for participant in live_game['participants']:
                participant['championId'] = champ_dict[str(participant['championId'])]
                summoner_in_game = self.watcher.summoner.by_name(self.region, participant['summonerName'])
                summoner_rank = self.watcher.league.by_summoner(self.region, summoner_in_game['id'])
                if summoner_rank:
                    if live_game['gameQueueConfigId'] == 440:
                        q_type = "RANKED_FLEX_SR"
                    else:
                        q_type = "RANKED_SOLO_5x5"
                    if summoner_rank[0]['queueType'] == q_type:
                        q_operator = 0
                    elif summoner_rank[1]['queueType'] == q_type:
                        q_operator = 1
                    flex_emoji, solo_emoji = await self.lol_rank_check(summoner_rank)
                    rank = f"{solo_emoji} {summoner_rank[q_operator]['tier']} {summoner_rank[q_operator]['rank']} | {summoner_rank[q_operator]['leaguePoints']} LP"
                    team_ranks.append(rank)
                else:
                    rank = "Unranked"
                    team_ranks.append(rank)
                    team_champs.append(participant['championId'])
                    team.append(participant['summonerName'])
            if q_type == "RANKED_FLEX_5x5":
                q_type = 'Ranked Flex'
            else:
                q_type = 'Ranked Solo/Duo'
            embed = discord.Embed(
                color=0x11f80d,
                title="👨‍🦽 League of Legends Live 👨‍🦽",
                description=f"{nickname}'s **{q_type}** live game"
            )
            embed.add_field(
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
        else:
            await ctx.send("You have to type nickname!")


def setup(client):
    client.add_cog(LolCommands(client))
