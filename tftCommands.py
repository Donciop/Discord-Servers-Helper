import discord
import os
import asyncio
import json
from tinydb import TinyDB, Query
from riotwatcher import TftWatcher
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
from main import client


class TftCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.leagueChannel = client.get_channel(910557144573673522)
        self.penguFilepath = "Media/Pengu_TFT.png"
        self.tftIconFilepath = "Media/Teamfight_Tactics_icon.png"
        self.tftEmoji = "<:TFT:912917249923375114>"
        self.region = 'eun1'
        self.watcher = TftWatcher(os.getenv('APIKEYTFT'))
        self.purgeSeconds = 5
        self.db = TinyDB('JsonData/db.json')

    @commands.command()
    async def rank_check(self, summoner_rank):
        with open("JsonData/rankDict.json") as rank_dict:
            rank_dict_json = rank_dict.read()
            rank_dict = json.loads(rank_dict_json)
        tier_list = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
        rank_list = ["IV", "III", "II", "I"]
        q_type = 0
        rank = 0
        if summoner_rank[0]['queueType'] == 'RANKED_TFT_TURBO':
            q_type = 1
        for tier in tier_list:
            if summoner_rank[q_type]['tier'] != tier:
                rank += 400
            else:
                tier_emoji = rank_dict[tier]
                break
        for localRank in rank_list:
            if summoner_rank[q_type]['rank'] != localRank:
                rank += 100
            else:
                break
        rank += summoner_rank[q_type]['leaguePoints']
        return tier_emoji, rank

    @commands.command()
    async def channel_check(self, channel):
        bot_channel = client.get_channel(888056072538042428)
        test_channel = client.get_channel(902710519646015498)
        if channel != bot_channel.id and channel != test_channel.id and channel != self.leagueChannel.id:
            channel_check = False
            our_channel = client.get_channel(channel)
            await our_channel.send(f"Please, use bot commands in {self.leagueChannel.mention} channel to prevent spam")
            await asyncio.sleep(self.purgeSeconds)
            await our_channel.purge(limit=2)
        else:
            channel_check = True
        return channel_check

    @cog_ext.cog_slash(
        name="tft_rank",
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
    async def tft_rank(self, ctx, nickname: str):
        channel_check = await self.channel_check(ctx.channel.id)
        if not channel_check:
            return
        summoner = self.watcher.summoner.by_name(self.region, nickname)
        if not summoner:
            await ctx.send(f"Can't find **{nickname}** on EUNE server.")
            return
        summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])
        if not summoner_tft_stats:
            await ctx.send(f"Player **{nickname}** is unranked on TFT")
            return
        title_nickname = nickname.lower()
        title_nickname = title_nickname.replace(" ", "")
        embed = discord.Embed(
          color=0x11f80d,
          title=f"🎲 Teamfight Tactics {nickname}'s Rank 🎲",
          description="Click the title for advanced information",
          url=f"https://lolchess.gg/profile/eune/{title_nickname}"
        )
        file = discord.File(self.penguFilepath, filename="image.png")
        embed.set_thumbnail(url="attachment://image.png")
        tier_emoji, rank = await self.rank_check(summoner_tft_stats)
        q_type = 0
        if summoner_tft_stats[0]['queueType'] == 'RANKED_TFT_TURBO':
            q_type = 1
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
        if self.db.search(Query().nickname == nickname):
            await ctx.send(f"Player **{nickname}** already exists in database")
            return
        else:
            tier_emoji, ranking = await self.rank_check(summoner_tft_stats)
            self.db.insert({'nickname': nickname, })
            self.db.update_multiple([
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
        channel_check = await self.channel_check(ctx.channel.id)
        if not channel_check:
            return
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You don't have permission to delete users from database, ask administrators or moderators")
            return
        if self.db.search(Query().nickname == nickname):
            self.db.remove(Query().nickname == nickname)
            await ctx.send(f"You have deleted **{nickname}** from database")
        else:
            await ctx.send(f"Can't find **{nickname}** in database")

    @cog_ext.cog_slash(
        name="tft_ranking",
        description="Show server's Teamfight Tactics leaderboard",
        guild_ids=[218510314835148802]
    )
    async def tft_ranking(self, ctx):
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
        leaderboard_not_sorted = {}
        await ctx.defer()
        for record in self.db:
            q_type = 0
            summoner = self.watcher.summoner.by_name(self.region, record['nickname'])
            summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])
            if summoner_tft_stats[0]['queueType'] == 'RANKED_TFT_TURBO':
                q_type = 1
            tier_emoji, ranking = await self.rank_check(summoner_tft_stats)
            self.db.update_multiple([
              ({'matchesPlayed': (summoner_tft_stats[q_type]['wins']+summoner_tft_stats[q_type]['losses'])}, Query().nickname == record['nickname']),
              ({'rank': summoner_tft_stats[q_type]['rank']}, Query().nickname == record['nickname']),
              ({'tier': summoner_tft_stats[q_type]['tier']}, Query().nickname == record['nickname']),
              ({'leaguePoints': summoner_tft_stats[q_type]['leaguePoints']}, Query().nickname == record['nickname']),
              ({'tierEmoji': tier_emoji}, Query().nickname == record['nickname']),
              ({'wins': summoner_tft_stats[q_type]['wins']}, Query().nickname == record['nickname'])
            ])
            leaderboard_not_sorted[f"{record['nickname']}"] = [ranking]
        leaderboard_sorted = sorted(
          leaderboard_not_sorted.items(),
          key=lambda x: x[1],
          reverse=True
        )
        iterator = 1
        for player in leaderboard_sorted:
            player_stats = self.db.search(Query().nickname == player[0])
            if iterator == 1:
                rank_emoji = ":first_place:"
            elif iterator == 2:
                rank_emoji = ":second_place:"
            elif iterator == 3:
                rank_emoji = ":third_place:"
            else:
                rank_emoji = None
            if rank_emoji is not None:
                embed.add_field(
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
                option_type=4,
                required=True
            )
        ]
    )
    async def tft_stats(self, ctx, nickname: str, number_of_matches: int):
        channel_check = await self.channel_check(ctx.channel.id)
        if not channel_check:
            return
        if number_of_matches >= 500 or number_of_matches <= 0:
            await ctx.send(f"Wrong number of matches! Try between 0 - 500")
            return
        count = number_of_matches
        summoner = self.watcher.summoner.by_name(self.region, nickname)
        if not summoner:
            await ctx.send(f"Can't find summoner **{nickname}**")
            return
        summoner_tft_stats = self.watcher.league.by_summoner(self.region, summoner['id'])
        match_list = self.watcher.match.by_puuid("europe", summoner['puuid'], count)
        if not match_list:
            await ctx.send(f"**{nickname}** didn't played any Teamfight Tactics games")
            return
        with open("JsonData/allStats.json") as allStatsFile, open("JsonData/tftComps.json") as tftCompsFile:
            all_stats_json = allStatsFile.read()
            all_stats = json.loads(all_stats_json)
            comps_json = tftCompsFile.read()
            comps = json.loads(comps_json)
        await ctx.defer()
        for match in match_list:
            match_detail = self.watcher.match.by_id("europe", match)
            if match_detail['info']['tft_set_number'] != 6:
                break
            for participant in match_detail['info']['participants']:
                if participant['puuid'] == summoner['puuid']:
                    for trait in participant['traits']:
                        if trait['tier_current'] > 0:
                            comps[str(trait['name'])][0] += 1
                            if participant['placement'] <= 4:
                                comps[str(trait['name'])][1] += 1
                    if match_detail['info']['queue_id'] == 1090:
                        q_type = 'Normal'
                    elif match_detail['info']['queue_id'] == 1100:
                        q_type = 'Ranked'
                    elif match_detail['info']['queue_id'] == 1150:
                        q_type = 'Double Up'
                    else:
                        q_type = 'Hyper Roll'
                    all_stats[str(q_type)]['hasPlayed'] = True
                    all_stats[str(q_type)]['played'] += 1
                    all_stats[str(q_type)]['placements'] += participant['placement']
                    if participant['placement'] <= 4:
                        all_stats[str(q_type)]['top4'] += 1
                        if participant['placement'] == 1:
                            all_stats[str(q_type)]['winrate'] += 1
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
        for key in all_stats.keys():
            if all_stats[key]['hasPlayed']:
                embed.add_field(
                  name=f"{key}",
                  value=f"""
                  **{all_stats[key]['played']}** games played with avg. **{round(all_stats[key]['placements']/all_stats[key]['played'], 2)}** place
                  **{round((all_stats[key]['top4']/all_stats[key]['played'])*100, 2)}%** top 4 rate
                  **{round((all_stats[key]['winrate']/all_stats[key]['played'])*100, 2)}%** winrate
                  """,
                  inline=False
                )
        embed.add_field(
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


def setup(client):
    client.add_cog(TftCommands(client))
