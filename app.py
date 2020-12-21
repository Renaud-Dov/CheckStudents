import discord

from discord.ext import commands
from data import *
from datetime import date

import sys

# import time
token = sys.argv[1]
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, dm_messages=True,
                          guild_reactions=True)
client = commands.Bot(command_prefix=get_prefix, intents=intents)

appelList = {}


def got_the_role(role, author: list):
    """
    Check if a user got at least one role in author list
    """
    if isinstance(role, list):
        for i in role:
            if i in [y.id for y in author]:
                return True
    elif isinstance(role, int):
        return role in [y.id for y in author]


def name(member):
    """
    Return server nickname of a user, and if he doesn't have one, return his pseudo
    """
    if member.nick is not None:
        return member.nick
    else:
        return member.name


def returnPresent(id_msg: str, guild_id: int, role_list: list):
    """
    Return presents and absents students who have reacted on a message
    """
    class_list = appelList[id_msg]['listStudents']
    # messages = returnLanguage(readGuild(guildID)["language"], "endcall")
    messages = returnLanguage(readGuild(guild_id)["language"], "endcall")

    presents_msg = messages[0]
    absents_msg = ""
    students = []
    for member in class_list:
        if member.id not in students:
            presents_msg += "• *{}* <@{}>\n".format(name(member), member.id)  # [user.display_name,user.id]
            students.append(member.id)
            if role_list is not None:
                role_list.remove(member)
    if role_list:
        absents_msg = "\n" + messages[1]
        for member in role_list:
            absents_msg += "• *{}* <@{}>\n".format(name(member), member.id)
    else:
        presents_msg += messages[2]
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
    embed.add_field(name=language_msg[3][0], value="[{}]({})".format(language_msg[3][1], message.jump_url))
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
    if students[0]:
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
    except AttributeError:
        guild.owner.send("You're trying to add the bot on {} but you denied some permissions."
                         "In that case, the bot cannot work on your server."
                         "Please, remove the bot, and add it again, allowing permissions."
                         "Link : {}".format(guild.name,"https://discord.com/api/oauth2/authorize?client_id=760157065997320192&permissions=92224&scope=bot"))
        return

    createGuild(guild.id, bot_id)
    if guild.system_channel is not None:
        message = returnLanguage("en", "commands")
        embed = discord.Embed(color=discord.Colour.blue(), title="I joined the Server",
                              description="Here the list of commands you can use:")
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        # embed.add_field(name="call", value=classe)
        embed = CompleteHelpEmbed(embed, message)
        try:
            await guild.system_channel.send(embed=embed)
        except commands.CommandInvokeError:
            print("CommandInvokeError", guild.id, guild)


@client.event
async def on_guild_remove(guild):
    removeGuild(guild.id)


async def CheckReaction(reaction: discord.reaction, user, entry: str):
    reactionContent = str(reaction).strip(" ")

    if reactionContent == "✅":  # si l'utilisateur a coché présent
        if got_the_role(appelList[entry]['ClasseRoleID'],
                        user.roles):  # si user a le role de la classe correspondante
            appelList[entry]['listStudents'].append(user)  # on le rajoute à la liste d'appel
        elif not got_the_role(readGuild(reaction.guild.id)['botID'], user.roles):
            await reaction.message.remove_reaction("✅", user)
            await reaction.message.channel.send(
                "<@{}> : {}".format(user.id, returnLanguage(readGuild(reaction.guild.id)["language"], "cantNotify")))

    elif reactionContent in ("🆗", "🛑"):
        if got_the_role(readGuild(reaction.guild.id)["admin"], user.roles):  # est prof

            if reactionContent == "🆗":
                await reaction.message.channel.send(
                    "<@{}> :{} <@&{}>".format(user.id,
                                              returnLanguage(readGuild(reaction.guild.id)["language"], "FinishCall"),
                                              appelList[entry]['ClasseRoleID']))
                await finishCall(reaction.message.channel, entry, reaction.guild.id, reaction)
            else:
                await reaction.message.channel.send(
                    returnLanguage(readGuild(reaction.guild.id)["language"], "cancelCall"))
            await reaction.message.clear_reactions()
            del appelList[entry]

        elif not got_the_role(readGuild(reaction.guild.id)['botID'], user.roles):  # pas le bot
            await reaction.message.remove_reaction(reactionContent, user)
            await reaction.message.channel.send(
                "<@{}> : {}".format(user.id, returnLanguage(readGuild(reaction.guild.id)["language"], "NoRightEnd")))
    else:  # autre emoji
        await reaction.message.remove_reaction(reactionContent, user)
        await reaction.message.channel.sendsend(
            "<@{}> : {}".format(user.id, returnLanguage(readGuild(reaction.guild.id)["language"], "unknowEmoji")))


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
        presentsMessage, absents, listAbsents = returnPresent(entry, guild_id, reaction.message.guild.get_role(
            appelList[entry]['ClasseRoleID']).members)

        if presentsMessage:
            await channel.send(presentsMessage)
        if absents:
            await channel.send(absents)
        await SendList(reaction.message, entry, [presentsMessage, absents])

        if data["mp"]:
            await Send_MP_absents(listAbsents, reaction.message)


@client.command(aliases=['call'])
async def Call(context, *args):
    global appelList
    class_role = convert(args[0])
    data = readGuild(context.guild.id)
    if class_role is None:
        await context.channel.send(returnLanguage(data["language"], "rolenotValid"))
    else:
        if got_the_role(data["admin"], context.author.roles):
            appelList["{}-{}".format(context.guild.id, context.message.id)] = {'ClasseRoleID': class_role,
                                                                               'listStudents': []}
            message = returnLanguage(data["language"], "startcall")

            embed = discord.Embed(color=discord.Colour.green(), title=message[0], description=message[1])
            embed.set_author(name=name(context.message.author),
                             icon_url=context.message.author.avatar_url)
            embed.add_field(name="**__{}__**".format(message[2]), value=args[0])
            embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"))
            embed.set_footer(text=message[3])

            await context.channel.send(embed=embed)
            await context.message.add_reaction("✅")  # on rajoute les réactions ✅ & 🆗
            await context.message.add_reaction("🆗")
            await context.message.add_reaction("🛑")
        else:
            await context.channel.send(
                "<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "notTeacher")))


@client.command(aliases=['roles', 'Roles', 'list', 'admin', 'admins'])
async def ListRoles(context):
    message = ""
    embed = discord.Embed(color=discord.Colour.orange())
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    admins = readGuild(context.guild.id)["admin"]
    if not admins:
        embed.add_field(name="**Admins :**", value="There is no admin yet")
    else:
        for i in admins:
            message += "<@&{}>\n".format(i)
        embed.add_field(name="**Admins :**", value=message)
    await context.channel.send(embed=embed)


@client.command(aliases=['add'])
async def addRole(context, *args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if data["admin"] != [] and not got_the_role(data["admin"], context.author.roles):
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

            if role not in data["admin"]:
                data["admin"].append(role)
                added_roles += i + "\n"
            else:
                already_added_roles += i + "\n"

        if added_roles == "" and already_added_roles == "":
            embed.add_field(name="You need to add roles to use the command", value="add @role1 @role2")
            await context.channel.send(embed=embed)
        else:
            if added_roles != "":
                embed.add_field(name="Added roles", value=added_roles)
            if already_added_roles != "":
                embed.add_field(name="Already added", value=already_added_roles)
            editGuild(guild, data)
            await AdminCommand(context, embed, "Add Command")


@client.command(aliases=['rm', 'del', 'remove'])
async def rmRole(context, *args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if not data["admin"]:
        await embedError(context.channel, returnLanguage(data["language"], "zeroPrivileges"))
    else:
        if got_the_role(data["admin"], context.author.roles):
            embed = discord.Embed(color=discord.Colour.orange())
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

            removed_roles = ""
            not_removed_roles = ""

            for i in args:
                role = convert(i)
                if role in data["admin"]:
                    removed_roles += "<@&{}>\n".format(role)
                    data["admin"].remove(role)
                else:
                    not_removed_roles += "<@&{}>\n".format(role)

            if removed_roles == "" and not_removed_roles == "":
                embed.add_field(name="You need to write role(s) to use the command", value="rm @role")
                await context.channel.send(embed=embed)
            else:
                if removed_roles != "":
                    embed.add_field(name="Removed roles", value=removed_roles)
                if not_removed_roles != "":
                    embed.add_field(name="Was not an admin", value=not_removed_roles)
                editGuild(guild, data)
                await AdminCommand(context, embed, "Remove Command")
        else:
            await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))


@client.command()
async def prefix(context, arg):
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author.roles):
        try:
            set_prefix(context.guild.id, arg)
            embed = discord.Embed(color=discord.Colour.orange(),
                                  title=returnLanguage(readGuild(context.guild.id)["language"],
                                                       "newPrefix") + "**{}**".format(arg))
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            await AdminCommand(context, embed)
        except commands.errors.MissingRequiredArgument:
            await embedError(context.channel, "You did not specify a prefix")
    else:
        await embedError(context.channel, returnLanguage(data["language"], "NoPrivileges"))


@client.command(aliases=["lang"])
async def language(context, lang=None):
    if lang in ["fr", "en", "de"]:
        data = readGuild(context.guild.id)
        if got_the_role(data["admin"], context.author.roles):
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
        await context.channel.send(returnLanguage(readGuild(context.guild.id)["language"], "unknownCommand"))
        await help(context)
    raise error


client.remove_command('help')


@client.command(aliases=["commands,command"])
async def help(context):
    message = returnLanguage(readGuild(context.guild.id)["language"], "commands")

    embed = discord.Embed(color=discord.Colour.green(), title="Help Commands")
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed = CompleteHelpEmbed(embed, message)

    await context.message.author.send(message[0], embed=embed)
    # await ctx.message.author.send()


@client.command()
async def reset(context):
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author.roles) or context.message.author == context.guild.owner:
        data["admin"] = []
        data["language"] = "en"
        data["prefix"] = ".Check "
        data["sysMessages"] = True
        data["mp"] = True
        editGuild(context.guild.id, data)

        embed = discord.Embed(color=discord.Colour.orange(),
                              title="**__Factory reset:__**\nLanguage set to English\nAdmins list reseted\n**Prefix :** `.Check`\n**Sys Messages and Private Messages :** Activated")
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


@client.command(aliases=["sys"])
async def sysMessages(context):
    """
    Activate/Deactivate system message
    """
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author.roles):
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

    if readGuild(context.guild.id)["sysMessages"] and context.guild.system_channel is not None\
            and context.guild.system_channel != context.channel:
        embed.add_field(name="Link to the action", value="[Link]({})".format(context.message.jump_url))
        embed.add_field(name="Used by", value=context.message.author.mention)
        if title is not None:
            embed.title = title
        try:
            await context.guild.system_channel.send(embed=embed)

        except commands.CommandInvokeError:
            print(context.guild, context.guild.id, "raised commands.CommandInvokeError")
    # jump_url


@client.command(aliases=["MP,mp"])
async def DeactivateMP(context):
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author.roles):
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
    embed.add_field(name="• Language", value=str(data["language"]), inline=False)

    await context.channel.send(embed=embed)


def CompleteHelpEmbed(embed: discord.Embed, message):
    embed.add_field(name=message[1][0], value=message[1][1], inline=False)
    embed.add_field(name=message[2][0], value=message[2][1], inline=False)
    embed.add_field(name=message[3][0], value=message[3][1], inline=False)
    embed.add_field(name=message[4][0], value=message[4][1], inline=False)
    embed.add_field(name=message[5][0], value=message[5][1], inline=False)
    embed.add_field(name=message[6][0], value=message[6][1], inline=False)
    embed.add_field(name=message[7][0], value=message[7][1], inline=False)
    embed.add_field(name=message[8][0], value=message[8][1], inline=False)
    embed.add_field(name=message[9][0], value=message[9][1], inline=False)
    embed.add_field(name=message[10][0], value=message[10][1], inline=False)
    embed.add_field(name=message[11][0], value=message[11][1], inline=False)
    return embed


client.run(token)
client.add_command(Call)
client.add_command(help)
client.add_command(addRole)
client.add_command(rmRole)
client.add_command(ListRoles)
client.add_command(language)
client.add_command(prefix)
client.add_command(reset)
client.add_command(sysMessages)
client.add_command(DeactivateMP)
