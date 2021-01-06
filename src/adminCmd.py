from src.data import *
from src.tools import Tools


class Admin:
    async def addRole(self, context, value, args):
        guild = str(context.guild.id)
        data = readGuild(guild)
        if data["admin"] != [] and not Tools.got_the_role(data["admin"], context.author):
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))
        else:
            embed = discord.Embed(color=discord.Colour.orange())
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

            added_roles = ""
            already_added_roles = ""
            for i in args:

                role = Tools.convert(i)

                if role not in data[value]:
                    data[value].append(role)
                    added_roles += i + "\n"
                else:
                    already_added_roles += i + "\n"

            if added_roles == "" and already_added_roles == "":
                embed.add_field(name="You need to add roles to use the command", value=f"{value} add @role1 @role2")
                await context.channel.send(embed=embed)
            else:
                if added_roles != "":
                    embed.add_field(name="Added roles", value=added_roles)
                if already_added_roles != "":
                    embed.add_field(name="Already added", value=already_added_roles)
                editGuild(guild, data)
                await self.AdminCommand(context, embed, "Add teacher Command")

    async def rmRole(self, context, value, args):
        guild = str(context.guild.id)
        data = readGuild(guild)
        if not data["admin"]:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "zeroPrivileges"))
        elif Tools.got_the_role(data["admin"], context.author):
            embed = discord.Embed(color=discord.Colour.orange())
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

            removed_roles = ""
            not_removed_roles = ""

            for i in args:
                role = Tools.convert(i)
                if role in data[value]:
                    removed_roles += i + "\n"
                    data[value].remove(role)
                else:
                    not_removed_roles += i + "\n"

            if removed_roles == "" and not_removed_roles == "":
                embed.add_field(name="You need to write role(s) to use the command", value=f"{value} rm @role")
                await context.channel.send(embed=embed)
            else:
                if removed_roles != "":
                    embed.add_field(name="Removed roles", value=removed_roles)
                if not_removed_roles != "":
                    embed.add_field(name=f"Was not an {value}", value=not_removed_roles)
                editGuild(guild, data)
                await self.AdminCommand(context, embed, "Remove Command")
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    async def prefix(self, context, arg):
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
                await self.AdminCommand(context, embed)
            except discord.ext.commands.errors.MissingRequiredArgument:
                await Tools.embedError(context.channel, "You did not specify a prefix")
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    async def language(self, context, lang=None):
        if lang in ["fr", "en", "de"]:
            data = readGuild(context.guild.id)
            if Tools.got_the_role(data["admin"], context.author):
                data["language"] = lang
                embed = discord.Embed(color=discord.Colour.orange(), title=returnLanguage(lang, "changeLanguage"))
                embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                                 icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
                await self.AdminCommand(context, embed)
                editGuild(context.guild.id, data)
            else:

                await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))
        else:
            await Tools.embedError(context.channel,
                             "Unknown language:\n**Languages :**\n• English: en\n• French: fr\n• German: de")

    async def ShowPresents(self, context):
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
            await self.AdminCommand(context, embed)
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    async def reset(self, context):
        data = readGuild(context.guild.id)
        if Tools.got_the_role(data["admin"], context.author) or context.message.author == context.guild.owner:
            data["admin"] = []
            data["teacher"] = []
            data["language"] = "en"
            data["prefix"] = ".Check "
            data["sysMessages"] = True
            data["mp"] = True
            data["ShowPresents"] = True
            editGuild(context.guild.id, data)

            embed = discord.Embed(color=discord.Colour.orange(),
                                  title="**__Factory reset:__**\nLanguage set to English\nAdmins and teachers list reseted\n**Prefix :** `.Check`\n**Show presents students, Sys Messages and Private Messages :** Activated")
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

            await self.AdminCommand(context, embed)

        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    async def sysMessages(self, context):
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
            await self.AdminCommand(context, embed)
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))

    async def AdminCommand(self, context, embed: discord.Embed, title=None):
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

    async def DeactivateMP(self, context):
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
            await self.AdminCommand(context, embed)
        else:
            await Tools.embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))