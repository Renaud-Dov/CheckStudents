import discord

from src import Embed
from src.data import Server
from src.tools import Tools


async def ListRoles(context, value: str):
    embed = Embed.BasicEmbed(color=discord.Colour.orange())
    if value == "teacher":
        role = Server(context.guild.id).teacher
    elif value == "admin":
        role = Server(context.guild.id).admin

    if not role["roles"] and not role["users"]:
        embed.add_field(name=f"**{value} :**", value=f"There is no {value} yet")
    else:
        if role["roles"]:
            message = ""
            for i in role["roles"]:
                message += f"<@&{i}>\n"
            embed.add_field(name=f"**{value.capitalize()} roles :**", value=message)

        if role["users"]:
            message = ""
            for i in role["users"]:
                message += f"<@{i}>\n"
            embed.add_field(name=f"**{value.capitalize()} users :**", value=message)
    await context.channel.send(embed=embed)


async def addRole(context, value):
    server = Server(context.guild.id)
    a = Tools.got_the_role(server.admin, context.author)
    if (server.admin["roles"] != [] or server.admin["users"] != []) and not Tools.got_the_role(server.admin,
                                                                                               context.author):
        await Tools.SendError(context.channel, server.returnLanguage("NoPrivileges"))
    else:
        embed = Embed.BasicEmbed(color=discord.Colour.orange())

        added_roles = str()
        already_added_roles = str()

        added_user = str()
        already_added_user = str()

        if value == "teacher":
            roles = server.teacher
        elif value == "admin":
            roles = server.admin

        for role in context.message.role_mentions:

            if role.id not in roles["roles"]:
                roles["roles"].append(role.id)
                added_roles += role.mention + "\n"
            else:
                already_added_roles += role.mention + "\n"

        for user in context.message.mentions:
            if user.id not in roles["users"]:
                roles["users"].append(user.id)
                added_user += user.mention + "\n"
            else:
                already_added_user += user.mention + "\n"

        if added_roles == "" and already_added_roles == "" and added_user == "" and already_added_user == "":
            await Tools.SendError(context.channel, "You need to add roles or users to use the command")
        else:
            if added_roles != "":
                embed.add_field(name="Added roles", value=added_roles)
            if already_added_roles != "":
                embed.add_field(name="Roles already added", value=already_added_roles)

            if added_user != "":
                embed.add_field(name="Added users", value=added_user)
            if already_added_user != "":
                embed.add_field(name="Users already added", value=already_added_user)

            server.Save_Settings()
            await Tools.AdminCommand(context, embed, "Add teacher Command")


async def rmRole(context, value):
    server = Server(context.guild.id)

    embed = Embed.BasicEmbed(color=discord.Colour.orange())

    removed_roles = ""
    not_removed_roles = ""

    removed_users = ""
    not_removed_users = ""

    if value == "teacher":
        roles = server.teacher
    elif value == "admin":
        roles = server.admin

    for role in context.message.role_mentions:
        if role.id in roles["roles"]:
            removed_roles += role.mention + "\n"
            roles["roles"].remove(role.id)
        else:
            not_removed_roles += role.mention + "\n"

    for user in context.message.mentions:
        if user.id in roles["users"]:
            removed_users += user.mention + "\n"
            roles["users"].remove(user.id)
        else:
            not_removed_users += user.mention + "\n"

    if removed_roles == "" and not_removed_roles == "" and removed_users == "" and not_removed_users == "":
        await Tools.SendError(context.channel, "You need to write role or user in order to use the command")
    else:
        if removed_roles != "":
            embed.add_field(name="Removed roles", value=removed_roles)
        if not_removed_roles != "":
            embed.add_field(name=f"Was not an {value} role", value=not_removed_roles)

        if removed_users != "":
            embed.add_field(name="Removed users", value=removed_users)
        if not_removed_users != "":
            embed.add_field(name=f"Was not an {value} user", value=not_removed_users)
        server.Save_Settings()
        await Tools.AdminCommand(context, embed, "Remove Command")
