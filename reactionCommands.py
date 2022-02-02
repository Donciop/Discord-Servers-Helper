from discord.ext import commands


class ReactionCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """ Event handler for handling reactions to messages. Here's used to assign roles based on reaction. """
        guild = await self.client.fetch_guild(payload.guild_id)  # get information about member and member's server
        member = await guild.fetch_member(payload.user_id)
        role = None
        # check if we react to desired message
        if payload.channel_id == 748120165001986128 and payload.message_id == 884555735671918642:
            # switch-case for every emote / every role.
            if str(payload.emoji) == "❌":
                role = guild.get_role(877347765519253544)
            if str(payload.emoji) == "1️⃣":
                role = guild.get_role(757291879195738322)
            if str(payload.emoji) == "2️⃣":
                role = guild.get_role(815411542735847434)
            if str(payload.emoji) == "3️⃣":
                role = guild.get_role(820002632822292491)
            if str(payload.emoji) == "🎸":
                role = guild.get_role(883802534580457522)
            if role is not None:
                await payload.member.add_roles(role)  # add role to member
                print(f"Added {role} to {member}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """ Event handler for handling reactions to messages. Here's used to remove unwanted roles. """
        guild = await self.client.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        role = None
        if payload.channel_id == 748120165001986128 and payload.message_id == 884555735671918642:
            if str(payload.emoji) == "❌":
                role = guild.get_role(877347765519253544)
            if str(payload.emoji) == "1️⃣":
                role = guild.get_role(757291879195738322)
            if str(payload.emoji) == "2️⃣":
                role = guild.get_role(815411542735847434)
            if str(payload.emoji) == "3️⃣":
                role = guild.get_role(820002632822292491)
            if str(payload.emoji) == "🎸":
                role = guild.get_role(883802534580457522)
            if role is not None:
                await member.remove_roles(role)  # remove role from member
                print(f"Removed {role} from {member}")


def setup(client):
    client.add_cog(ReactionCommands(client))
