import discord

from discord.ext import commands
from data import *

import sys

# import time
token = sys.argv[1]
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, dm_messages=True,
                          guild_reactions=True)
client = commands.Bot(command_prefix='.Check ', intents=intents)

appelList = {}


def got_the_role(role, author: list):
    if isinstance(role, list):
        for i in role:
            if i in [y.id for y in author]:
                return True
    elif isinstance(role, int):
        return role in [y.id for y in author]


def returnPresent(idmessage: str, guildID: int, rolelist: list):
    """
    Retourne la liste des élèves ayant notifié leur présence sur un message.
    """
    liste = appelList[idmessage]['listStudents']
    messages = returnLanguage(readGuild(guildID)["language"], "endcall")
    if liste == []:
        return returnLanguage(readGuild(guildID)["language"], "NoStudents")
    else:
        message = messages[0]
        eleve = []
        for member in liste:
            if not member.id in eleve:
                message += "• *{}* <@{}>\n".format(member.name, member.id)  # [user.display_name,user.id]
                eleve.append(member.id)
                if rolelist is not None: rolelist.remove(member)
        if rolelist != []:
            message += "\n" + messages[1]
            for member in rolelist:
                message += "• *{}* <@{}>\n".format(member.name, member.id)
        else:
            message += messages[2]
        return message


def convert(role: str):
    try:
        return int(role.replace(" ", "").lstrip("<@&").rstrip(">"))
    except Exception as e:
        print(e)
        return None


@client.event
async def on_guild_join(guild):  # readGuild(message.guild.id)
    rolebot = discord.utils.get(guild.roles, name="CheckStudents").id
    createGuild(guild.id, rolebot)


@client.event
async def on_guild_remove(guild):
    removeGuild(guild.id)

@client.event
async def on_reaction_add(reaction, user):
    global appelList
    idMessage = str(reaction.message.id)
    idGuild = str(reaction.message.guild.id)
    entry = idGuild + "-" + idMessage

    if entry in appelList:  # si c'est un message d'appel lancé par un professeur
        reactionContent = str(reaction).strip(" ")

        if reactionContent == "✅":  # si l'utilisateur a coché présent
            if got_the_role(appelList[entry]['ClasseRoleID'],
                            user.roles):  # si user a le role de la classe correspondante
                appelList[entry]['listStudents'].append(user)  # on le rajoute à la liste d'appel
            elif not got_the_role(readGuild(idGuild)['botID'], user.roles):
                await reaction.message.remove_reaction("✅",user)
                await reaction.message.channel.send("<@{}> : {}".format(user.id, returnLanguage(readGuild(idGuild)["language"], "cantNotify")))


        elif reactionContent == "🆗" or reactionContent == "🛑":  # si l'utilisateur a coché OK
            if got_the_role(readGuild(idGuild)["admin"], user.roles):  # est prof

                if reactionContent == "🆗":
                    await reaction.message.channel.send(
                        "<@{}> :{} <@&{}>".format(user.id, returnLanguage(readGuild(idGuild)["language"], "FinishCall"),
                                                  appelList[entry]['ClasseRoleID']))
                    presents = returnPresent(entry, idGuild,
                                             reaction.message.guild.get_role(appelList[entry]['ClasseRoleID']).members)
                    await reaction.message.channel.send(presents)
                else:
                    await reaction.message.channel.send(returnLanguage(readGuild(idGuild)["language"], "cancelCall"))
                await reaction.message.clear_reactions()
                del appelList[entry]

            elif not got_the_role(readGuild(idGuild)['botID'], user.roles):  # pas le bot
                await reaction.message.remove_reaction(reactionContent, user)
                await reaction.message.channel.send("<@{}> : {}".format(user.id, returnLanguage(readGuild(idGuild)["language"], "NoRightEnd")))
        else:  # autre emoji
            await reaction.message.remove_reaction(reactionContent, user)
            await reaction.message.channel.sendsend("<@{}> : {}".format(user.id, returnLanguage(readGuild(idGuild)["language"], "unknowEmoji")))


@client.command(aliases=['call'])
async def appel(context, args):
    global appelList
    classe = convert(args)
    data = readGuild(context.guild.id)
    if classe is None:
        await context.channel.send(returnLanguage(data["language"], "rolenotValid"))
    else:
        if got_the_role(data["admin"], context.author.roles):
            appelList["{}-{}".format(context.guild.id, context.message.id)] = {'ClasseRoleID': classe,
                                                                               'listStudents': []}
            await context.channel.send(returnLanguage(data["language"], "startCall"))
            await  context.message.add_reaction("✅")  # on rajoute les réactions ✅ & 🆗
            await  context.message.add_reaction("🆗")
            await  context.message.add_reaction("🛑")
        else:
            await context.channel.send("<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "notTeacher")))


@client.command(aliases=[ 'roles', 'Roles', 'list'])
async def ListRoles(context, *args):
    message = "**Admins :**"
    quiet = args != () and args[0] == '-q'
    for i in readGuild(context.guild.id)["admin"]:
        if quiet:
            message += "\n• {}".format(discord.utils.get(context.guild.roles, id=i))
        else:
            message += "\n• <@&{}> : {}".format(i, discord.utils.get(context.guild.roles, id=i))
    await context.channel.send(message)


@client.command(aliases=['add'])
async def addRole(context, *args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if data["admin"]!=[] and not got_the_role(data["admin"], context.author.roles):
        await context.channel.send("<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "NoPrivileges")))
    else:
        message = str()
        langMessage=returnLanguage(data["language"], "newAdmin")
        for i in args:
            role = convert(i)
            if role is not None:
                if not role in data["admin"]:
                    data["admin"].append(role)
                    message += '\n• ' + langMessage[0] + i
                else:
                    message += "\n• **{}** ".format(i)+langMessage[1]
            else:
                message += "\n• **{}** ".format(i)+langMessage[2]
        editGuild(guild, data)
        await context.channel.send(message)


@client.command(aliases=['rm', 'del', 'remove'])
async def rmRole(context, *args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if len(data["admin"]) > 0:
        if got_the_role(data["admin"], context.author.roles):
            message = str()
            for i in args:
                role = convert(i)
                if role in data["admin"]:
                    data["admin"].remove(role)
                    message += '\n• *{}:* <@&{}>'.format(returnLanguage(data["language"], "removeAdmin"), role)
                else:
                    message += "\n• *<@&{}> {}*".format(role, returnLanguage(data["language"], "notAdmin"))
            editGuild(guild, data)
            await context.channel.send(message)
        else:
            await context.channel.send("<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "NoPrivileges")))
    else:
        await context.channel.send(returnLanguage(data["language"], "zeroPrivileges"))


@client.command()
async def language(context, langue):
    if langue in ["fr", "en", "de"]:
        data = readGuild(context.guild.id)
        if got_the_role(data["admin"], context.author.roles):
            data["language"] = langue
            await context.channel.send(returnLanguage(langue, "changeLanguage"))
            editGuild(context.guild.id, data)
        else:
            await context.channel.send("<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "NoPrivileges")),
                       context.channel)
    else:
        await context.channel.send("Unknow language:\n**Languages :**\n• English: en\n• French: fr\n• German: de")


@client.event
async def on_command_error(context, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await context.channel.send(returnLanguage(readGuild(context.guild.id)["language"], "unknowCommand"))
        await help(context)
    raise error


client.remove_command('help')


@client.command(aliases=["commands,command"])
async def help(context):
    message = returnLanguage(readGuild(context.guild.id)["language"], "commands")

    embed = discord.Embed(color=discord.Colour.green(), title="Help Commands")
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.add_field(name=message[1][0], value=message[1][1])
    embed.add_field(name=message[2][0], value=message[2][1])
    embed.add_field(name=message[3][0], value=message[3][1])
    embed.add_field(name=message[4][0], value=message[4][1])
    embed.add_field(name=message[5][0], value=message[5][1])

    await context.message.author.send(message[0], embed=embed)
    # await ctx.message.author.send()


client.run(token)
client.add_command(appel)
client.add_command(help)
client.add_command(addRole)
client.add_command(rmRole)
client.add_command(ListRoles)
client.add_command(language)
