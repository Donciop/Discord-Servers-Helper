# Discord Servers Helper
Basic Discord Bot to help maintain small Discord servers.

## Purpose of this bot

I've created Discord Servers Heleper for my small town community to better maintain our Discord server. It started out with very basic commands like ``*mute`` or ``*msg_count`` but it grew alot from that.

Along with commands to moderate server, main goal is to focus on commands that are integrated with external API's for ex. **RIOT API**.

## API Features

- Local leaderboard for Teamfight Tactics® by Riot Games
- Data collection and simple analytics about your match history in Teamfight Tactics®
- Simple quality-of-life commands to quickly access specific data from League of Legends® by Riot Games
- Simple usage of local database to store information about players

![image](https://user-images.githubusercontent.com/39534836/149308416-7e97fe6e-4ebf-469b-abcc-37597436bad0.png)

## Moderation Features

- Quality-of-life commands that speed up moderation process of Discord server
- Adding certain functions that Discord does not provide, for ex. mass deleting messages
- Simple data collection and local leaderboards for messages sent
- Simple search function to help locate specific keywords
- Error handling for wrong usage of commands

![image](https://user-images.githubusercontent.com/39534836/149313050-4dd996e4-7603-490e-8101-46d4bb485ccd.png)


## Slash commands

With recent changes, now you can use **slash commands** for more intuitive way of using commands.

![image](https://user-images.githubusercontent.com/39534836/149313172-47325447-56af-4ec7-8bc9-21f7ec8ecd56.png)

## Tech used

- [Discord.py](https://github.com/Rapptz/discord.py) - A modern, easy to use, feature-rich, and async ready API wrapper for Discord written in Python.
- [Discord.interactions](https://discord-py-slash-command.readthedocs.io/en/latest/index.html) - a Python library for the Discord Artificial Programming Interface (used for slash commands).
- [TinyDB](https://tinydb.readthedocs.io/en/latest/) - Tiny, document oriented database.
- [RiotWatcher](https://riot-watcher.readthedocs.io/en/latest/) - RiotWatcher is a thin wrapper on top of the Riot Games API for League of Legends.
- [Heroku](https://dashboard.heroku.com/apps) - A platform as a service (PaaS) that enables developers to build, run, and operate applications entirely in the cloud.

## Code example

Simple channel check to prevent spam on for ex. general channel

```sh
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
```
## Adding bot to your server

You can add this bot directly to your Discord server here: [Add me!](https://discord.com/api/oauth2/authorize?client_id=930972990311641138&permissions=8&scope=bot%20applications.commands) or you can join our [Discord server](https://discord.gg/e5daMkFVJP) directly to maybe ask some questions!

However, this bot is not fully configured for being on multiple servers. It's still in early development. If you really want this bot on your Discord server, feel free to contact.
