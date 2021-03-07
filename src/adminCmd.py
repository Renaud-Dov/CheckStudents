from src.data import *
from src import Embed
from src.tools import Tools
from discord.ext import commands


class Admin:
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    async def prefix(context, arg):
        data = Server(context.guild.id)
        try:
            data.prefix = arg
            embed = Embed.BasicEmbed(color=discord.Colour.orange(),
                                     title=data.returnLanguage("newPrefix") + f"**{arg}**",
                                     description="You still can use \"`.Check `\"")
            await Tools.AdminCommand(context, embed)

            data.Save_Settings()
        except commands.errors.MissingRequiredArgument:
            await Tools.SendError(context.channel, "You did not specify a prefix")

    @staticmethod
    async def language(context, lang=None):
        if lang not in ["fr", "en", "de"]:
            await Tools.SendError(context.channel,
                                  "Unknown language:\n**Languages :**\n• English: en\n• French: fr\n• German: de")
            return None

        data = Server(context.guild.id)
        data.language = lang
        embed = Embed.BasicEmbed(color=discord.Colour.orange(), title=data.returnLanguage("changeLanguage"))

        await Tools.AdminCommand(context, embed)
        data.Save_Settings()

    @staticmethod
    async def ShowPresents(context):
        """
            Activate/Deactivate Show presents students in call summary
        """
        data = Server(context.guild.id)

        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Call summary will only show absents students" if data.showPresents else "Call summary will show absents and presents students")

        data.showPresents = not data.showPresents

        data.Save_Settings()
        await Tools.AdminCommand(context, embed)

    @staticmethod
    async def Reset(context):
        data = Server(context.guild.id)
        if not Tools.got_the_role(data.admin, context.author) and context.message.author != context.guild.owner:
            await Tools.SendError(context.channel, data.returnLanguage("NoPrivileges"))
            return None

        data.Reset()
        data.Save_Settings()

        embed = Embed.BasicEmbed(color=discord.Colour.orange(),
                                 title="**__Factory reset:__**\nLanguage set to English\nAdmins and teachers list "
                                       "reseted\n**Prefix :** `.Check`\n**Show presents students, Sys Messages and "
                                       "Private Messages :** Activated\nDelay for for late students after a call : "
                                       "10 minutes")

        await Tools.AdminCommand(context, embed)

    @staticmethod
    async def sysMessages(context):
        """
        Activate/Deactivate system message
        """
        data = Server(context.guild.id)

        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="System Messages are now disabled" if data.showPresents else "System Messages are now activated")

        data.sysMessages = not data.sysMessages
        data.Save_Settings()

        await Tools.AdminCommand(context, embed)

    @staticmethod
    async def DeactivateMP(context):
        data = Server(context.guild.id)

        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Private messages are now disabled" if data.showPresents else "Private messages are now disabled")
        data.mp = not data.mp
        data.Save_Settings()

        await Tools.AdminCommand(context, embed)

    @staticmethod
    async def Delay(context, delay: str):
        data = Server(context.guild.id)

        try:
            delay = int(delay)
            if delay < 0 or delay > 60:
                raise ValueError
            data.delay = delay

            embed = Embed.BasicEmbed(color=discord.Color.red(), title=f"New delay : **{delay} minutes**")

            data.Save_Settings()
            await Tools.AdminCommand(context, embed)
        except ValueError:
            await Tools.SendError(context.channel,
                                  "Value must be between 0 and 60 minutes\nEnter 0 if you do not want to have any delay")
