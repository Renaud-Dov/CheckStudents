from src.data import *
from src.tools import Tools


class Admin:
    @staticmethod
    async def addRole(context, value):
        guild = str(context.guild.id)
        data = readGuild(guild)
        a = Tools.got_the_role(data["admin"], context.author)
        if (data["admin"]["roles"] != [] or data["admin"]["users"] != []) and not Tools.got_the_role(data["admin"], context.author):
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))
        else:
            embed = discord.Embed(color=discord.Colour.orange())
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

            added_roles = ""
            already_added_roles = ""

            added_user = ""
            already_added_user = ""
            for role in context.message.role_mentions:

                if role.id not in data[value]["roles"]:
                    data[value]["roles"].append(role.id)
                    added_roles += role.mention + "\n"
                else:
                    already_added_roles += role.mention + "\n"

            for user in context.message.mentions:
                if user.id not in data[value]["users"]:
                    data[value]["users"].append(user.id)
                    added_user += user.mention + "\n"
                else:
                    already_added_user += user.mention + "\n"

            if added_roles != "" or already_added_roles != "" or added_user != "" or already_added_user != "":
                if added_roles != "":
                    embed.add_field(name="Added roles", value=added_roles)
                if already_added_roles != "":
                    embed.add_field(name="Roles already added", value=already_added_roles)

                if added_user != "":
                    embed.add_field(name="Added users", value=added_user)
                if already_added_user != "":
                    embed.add_field(name="Users already added", value=already_added_user)

                editGuild(guild, data)
                await Admin.AdminCommand(context, embed, "Add teacher Command")
            else:
                await Tools.embedError(context.channel, "You need to add roles or users to use the command")

    @staticmethod
    async def rmRole(context, value):
        guild = str(context.guild.id)
        data = readGuild(guild)
        if not data["admin"]["users"] and not data["admin"]["roles"]:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "zeroPrivileges"))
        elif Tools.got_the_role(data["admin"], context.author):
            embed = discord.Embed(color=discord.Colour.orange())
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

            removed_roles = ""
            not_removed_roles = ""

            removed_users = ""
            not_removed_users = ""

            for role in context.message.role_mentions:
                if role.id in data[value]["roles"]:
                    removed_roles += role + "\n"
                    data[value]["roles"].remove(role.id)
                else:
                    not_removed_roles += role + "\n"

            for user in context.message.mentions:
                if user.id in data[value]["users"]:
                    removed_users += user + "\n"
                    data[value]["roles"].remove(user.id)
                else:
                    not_removed_users += user + "\n"

            if removed_roles == "" and not_removed_roles == "" and removed_users == "" and not_removed_users == "":
                await Tools.embedError(context.channel, "You need to write role or user in order to use the command")
            else:
                if removed_roles != "":
                    embed.add_field(name="Removed roles", value=removed_roles)
                if not_removed_roles != "":
                    embed.add_field(name=f"Was not an {value} role", value=not_removed_roles)

                if removed_users != "":
                    embed.add_field(name="Removed users", value=removed_users)
                if not_removed_users != "":
                    embed.add_field(name=f"Was not an {value} user", value=not_removed_users)
                editGuild(guild, data)
                await Admin.AdminCommand(context, embed, "Remove Command")
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    @staticmethod
    async def prefix(context, arg):
        data = readGuild(context.guild.id)
        if Tools.got_the_role(data["admin"], context.author):
            try:
                set_prefix(context.guild.id, arg)
                embed = discord.Embed(color=discord.Colour.orange(),
                                      title=returnLanguage(readGuild(context.guild.id)["language"],
                                                           "newPrefix") + f"**{arg}**",
                                      description="You still can use \"`.Check `\"")
                embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                                 icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
                await Admin.AdminCommand(context, embed)
            except discord.ext.commands.errors.MissingRequiredArgument:
                await Tools.embedError(context.channel, "You did not specify a prefix")
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    @staticmethod
    async def language(context, lang=None):
        if lang in ["fr", "en", "de"]:
            data = readGuild(context.guild.id)
            if Tools.got_the_role(data["admin"], context.author):
                data["language"] = lang
                embed = discord.Embed(color=discord.Colour.orange(), title=returnLanguage(lang, "changeLanguage"))
                embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                                 icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
                await Admin.AdminCommand(context, embed)
                editGuild(context.guild.id, data)
            else:

                await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))
        else:
            await Tools.embedError(context.channel,
                                   "Unknown language:\n**Languages :**\n• English: en\n• French: fr\n• German: de")

    @staticmethod
    async def ShowPresents(context):
        """
            Activate/Deactivate Show presents students in call summary
        """
        data = readGuild(context.guild.id)
        if Tools.got_the_role(data["admin"], context.author):
            if data["showPresents"]:
                data["showPresents"] = False
                embed = discord.Embed(color=discord.Color.red(), title="Call summary will only show absents students")
            else:
                data["showPresents"] = True
                embed = discord.Embed(color=discord.Color.red(),
                                      title="Call summary will show absents and presents students")

            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            editGuild(context.guild.id, data)
            await Admin.AdminCommand(context, embed)
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    @staticmethod
    async def reset(context):
        data = readGuild(context.guild.id)
        if Tools.got_the_role(data["admin"], context.author) or context.message.author == context.guild.owner:
            data["admin"] = {"roles": [], "users": []}
            data["teacher"] = {"roles": [], "users": []}
            data["language"] = "en"
            data["prefix"] = ".Check "
            data["sysMessages"] = True
            data["mp"] = True
            data["ShowPresents"] = True
            data["delay"] = 10
            editGuild(context.guild.id, data)

            embed = discord.Embed(color=discord.Colour.orange(),
                                  title="**__Factory reset:__**\nLanguage set to English\nAdmins and teachers list "
                                        "reseted\n**Prefix :** `.Check`\n**Show presents students, Sys Messages and "
                                        "Private Messages :** Activated\nDelay for for late students after a call : "
                                        "10 minutes")
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

            await Admin.AdminCommand(context, embed)

        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    @staticmethod
    async def sysMessages(context):
        """
        Activate/Deactivate system message
        """
        data = readGuild(context.guild.id)
        if Tools.got_the_role(data["admin"], context.author):
            if data["sysMessages"]:
                data["sysMessages"] = False
                embed = discord.Embed(color=discord.Color.red(), title="System Messages are now disabled")
            else:
                data["sysMessages"] = True
                embed = discord.Embed(color=discord.Color.red(), title="System Messages are now activated")

            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            editGuild(context.guild.id, data)
            await Admin.AdminCommand(context, embed)
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    @staticmethod
    async def AdminCommand(context, embed: discord.Embed, title=None):
        await context.channel.send(embed=embed)

        if readGuild(context.guild.id)["sysMessages"] and context.guild.system_channel is not None \
                and context.guild.system_channel != context.channel:
            embed.add_field(name="Link to the action", value=f"[Link]({context.message.jump_url})")
            embed.add_field(name="Used by", value=context.message.author.mention)
            if title is not None:
                embed.title = title
            try:
                await context.guild.system_channel.send(embed=embed)

            except discord.ext.commands.CommandInvokeError:
                print(context.guild, context.guild.id, "raised commands.CommandInvokeError")

    @staticmethod
    async def DeactivateMP(context):
        data = readGuild(context.guild.id)
        if Tools.got_the_role(data["admin"], context.author):
            if data["mp"]:
                data["mp"] = False
                embed = discord.Embed(color=discord.Color.red(), title="Private messages are now disabled")
            else:
                data["mp"] = True
                embed = discord.Embed(color=discord.Color.red(), title="Private messages are now activated")
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            editGuild(context.guild.id, data)
            await Admin.AdminCommand(context, embed)
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    @staticmethod
    async def Delay(context, delay: str):
        data = readGuild(context.guild.id)
        if Tools.got_the_role(data["admin"], context.author):

            try:
                delay = int(delay)
                if delay < 0 or delay > 60:
                    raise ValueError
                data["delay"] = delay
                embed = discord.Embed(color=discord.Color.red(), title=f"New delay : **{delay} minutes**")
                embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                                 icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
                editGuild(context.guild.id, data)
                await Admin.AdminCommand(context, embed)
            except ValueError:
                await Tools.embedError(context.channel,
                                       "Value must be between 0 and 60 minutes\nEnter 0 if you do not want to have any delay")
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))
