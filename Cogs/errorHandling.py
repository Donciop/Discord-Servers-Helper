import nextcord
from nextcord.ext import commands, application_checks
from Cogs.settingsCommands import SettingsCommands


class ErrorHandling(commands.Cog):
    def __init__(self, client):
        self.client = client


@commands.Cog.listener()
async def on_application_command_error(interaction: nextcord.Interaction, error):
    if isinstance(error, application_checks.ApplicationMissingPermissions):
        missing_perms = await SettingsCommands.format_missing_permissions(error)
        await interaction.response.send_message(f'You don\'t have '
                                                f'{missing_perms}permissions to run this command')


@commands.Cog.listener()
async def on_command_error(ctx, error):
    """
    Error handling for exceptions when using commands. Called when bot encounters an error.

        Args:
            ctx: Context of the command
            error (nextcord.ext.commands.errors): Error that we're trying to catch

        Returns:
            None
    """
    if isinstance(error, commands.CommandOnCooldown):  # called when you try to use command that is on cooldown.
        await ctx.send(f"Command's on cooldown. Time remaining: {round(error.retry_after)}s")
        return

    if isinstance(error, commands.ChannelNotFound) or isinstance(error, commands.ChannelNotReadable):
        await ctx.send("Could not find channel", delete_after=5)

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Couldn't find that command, check for any spelling errors", delete_after=5)

    if isinstance(error, commands.MissingPermissions):  # called when you don't have permission to use that command.
        missing_perms = await SettingsCommands.format_missing_permissions(error)
        await ctx.send(f"You don't have {missing_perms} permissions to use this command, check *help for more info",
                       delete_after=5)

    if isinstance(error, commands.BotMissingPermissions):
        missing_perms = await SettingsCommands.format_missing_permissions(error)
        await ctx.send(f'Bot is missing permissions. '
                       f'Make sure that bot has permission to **{missing_perms}**', delete_after=5)


def setup(client):
    client.add_cog(ErrorHandling(client))
