from typing import Union

from src.data import *
from src import Embed


class Tools:
    @staticmethod
    def has_permission(role: Union[dict, list, discord.Role, int], user: discord.Member):
        """
        Check if a user got at least one role in author list
        """

        if isinstance(role, dict):
            if user.id in role["users"]:
                return True
            for i in role["roles"]:
                if i in [y.id for y in user.roles]:
                    return True
            return False
        elif isinstance(role, list):
            for i in role:
                if i in [y.id for y in user.roles]:
                    return True
            return False
        elif isinstance(role, discord.Role):
            return role in user.roles
        elif isinstance(role, int):
            return role in [y.id for y in user.roles]

    @staticmethod
    async def SendError(interaction: discord.Interaction, message: str, desc: str = None, ephemeral: bool = True):
        embed = Embed.BasicEmbed(color=discord.Color.red(), title=message)
        # embed.add_field(name="Permission Denied",value=message)
        if desc is not None:
            embed.description = desc
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/remove.png")
        # embed.set_footer(text="Feel free to open a issue on Github")
        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

