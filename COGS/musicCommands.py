import yt_dlp as youtube_dl
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
import asyncio
import logging
from async_timeout import timeout
# Setting up logger for the MusicCommands Cog
logger = logging.getLogger("BotLogger")


class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []  # Queue for songs
        self.cookies_file = 'yt_cookies.txt'  # Path to the cookies file

    @nextcord.slash_command(name="play", description="Play a song from YouTube")
    async def play(self, interaction: Interaction, url: str):
        """Play a song from YouTube."""
        await interaction.response.defer()
        logger.info(f"{interaction.user} is trying to play a song...")
        if not interaction.user.voice:
            await interaction.response.send_message("You need to join a voice channel first!", ephemeral=True)
            logger.warning(f"{interaction.user} tried to play a song but is not in a voice channel.")
            return
        
        logger.info(f"Bot is trying to connect to a voice channel...")
        try:
            channel = interaction.user.voice.channel
        except Exception as ex:
            logger.error(f"There was an error while getting channel: Error message: {str(ex)}")
            return

        if not interaction.guild.voice_client:
            logger.info(f"Bot was not connected to voice channel and now is attempting a connection...")
            try:
                async with timeout(10):
                    await channel.connect()
            except asyncio.TimeoutError:    
                logger.error(f"Connection to the voice channel timed out")
                await interaction.response.send_message(f"Timeout")    
            except Exception as ex:
                logger.error(f"There was an error connecting to voice channel: {str(e)}")
                await interaction.response.send_message(f"Failed: {str(e)}")
            logger.info(f"Bot connected to voice channel: {channel.name}.")

        logger.info(f"ytdlp settings start")
        ydl_options = {
            'format': 'bestaudio/best',
            'quiet': True,
            'noplaylist': True,
            'cookies': self.cookies_file
        }
        logger.info(f"ytdlp settings final")
        # Send an initial response to indicate the bot is working
        #logger.info(f"Bot is trying to send a processing request message...")
        #try:
        #    await interaction.response.send_message("Processing your request...")
        #except Exception as ex:
        #    logger.error(f"There was an error while sending response message. Error message: {str(ex)} ")
        #    return
        
        logger.info(f"Bot is trying to stream URL from YouTube...")
        try:
            # Use yt-dlp to get the stream URL
            with youtube_dl.YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info['url']
                self.queue.append({'title': info['title'], 'url': audio_url})
                logger.info(f"Added song to queue: {info['title']}.")

                if len(self.queue) == 1:  # If no song is currently playing
                    await self.play_next(interaction)

                # Edit the original interaction response with the song title
                await interaction.edit_original_message(content=f"Added to queue: {info['title']}")
        except Exception as e:
            # Edit the original interaction response with the error message
            await interaction.edit_original_message(content=f"Error playing the audio: {str(e)}")
            logger.error(f"Error playing the song: {str(e)}")

    async def play_next(self, interaction: Interaction):
        if len(self.queue) > 0:
            song = self.queue[0]
            source = await nextcord.FFmpegOpusAudio.from_probe(
                song['url'],
                **{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            )
            interaction.guild.voice_client.play(source, after=lambda e: self.song_finished(interaction))
            logger.info(f"Now playing: {song['title']}.")

    def song_finished(self, interaction: Interaction):
        if len(self.queue) > 0:
            finished_song = self.queue.pop(0)
            logger.info(f"Finished playing: {finished_song['title']}.")

        if len(self.queue) > 0:
            asyncio.run_coroutine_threadsafe(self.play_next(interaction), self.bot.loop)

    @nextcord.slash_command(name="skip", description="Skip the current song")
    async def skip(self, interaction: Interaction):
        """Skip the current song"""
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("Skipped the current song.")
            logger.info(f"Skipped the current song in the queue.")
        else:
            await interaction.response.send_message("No song is currently playing.")
            logger.warning(f"{interaction.user} tried to skip but no song is playing.")

    @nextcord.slash_command(name="queue", description="Show the current song queue")
    async def queue_list(self, interaction: Interaction):
        """Show the current song queue"""
        if not self.queue:
            await interaction.response.send_message("The queue is currently empty.")
            logger.info(f"{interaction.user} checked the queue, but it was empty.")
        else:
            queue_message = "\n".join([f"{idx + 1}. {song['title']}" for idx, song in enumerate(self.queue)])
            await interaction.response.send_message(f"Current queue:\n{queue_message}")
            logger.info(f"{interaction.user} checked the queue.")

    @nextcord.slash_command(name="stop", description="Stop the music and disconnect")
    async def stop(self, interaction: Interaction):
        """Stop the music and disconnect"""
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            self.queue.clear()
            await interaction.response.send_message("Stopped the music and disconnected.")
            logger.info(f"Music stopped and bot disconnected from the voice channel.")
        else:
            await interaction.response.send_message("No bot is connected to a voice channel.")
            logger.warning(f"{interaction.user} tried to stop music but bot was not in a voice channel.")


def setup(bot):
    bot.add_cog(MusicCommands(bot))
