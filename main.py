import nextcord  # main packages
from nextcord.ext import commands
import os  # utility packages

# Making sure the bot has all the permissions
intents = nextcord.Intents().all()

# Initialize bot
client = commands.Bot(command_prefix='*', intents=intents, help_command=None)

# Loading cogs
for filename in os.listdir("COGS"):  # iterate over files in 'COGS' dictionary
    print(filename)
    if filename.endswith(".py"):
        client.load_extension(f"COGS.{filename[:-3]}")  # load cogs into bot
        print("Cog Loaded!")

client.run(os.getenv('TOKEN'))  # actually run the bot and pass the secret TOKEN
