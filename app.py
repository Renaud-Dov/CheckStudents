import discord

from discord.ext import commands
from data import *
from datetime import date
import helpEmbed
import sys

# import time
token = sys.argv[1]
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, dm_messages=True,
                          guild_reactions=True)
client = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

appelList = {}


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=".Check help"))
    # await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=".Check help"))
    # await client.change_presence(activity=discord.Game(name=".Check help"))
    print("Bot is ready!")


def got_the_role(role, user: discord.User):
    """
    Check if a user got at least one role in author list
    """
    if isinstance(role, list):
        for i in role:
            if i in [y.id for y in user.roles]:
                return True
    elif isinstance(role, int):
        return role in [y.id for y in user.roles]


def name(member):
    """
    Return server nickname of a user, and if he doesn't have one, return his pseudo
    """
    if member.nick is not None:
        return member.nick
    else:
        return member.name


@client.group()
async def admin(context):
    if context.invoked_subcommand is None:
        embed = helpEmbed.AdminHelp()
        embed.add_field(name="admin help", value="Show this message")
        await context.channel.send(embed=embed)


@client.group()
async def teacher(context):
    if context.invoked_subcommand is None:
        embed = helpEmbed.TeacherHelp()
        embed.add_field(name="teacher help", value="Show this message")
        await context.channel.send(embed=embed)


def returnPresent(guild_id: int, role_list: list, class_list: list):
    """
    Return presents and absents students who have reacted on a message
    """
    class_list.sort(key=lambda x: name(x).lower())
    role_list.sort(key=lambda x: name(x).lower())
    messages = returnLanguage(readGuild(guild_id)["language"], "endcall")

    presents_msg = messages[0]
    absents_msg = ""
    students = []

    for member in class_list:
        if member.id not in students:
            presents_msg += f"• *{name(member)}* <@{member.id}>\n"  # [user.display_name,user.id]
            students.append(member.id)
            if role_list is not None:
                role_list.remove(member)
    if role_list:
        absents_msg = "\n" + messages[1]
        for member in role_list:
            absents_msg += f"• *{name(member)}* <@{member.id}>\n"
    else:
        absents_msg += messages[2]
    return presents_msg, absents_msg, role_list


async def Send_MP_absents(absents: list, message: discord.Message):  # guild, url: str, author, channel
    """
    Send a mp message to all absents
    """
    language_msg = returnLanguage(readGuild(message.guild.id)["language"], "sendabsents")

    embed = discord.Embed(color=discord.Colour.red(), title="Absence")
    embed.set_author(name=name(message.author), icon_url=message.author.avatar_url)
    embed.add_field(name=language_msg[0], value=name(message.author))
    embed.add_field(name=language_msg[1], value=message.guild)
    embed.add_field(name=language_msg[2], value=message.guild)
    embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"))
    embed.add_field(name=language_msg[3][0], value=f"[{language_msg[3][1]}]({message.jump_url})")
    for member in absents:
        await member.send(embed=embed)


async def SendList(message: discord.Message, entry, students: list):
    """
    Send the list of absents and presents students to the teacher
    """
    language_msg = returnLanguage(readGuild(message.guild.id)["language"], "class")
    embed = discord.Embed(color=discord.Colour.blue(), title=language_msg[1])
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.add_field(name=language_msg[0], value=message.guild.get_role(appelList[entry]['ClasseRoleID']))
    embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"), inline=False)

    await message.author.send(embed=embed)

    await message.author.send(students[0])
    if students[1]:
        await message.author.send(students[1])


def convert(role: str):
    try:
        return int(role.replace(" ", "").lstrip("<@&").rstrip(">"))
    except Exception as e:
        print(e)
        return None


@client.event
async def on_guild_join(guild: discord.Guild):  # readGuild(message.guild.id)
    """
    Send help message  when joining a server
    """
    try:
        bot_id = discord.utils.get(guild.roles, name="CheckStudents").id
        createGuild(guild.id, bot_id)
        if guild.system_channel is not None:
            await guild.system_channel.send(embed=helpEmbed.HelpMsg())
            await guild.system_channel.send(embed=helpEmbed.TeacherHelp())
            await guild.system_channel.send(embed=helpEmbed.AdminHelp())

    except AttributeError:
        await guild.owner.send(f"You're trying to add the bot on **{guild.name}** but you denied some permissions. "
                               "In that case, the bot cannot work on your server. "
                               "Please, remove the bot, and add it again, allowing permissions. "
                               "Link : https://discord.com/api/oauth2/authorize?client_id=760157065997320192&permissions=92224&scope=bot")
    except commands.CommandInvokeError:
        print("CommandInvokeError", guild.id, guild)


@client.event
async def on_guild_remove(guild):
    try:
        removeGuild(guild.id)
    except FileNotFoundError:
        print("FileNotFoundError", guild, guild.id)


async def CheckReaction(reaction: discord.Reaction, user, entry: str):
    reactionContent = str(reaction).strip(" ")

    if reactionContent == "✅":  # si l'utilisateur a coché présent
        if got_the_role(appelList[entry]['ClasseRoleID'],
                        user):  # si user a le role de la classe correspondante
            appelList[entry]['listStudents'].append(user)  # on le rajoute à la liste d'appel
        elif not got_the_role(readGuild(reaction.message.guild.id)['botID'], user):
            await reaction.message.remove_reaction("✅", user)
            await reaction.message.channel.send(
                "<@{}> : {}".format(user.id,
                                    returnLanguage(readGuild(reaction.message.guild.id)["language"], "cantNotify")))

    elif reactionContent in ("🆗", "🛑"):
        # Check if user got teacher privileges
        if got_the_role(readGuild(reaction.message.guild.id)["teacher"], user):

            if reactionContent == "🆗":
                await reaction.message.channel.send(
                    "<@{}> :{} <@&{}>".format(user.id,
                                              returnLanguage(readGuild(reaction.message.guild.id)["language"],
                                                             "FinishCall"),
                                              appelList[entry]['ClasseRoleID']))
                await finishCall(reaction.message.channel, entry, reaction.message.guild.id, reaction)
            else:
                await reaction.message.channel.send(
                    returnLanguage(readGuild(reaction.message.guild.id)["language"], "cancelCall"))
            await reaction.message.clear_reactions()
            del appelList[entry]

        elif not got_the_role(readGuild(reaction.message.guild.id)['botID'], user):  # pas le bot
            await reaction.message.remove_reaction(reactionContent, user)
            await reaction.message.channel.send(
                "<@{}> : {}".format(user.id,
                                    returnLanguage(readGuild(reaction.message.guild.id)["language"], "NoRightEnd")))
    else:  # autre emoji
        await reaction.message.remove_reaction(reactionContent, user)
        await reaction.message.channel.send(
            "<@{}> : {}".format(user.id,
                                returnLanguage(readGuild(reaction.message.guild.id)["language"], "unknowEmoji")))


@client.event
async def on_reaction_add(reaction, user):
    global appelList
    idMessage = str(reaction.message.id)
    idGuild = str(reaction.message.guild.id)
    entry = idGuild + "-" + idMessage

    if entry in appelList:  # si c'est un message d'appel lancé par un professeur
        await CheckReaction(reaction, user, entry)


async def finishCall(channel: discord.TextChannel, entry, guild_id, reaction: discord.Reaction):
    data = readGuild(guild_id)
    if not appelList[entry]['listStudents']:
        embed = discord.Embed(color=discord.Colour.red(),
                              title="No students presents, please use 🛑 to cancel the call")
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/remove.png")

        await channel.send(embed=embed)
    else:
        role_list = reaction.message.guild.get_role(appelList[entry]['ClasseRoleID']).members
        nbStudents: int = len(role_list)
        presentsMessage, absents, listAbsents = returnPresent(guild_id, role_list, appelList[entry]['listStudents'])
        firstMsg = presentsMessage if data["showPresents"] and presentsMessage else f"{len(appelList[entry]['listStudents'])} students out of {nbStudents} are present"
        await channel.send(firstMsg)

        await channel.send(absents)
        await SendList(reaction.message, entry, [firstMsg, absents])

        if data["mp"]:
            await Send_MP_absents(listAbsents, reaction.message)


@client.command(aliases=['call'])
async def Call(context, *args):
    global appelList
    class_role = convert(args[0])
    data = readGuild(context.guild.id)
    if class_role is None:
        await embedError(context.channel, "This is not a role, but a specific user")
    else:
        if got_the_role(data["teacher"], context.author):
            appelList[f"{context.guild.id}-{context.message.id}"] = {'ClasseRoleID': class_role,
                                                                     "teacher": context.message.author,
                                                                     'listStudents': []}
            message = returnLanguage(data["language"], "startcall")

            embed = discord.Embed(color=discord.Colour.green(), title=message[0], description=message[1])
            embed.set_author(name=name(context.message.author),
                             icon_url=context.message.author.avatar_url)
            embed.add_field(name=f"**__{message[2]}__**", value=args[0])
            embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"))
            embed.set_footer(text=message[3])

            await context.channel.send(embed=embed)
            await context.message.add_reaction("✅")  # on rajoute les réactions ✅ & 🆗
            await context.message.add_reaction("🆗")
            await context.message.add_reaction("🛑")
        else:
            await context.channel.send(
                "<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "notTeacher")))


@admin.command(aliases=['Roles', 'list', 'admin', 'admins'])
async def roles(context):
    await ListRoles(context, "admin")


@teacher.command(aliases=['Roles', 'list', 'admin', 'admins'])
async def roles(context):
    await ListRoles(context, "teacher")


async def ListRoles(context, value: str):
    message = ""
    embed = discord.Embed(color=discord.Colour.orange())
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    role = readGuild(context.guild.id)[value]
    if not role:
        embed.add_field(name=f"**{value} :**", value=f"There is no {value} yet")
    else:
        for i in role:
            message += f"<@&{i}>\n"
        embed.add_field(name=f"**{value.capitalize()} :**", value=message)
    await context.channel.send(embed=embed)


@admin.command()
async def add(context, *args):
    await addRole(context, "admin", args)


@teacher.command()
async def add(context, *args):
    await addRole(context, "teacher", args)


async def addRole(context, value, args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if data["admin"] != [] and not got_the_role(data["admin"], context.author):
        await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))
    else:
        # message = str()
        # langMessage = returnLanguage(data["language"], "newAdmin")
        embed = discord.Embed(color=discord.Colour.orange())
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

        added_roles = ""
        already_added_roles = ""
        for i in args:

            role = convert(i)

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
            await AdminCommand(context, embed, "Add teacher Command")


@admin.command(aliases=['del', 'remove'])
async def rm(context, *args):
    await rmRole(context, "admin", args)


@teacher.command(aliases=['del', 'remove'])
async def rm(context, *args):
    await rmRole(context, "teacher", args)


async def rmRole(context, value, args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if not data["admin"]:
        await embedError(context.channel, returnLanguage(data["language"], "zeroPrivileges"))
    elif got_the_role(data["admin"], context.author):
        embed = discord.Embed(color=discord.Colour.orange())
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

        removed_roles = ""
        not_removed_roles = ""

        for i in args:
            role = convert(i)
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
            await AdminCommand(context, embed, "Remove Command")
    else:
        await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))


@admin.command()
async def prefix(context, arg):
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author):
        try:
            set_prefix(context.guild.id, arg)
            embed = discord.Embed(color=discord.Colour.orange(),
                                  title=returnLanguage(readGuild(context.guild.id)["language"],
                                                       "newPrefix") + f"**{arg}**",
                                  description="You still can use \"`.Check `\"")
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            await AdminCommand(context, embed)
        except commands.errors.MissingRequiredArgument:
            await embedError(context.channel, "You did not specify a prefix")
    else:
        await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))


@admin.command(aliases=["lang"])
async def language(context, lang=None):
    if lang in ["fr", "en", "de"]:
        data = readGuild(context.guild.id)
        if got_the_role(data["admin"], context.author):
            data["language"] = lang
            embed = discord.Embed(color=discord.Colour.orange(), title=returnLanguage(lang, "changeLanguage"))
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            await AdminCommand(context, embed)
            editGuild(context.guild.id, data)
        else:

            await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))
    else:
        await embedError(context.channel,
                         "Unknown language:\n**Languages :**\n• English: en\n• French: fr\n• German: de")


@client.event
async def on_command_error(context, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await embedError(context.channel, "Unknown Command. Use help command")
    # print(error, context.guild, context.guild.id, context.channel, context.message.jump_url)


@admin.command()
async def ShowPresents(context):
    """
        Activate/Deactivate Show presents students in call summary
    """
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author):
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
        await AdminCommand(context, embed)
    else:
        await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))


@admin.command()
async def reset(context):
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author) or context.message.author == context.guild.owner:
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

        await AdminCommand(context, embed)

    else:
        await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))


async def embedError(channel, message):
    embed = discord.Embed(color=discord.Color.red(), title=message)
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    # embed.add_field(name="Permission Denied",value=message)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/remove.png")
    await channel.send(embed=embed)


@admin.command(aliases=["sys"])
async def sysMessages(context):
    """
    Activate/Deactivate system message
    """
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author):
        if data["sysMessages"]:
            data["sysMessages"] = False
            embed = discord.Embed(color=discord.Color.red(), title="System Messages are now disabled")
        else:
            data["sysMessages"] = True
            embed = discord.Embed(color=discord.Color.red(), title="System Messages are now activated")

        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        editGuild(context.guild.id, data)
        await AdminCommand(context, embed)
    else:
        await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))


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

        except commands.CommandInvokeError:
            print(context.guild, context.guild.id, "raised commands.CommandInvokeError")
    # jump_url


@admin.command(aliases=["MP,mp"])
async def DeactivateMP(context):
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author):
        if data["mp"]:
            data["mp"] = False
            embed = discord.Embed(color=discord.Color.red(), title="Private messages are now disabled")
        else:
            data["mp"] = True
            embed = discord.Embed(color=discord.Color.red(), title="Private messages are now activated")
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        editGuild(context.guild.id, data)
        await AdminCommand(context, embed)
    else:
        await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))


@client.command()
async def settings(context):
    data = readGuild(context.guild.id)
    embed = discord.Embed(color=discord.Colour.orange(), title="Current settings")
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.add_field(name="• System Messages", value=str(data["sysMessages"]), inline=False)
    embed.add_field(name="• Private Messages", value=str(data["mp"]), inline=False)
    embed.add_field(name="• Show present students after call", value=str(data["showPresents"]), inline=False)
    embed.add_field(name="• Language", value=str(data["language"]), inline=False)
    embed.add_field(name="• Prefix", value=str(data["prefix"]), inline=False)

    await context.channel.send(embed=embed)


@teacher.command(aliases=["commands,command"])
async def help(context):
    await context.message.author.send("Here the list of subcommand you can use with *teacher*",
                                      embed=helpEmbed.TeacherHelp())


@admin.command(aliases=["commands,command"])
async def help(context):
    await context.message.author.send("Here the list of subcommand you can use with *admin*",
                                      embed=helpEmbed.AdminHelp())


@client.command(aliases=["commands,command"])
async def help(context):
    await context.message.author.send(embed=helpEmbed.HelpMsg())


client.run(token)
client.add_command(help)
