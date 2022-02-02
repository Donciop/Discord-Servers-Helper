from discord.ext import commands
import json


class SettingsCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def load_json_dict(self, filepath: str):
        if not filepath:
            return
        with open(filepath) as file:
            temp_dict = file.read()
            final_dict = json.loads(temp_dict)
            file.close()
        return final_dict


def setup(client):
    client.add_cog(SettingsCommands(client))
