from typing import Union, List

import discord
from discord import app_commands

from src import Embed
from src.data import Server
from src.tools import Tools


def is_admin():
    async def predicate(interaction: discord.Interaction):
        data = Server(interaction.guild_id)
        if Tools.has_permission(data.admin, interaction.user) \
                or interaction.guild.owner_id == interaction.user.id:
            return True
        await Tools.SendError(interaction, "You are not an admin or the server owner, you can't do that.",
                              ephemeral=True)
        return False

    return app_commands.check(predicate)


class Settings(app_commands.Group):
    admin = app_commands.Group(name='settings', description='settings commands')

    def __init__(self):
        super().__init__()

    @staticmethod
    async def completeBool(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        permissions = ["true", "false"]
        return [app_commands.Choice(name=permission, value=permission) for permission in permissions if current.lower()]

    @staticmethod
    async def complete(interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        permissions = ["teacher", "admin"]
        return [app_commands.Choice(name=permission, value=permission) for permission in permissions if current.lower()]

    @is_admin()
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

    @is_admin()
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

    @is_admin()
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

    @app_commands.command(name="get", description="See actual settings")
    async def settings(self, interaction: discord.Interaction):
        data = Server(interaction.guild.id)
        embed = Embed.BasicEmbed(color=discord.Colour.orange(), title="Current settings")

        embed.add_field(name="• System Messages", value=str(data.sysMessages), inline=False)
        embed.add_field(name="• Private Messages", value=str(data.mp), inline=False)
        embed.add_field(name="• Show present students after call", value=str(data.showPresents), inline=False)
        embed.add_field(name="• Delay in minutes", value=str(data.delay), inline=False)

        await interaction.response.send_message(embed=embed)

    @is_admin()
    @app_commands.command(name="present", description="Show present students")
    @app_commands.describe(value="Do you want to show present students?")
    # @app_commands.autocomplete(value=completeBool)
    async def ShowPresents(self, interaction: discord.Interaction, value: str):
        data = Server(interaction.guild.id)
        value = bool(value)

        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Call summary will only show absents students" if value
                                 else "Call summary will show absents and presents students")

        data.showPresents = value

        data.Save_Settings()
        await interaction.response.send_message(embed=embed)

    @is_admin()
    @app_commands.command(description="Reset all settings")
    async def reset(self, interaction: discord.Interaction):
        data = Server(interaction.guild.id)

        data.Reset()
        data.Save_Settings()

        embed = Embed.BasicEmbed(color=discord.Colour.orange(),
                                 title="**__Factory reset:__**\nAdmins and teachers list "
                                       "reset\n**Show presents students, Sys Messages and "
                                       "Private Messages :** Activated\nDelay for for late students after a call : "
                                       "10 minutes")

        await interaction.response.send_message(embed=embed)

    @is_admin()
    @app_commands.command(description="Activate/Deactivate system message")
    @app_commands.describe(value="Do you want to activate system messages?")
    # @app_commands.autocomplete(value=completeBool)
    async def system(self, context, value: str):
        """
        Activate/Deactivate system message
        """
        data = Server(context.guild.id)
        value = bool(value)

        embed = Embed.BasicEmbed(color=discord.Color.orange(),
                                 title="System Messages are now disabled" if value
                                 else "System Messages are now activated")

        data.sysMessages = value
        data.Save_Settings()

        await context.channel.send(embed=embed)

    @is_admin()
    @app_commands.command(description="Activate/Deactivate private messages")
    @app_commands.describe(value="Do you want to activate private messages?")
    # @app_commands.autocomplete(value=completeBool)
    async def mp(self, interaction: discord.Interaction, value: str):
        data = Server(interaction.guild.id)
        value = bool(value)
        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Private messages are now disabled" if data.showPresents
                                 else "Private messages are now disabled")
        data.mp = value
        data.Save_Settings()

        await interaction.response.send_message(embed=embed)

    @is_admin()
    @app_commands.command(description="Set delay (in minutes). Default is 10 minutes")
    async def delay(self, context, delay: app_commands.Range[int, 0, 60] = 10):
        data = Server(context.guild.id)

        data.delay = delay
        embed = Embed.BasicEmbed(color=discord.Color.red(), title=f"New delay : **{delay} minutes**")

        data.Save_Settings()
        await context.channel.send(embed=embed)
