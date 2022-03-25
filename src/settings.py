from typing import Union, List, Optional

import discord
from discord import app_commands, ui
from discord.app_commands import Choice
from discord.utils import MISSING

from src import Embed
from src.data import Server
from src.tools import Tools


# def is_admin():
#     async def predicate(interaction: discord.Interaction):
#         data = Server(interaction.guild_id)
#         if Tools.has_permission(data.admin, interaction.user) \
#                 or interaction.guild.owner_id == interaction.user.id:
#             return True
#         await Tools.SendError(interaction, "You are not an admin or the server owner, you can't do that.",
#                               ephemeral=True)
#         return False
#
#     return app_commands.check(predicate)

def is_admin(interaction: discord.Interaction):
    data = Server(interaction.guild_id)
    return Tools.has_permission(data.admin, interaction.user) or interaction.guild.owner_id == interaction.user.id


class Settings(app_commands.Group):
    admin = app_commands.Group(name='settings', description='settings commands')

    def __init__(self):
        super().__init__()

    # @is_admin()
    @app_commands.command(name='add', description='Add teacher/admin access to a user or role')
    @app_commands.describe(category="Category of permission")
    @app_commands.describe(role="Role or User to add")
    # @app_commands.autocomplete(category=complete)
    async def add(self, interaction: discord.Interaction, category: str, role: Union[discord.Role, discord.User]):
        server = Server(interaction.guild_id)

        embed = Embed.BasicEmbed(title=f"Added {category}", color=discord.Colour.orange())

        if category == "admin":
            roles = server.admin
        else:  # category == "teacher"
            roles = server.teacher

        if isinstance(role, discord.Role):
            if role.id in roles["roles"]:
                embed.add_field(name="Role already added", value=role.mention)
            else:
                roles["roles"].append(role.id)
                embed.add_field(name="Added role", value=role.mention)
        elif isinstance(role, discord.User) or isinstance(role, discord.Member):
            if role.id in roles["users"]:
                embed.add_field(name="User already added", value=role.mention)
            else:
                roles["users"].append(role.id)
                embed.add_field(name="Added user", value=role.mention)

        server.Save_Settings()
        await interaction.response.send_message(embed=embed)

    # @is_admin()
    @app_commands.command(name='remove', description='Remove teacher/admin access to a user or role')
    @app_commands.describe(category="Category of permission")
    @app_commands.describe(role="Role or User to remove")
    # @app_commands.autocomplete(category=complete)
    async def remove(self, interaction: discord.Interaction, category: str, role: Union[discord.Role, discord.User]):
        server = Server(interaction.guild_id)

        embed = Embed.BasicEmbed(title=f"Removed {category}", color=discord.Colour.orange())
        if category == "admin":
            roles = server.admin
        else:  # category == "teacher"
            roles = server.teacher

        if isinstance(role, discord.Role):
            if role.id not in roles["roles"]:
                embed.add_field(name="Role not added", value=role.mention)
            else:
                roles["roles"].remove(role.id)
                embed.add_field(name="Removed role", value=role.mention)
        elif isinstance(role, discord.User) or isinstance(role, discord.Member):
            if role.id not in roles["users"]:
                embed.add_field(name="User not added", value=role.mention)
            else:
                roles["users"].remove(role.id)
                embed.add_field(name="Removed user", value=role.mention)

        server.Save_Settings()
        await interaction.response.send_message(embed=embed)

    # @is_admin()
    @app_commands.command(name='list', description='List all users and roles with teacher/admin access')
    @app_commands.describe(category="Category of permission")
    # @app_commands.autocomplete(category=complete)
    async def list_admin(self, interaction: discord.Interaction, category: str):
        embed = Embed.BasicEmbed(title=f"{category} list", color=discord.Colour.orange())

        if category == "admin":
            perms = Server(interaction.guild_id).admin
        else:  # category == "teacher"
            perms = Server(interaction.guild_id).teacher
        if not perms["users"] and not perms["roles"]:
            embed.description = f"No {category} set. Use `/settings add` to add them first."
        if perms["roles"]:
            embed.add_field(name="Roles", value="\n".join([f"<@&{role}>" for role in perms["roles"]]))
        if perms["users"]:
            embed.add_field(name="Users", value="\n".join([f"<@{user}>" for user in perms["users"]]))

        await interaction.response.send_message(embed=embed)


def SettingsEmbed(interaction: discord.Interaction):
    data = Server(interaction.guild_id)
    embed = Embed.BasicEmbed(color=discord.Colour.orange(), title="Settings")

    embed.add_field(name="• Private Messages",
                    value="Private messages are now " + (
                        "enable. A message will be sent to evry absent students." if
                        data.mp else "disable. No message will be sent to absent students."),
                    inline=False)
    embed.add_field(name="• Show present students after call",
                    value="Present students message is now" + ("enabled" if data.showPresents else "disable"),
                    inline=False)
    embed.add_field(name="• Delay (in minutes)", value=str(data.delay), inline=False)
    embed.add_field(name="• Number of admins", value=str(data.sum_admin), inline=False)
    embed.add_field(name="• Number of teachers", value=str(data.sum_teacher), inline=False)

    return embed


class Home(discord.ui.View):
    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="Edit settings", style=discord.ButtonStyle.blurple, emoji="📝")
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin(interaction):
            embed = Embed.BasicEmbed(
                title="You don't have permission to do that. You need admin permission or to be the admin owner.",
                color=discord.Colour.red())
            await self.interaction.edit_original_message(
                embed=embed,
                view=Done(self.interaction, Home(self.interaction), SettingsEmbed(interaction)))
            await interaction.response.defer()
        else:
            await interaction.response.defer()
            await self.interaction.edit_original_message(view=Edit(self.interaction))


class Edit(discord.ui.View):

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple, emoji="⬅")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.interaction.edit_original_message(view=Home(self.interaction))
        await interaction.response.defer()

    @discord.ui.button(label="Reset all settings", style=discord.ButtonStyle.green)
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = Server(interaction.guild_id)
        data.Reset()
        data.Save_Settings()

        embed = Embed.BasicEmbed(color=discord.Colour.orange(),
                                 title="**__Factory reset:__**\nAdmins and teachers list "
                                       "reset\n**Show presents students, Sys Messages and "
                                       "Private Messages :** Activated\nDelay for for late students after a call : "
                                       "10 minutes")

        await self.interaction.edit_original_message(embed=embed,
                                                     view=Done(self.interaction, Edit(self.interaction),
                                                               SettingsEmbed(interaction)))
        await interaction.response.defer()

    @discord.ui.button(label="Set Delay", style=discord.ButtonStyle.green)
    async def setDelay(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SetDelay(self.interaction))

    @discord.ui.button(label="Activate/Deactivate system messages", style=discord.ButtonStyle.green)
    async def system(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = Server(interaction.guild.id)
        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Private messages are now disabled" if data.mp
                                 else "Private messages are now enabled")
        data.mp = not data.mp
        data.Save_Settings()

        await self.interaction.edit_original_message(embed=embed,
                                                     view=Done(self.interaction, Edit(self.interaction),
                                                               SettingsEmbed(interaction)))
        await interaction.response.defer()

    @discord.ui.button(label="Activate/Deactivate presents students", style=discord.ButtonStyle.green)
    async def presents(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = Server(interaction.guild_id)
        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Private messages are now disabled" if data.showPresents
                                 else "Private messages are now enabled")
        data.showPresents = not data.showPresents
        data.Save_Settings()

        await self.interaction.edit_original_message(embed=embed, view=Done(self.interaction, Edit(self.interaction),
                                                                            SettingsEmbed(interaction)))
        await interaction.response.defer()

    @discord.ui.button(label="Admin Access", style=discord.ButtonStyle.blurple, emoji="🔑")
    async def admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = Embed.BasicEmbed(color=discord.Color.orange(),
                                 title="**__Admin Access:__**\n",
                                 description="For the moment, new admin panel is still under development. Please use these commands instead.")
        embed.add_field(name="add", value="/settings add admin @role", inline=False)
        embed.add_field(name="remove", value="/settings remove admin @role", inline=False)
        embed.add_field(name="list", value="/settings list admin", inline=False)

        await self.interaction.edit_original_message(embed=embed,
                                                     view=Done(self.interaction, Edit(self.interaction),
                                                               SettingsEmbed(interaction)))
        await interaction.response.defer()

    @discord.ui.button(label="Teacher Access", style=discord.ButtonStyle.blurple, emoji="🎓")
    async def teacher(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = Embed.BasicEmbed(color=discord.Color.orange(),
                                 title="**__Teacher Access:__**\n",
                                 description="For the moment, new teacher panel is still under development. Please use these commands instead.")
        embed.add_field(name="add", value="/settings add teacher @role", inline=False)
        embed.add_field(name="remove", value="/settings remove teacher @role", inline=False)
        embed.add_field(name="list", value="/settings list teacher", inline=False)

        await self.interaction.edit_original_message(embed=embed,
                                                     view=Done(self.interaction, Edit(self.interaction),
                                                               SettingsEmbed(interaction)))
        await interaction.response.defer()


class Done(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, next_view: discord.ui.View,
                 next_embed: Optional[discord.Embed] = MISSING):
        super().__init__()
        self.next_view = next_view
        self.next_embed = next_embed
        self.interaction = interaction

    @discord.ui.button(label="OK", style=discord.ButtonStyle.blurple, emoji="✅")
    async def ok(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.interaction.edit_original_message(view=self.next_view, embed=self.next_embed)
        await interaction.response.defer()


class PermPanel(discord.ui.View):

    def __init__(self, category: str):
        """
        :param category: The category of the permissions (admin or teacher)
        """
        super().__init__()
        self.category = category

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple, emoji="⬅")
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.edit_original_message(view=Edit(), embed=SettingsEmbed(interaction))

    @discord.ui.button(label="Add", style=discord.ButtonStyle.green, emoji="➕")
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Remove", style=discord.ButtonStyle.red, emoji="➖")
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="List", style=discord.ButtonStyle.blurple, emoji="📋")
    async def list(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = Embed.BasicEmbed(title=f"{self.category} list", color=discord.Colour.orange())

        if self.category == "admin":
            perms = Server(interaction.guild_id).admin
        else:  # category == "teacher"
            perms = Server(interaction.guild_id).teacher
        if not perms["users"] and not perms["roles"]:
            embed.description = f"No {self.category} set."
        if perms["roles"]:
            embed.add_field(name="Roles", value="\n".join([f"<@&{role}>" for role in perms["roles"]]))
        if perms["users"]:
            embed.add_field(name="Users", value="\n".join([f"<@{user}>" for user in perms["users"]]))

        await interaction.channel.send(embed=embed, view=Done(Edit(), SettingsEmbed(interaction)))


class SetDelay(ui.Modal, title='Set Delay'):
    value = ui.TextInput(label='Delay (in minutes between 0 and 60 min)', default="10", style=discord.TextStyle.short,
                         required=True)

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        data = Server(interaction.guild_id)
        # if value is a number between 0 and 60
        if self.value.value.isdigit():
            value = int(self.value.value)
            if 0 <= value <= 60:

                data.delay = value
                data.Save_Settings()
                embed = Embed.BasicEmbed(color=discord.Color.red(), title=f"Value set to {value} minute(s)")
                await self.interaction.edit_original_message(embed=embed,
                                                             view=Done(self.interaction, Edit(self.interaction),
                                                                       SettingsEmbed(interaction)))
                await interaction.response.defer()
            else:
                embed = Embed.BasicEmbed(color=discord.Color.red(), title="Value must be between 0 and 60")
                await self.interaction.edit_original_message(embed=embed,
                                                             view=Done(self.interaction, Edit(self.interaction),
                                                                       SettingsEmbed(interaction)))
                await interaction.response.defer()
        else:
            embed = Embed.BasicEmbed(color=discord.Color.red(), title="Value must be a integer.")
            await self.interaction.edit_original_message(embed=embed,
                                                         view=Done(self.interaction, Edit(self.interaction),
                                                                   SettingsEmbed(interaction)))
            await interaction.response.defer()
