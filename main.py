import nextcord  # main packages
from nextcord.ext import commands
from logger import get_logger
import os  # utility packages

# Making sure the bot has all the permissions
intents = nextcord.Intents().all()

# Initialize bot
client = commands.Bot(command_prefix='*', intents=intents, help_command=None)

# Setting up logging
bot_logger = get_logger()

# Loading cogs
for filename in os.listdir("COGS"):  # iterate over files in 'COGS' dictionary
    if filename.endswith(".py"):
        client.load_extension(f"COGS.{filename[:-3]}")  # load cogs into bot
        bot_logger.info(f"Cog: {filename} loaded!")

# Starting bot
bot_logger.info("Bot is starting...")
client.run(os.getenv('ALPHATOKEN'))  # actually run the bot and pass the secret TOKEN
