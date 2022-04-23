import nextcord
from nextcord.ext import commands, application_checks

VIEW_NAME = "RoleView"


def custom_id(view: str, id: int):
    return f"{view}:{id}"


class RoleView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @staticmethod
    async def button_callback(button: nextcord.Button, interaction: nextcord.Interaction):
        role_id = int(button.custom_id.split(':')[-1])
        role = interaction.guild.get_role(role_id)
        assert isinstance(role, nextcord.Role)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f'Your {role.name} role has been removed', ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f'Role {role.name} has been added', ephemeral=True)

    @nextcord.ui.button(label='CS:GO', emoji='🔫', style=nextcord.ButtonStyle.primary,
                        custom_id=custom_id(VIEW_NAME, 820002632822292491))
    async def cs_button(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await self.button_callback(button, interaction)

    @nextcord.ui.button(label='R6 Siege', emoji='🔫', style=nextcord.ButtonStyle.primary,
                        custom_id=custom_id(VIEW_NAME, 877347765519253544))
    async def r6_button(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await self.button_callback(button, interaction)

    @nextcord.ui.button(label='Among Us', emoji='🚀', style=nextcord.ButtonStyle.green,
                        custom_id=custom_id(VIEW_NAME, 757291879195738322))
    async def amongus_button(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await self.button_callback(button, interaction)

    @nextcord.ui.button(label='Path of Exile', emoji='💍', style=nextcord.ButtonStyle.green,
                        custom_id=custom_id(VIEW_NAME, 933846670154793040))
    async def poe_button(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await self.button_callback(button, interaction)

    @nextcord.ui.button(label='Factorio', emoji='🧱', style=nextcord.ButtonStyle.green,
                        custom_id=custom_id(VIEW_NAME, 898565007565021225))
    async def factorio_button(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await self.button_callback(button, interaction)

    @nextcord.ui.button(label='Lost Ark', emoji='🔮', style=nextcord.ButtonStyle.danger,
                        custom_id=custom_id(VIEW_NAME, 943982583954427994))
    async def lost_ark_button(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await self.button_callback(button, interaction)

    @nextcord.ui.button(label='League of Legends', emoji='🦽', style=nextcord.ButtonStyle.danger,
                        custom_id=custom_id(VIEW_NAME, 815411542735847434))
    async def lol_button(self, button: nextcord.Button, interaction: nextcord.Interaction):
        await self.button_callback(button, interaction)


class ReactionCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        self.client.add_view(RoleView())

    @nextcord.slash_command(name='roles', guild_ids=[218510314835148802], force_global=True)
    @application_checks.has_permissions(administrator=True)
    async def roles(self, interaction: nextcord.Interaction):
        """
        Utility config method for #role channel. Needs OWNER permissions.

            Args:
               interaction (nextcord.Interaction): Context of the command

            Returns:
                None
        """
        embed = nextcord.Embed(title='💎 Wanatawka Reaction Roles',
                               description='React to add or remove any role You want')
        await interaction.response.send_message(embed=embed, view=RoleView())


def setup(client):
    client.add_cog(ReactionCommands(client))
