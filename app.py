from typing import List
import discord
import json
from discord.ext import commands
from data import *

import sys

# import time
token = sys.argv[1]

client = commands.Bot(command_prefix='.Check ')

appelList = {}


def got_the_role(role, author:list):
    if isinstance(role, list):
        for i in role:
            if i in [y.id for y in author]:
                return True
    elif isinstance(role, int):
        return role in [y.id for y in author]


def returnPresent(idmessage: str, guild: int,rolelist):
    """
    Retourne la liste des élèves ayant notifié leur présence sur un message.
    """
    liste = appelList[idmessage]['listStudents']
    print(rolelist)
    if liste == []:
        return returnLanguage(readGuild(guild)["language"], "NoStudents")
    else:
        message = returnLanguage(readGuild(guild)["language"], "Studentsnotify")
        eleve = []
        for i in liste:
            if not i[1] in eleve:
                message += "• *{}* <@{}>\n".format(i[0], i[1])  # [user.display_name,user.id]
                eleve.append(i[1])
                rolelist.remove(i[1])
        if rolelist !=[]:
            message+="\n"+returnLanguage(readGuild(guild)["language"], "missing")
            for i in rolelist:
                message += "• *{}* <@{}>\n".format(i)
        return message


def convert(role: str):
    return int(role.replace(" ", "").lstrip("<@&").rstrip(">"))


async def on_ready():
    """Initilisation du bot"""
    print('Bot started')


@client.event
async def on_guild_join(guild):  # readGuild(message.guild.id)
    rolebot = discord.utils.get(guild.roles, name="CheckStudents").id
    createGuild(guild.id, rolebot)


@client.event
async def on_guild_remove(guild):
    removeGuild(guild.id)


@client.command()
async def send(message, channel):
    await channel.send(message)


@client.command()
async def add_reaction(emoji, message):
    await message.add_reaction(emoji)


@client.command()
async def remove_reaction(emoji, message, user):
    await message.remove_reaction(emoji, user)


@client.command()
async def clear_reaction(emoji, message):
    await message.clear_reaction(emoji)


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
                appelList[entry]['listStudents'].append(
                    [user.display_name, user.id])  # on le rajoute à la liste d'appel
            elif not got_the_role(readGuild(idGuild)['botID'], user.roles):
                await remove_reaction("✅", reaction.message, user)
                await send("<@{}> : {}".format(user.id, returnLanguage(readGuild(idGuild)["language"], "cantNotify")),
                           reaction.message.channel)


        elif reactionContent == "🆗":  # si l'utilisateur a coché OK
            if got_the_role(readGuild(idGuild)["admin"], user.roles):  # est prof
                await send(
                    "<@{}> :{} <@&{}>".format(user.id, returnLanguage(readGuild(idGuild)["language"], "FinishCall"),
                                              appelList[entry]['ClasseRoleID']), reaction.message.channel)
                await clear_reaction("✅", reaction.message)
                await clear_reaction("🆗", reaction.message)
                await send(returnPresent(idGuild + "-" + idMessage, idGuild,allUser(reaction.message.guild,appelList[entry]['ClasseRoleID'])), reaction.message.channel)
                del appelList[entry]

            elif not got_the_role(readGuild(idGuild)['botID'], user.roles):  # pas le bot
                await remove_reaction("🆗", reaction.message, user)
                await send("<@{}> : {}".format(user.id, returnLanguage(readGuild(idGuild)["language"], "NoRightEnd")),
                           reaction.message.channel)

        else:  # autre emoji
            await remove_reaction(reactionContent, reaction.message, user)
            await send("<@{}> : {}".format(user.id, returnLanguage(readGuild(idGuild)["language"], "unknowEmoji")),
                       reaction.message.channel)


@client.command(aliases= ['call'])
async def appel(context, args):
    global appelList
    classe = convert(args)
    data = readGuild(context.guild.id)

    if got_the_role(data["admin"], context.author.roles):
        appelList["{}-{}".format(context.guild.id, context.message.id)] = {'ClasseRoleID': classe, 'listStudents': []}
        await send(returnLanguage(data["language"], "startCall"), context.channel)
        await add_reaction("✅", context.message)  # on rajoute les réactions ✅ & 🆗
        await add_reaction("🆗", context.message)
    else:
        await send("<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "notTeacher")),
                   context.channel)


@client.command()
async def ListRoles(context):
    for i in readGuild(context.guild.id)["admin"]:
        await send("<@&{}> : {}".format(i, discord.utils.get(context.guild.roles, id=i)), context.channel)


@client.command()
async def addRole(context, *args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if len(data["admin"]) > 0 and not got_the_role(data["admin"], context.author.roles):
        await send("<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "NoPrivileges")),
                   context.channel)
    else:
        for i in args:
            data["admin"].append(convert(i))
            await send('*{} :*{}'.format(returnLanguage(data["language"], "newAdmin"), i), context.channel)
        editGuild(guild, data)


@client.command()
async def rmRole(context, *args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if len(data["admin"]) > 0:
        if got_the_role(data["admin"], context.author.roles):
            for i in args:
                i = convert(i)
                if i in data["admin"]:
                    data["admin"].remove(i)
                    await send('*{}:*<@&{}>'.format(returnLanguage(data["language"], "removeAdmin"), i),
                               context.channel)
                else:
                    await send("*<@&{}> {}*".format(i, returnLanguage(data["language"], "notAdmin")), context.channel)
            editGuild(guild, data)
        else:
            await send("<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "NoPrivileges")),
                       context.channel)
    else:
        await send(returnLanguage(data["language"], "zeroPrivileges"), context.channel)


@client.command()
async def language(context, langue):
    if langue in ["fr", "en", "de"]:
        data = readGuild(context.guild.id)
        if got_the_role(data["admin"], context.author.roles):
            data["language"] = langue
            await send(returnLanguage(langue, "changeLanguage"), context.channel)
            editGuild(context.guild.id, data)
        else:
            await send("<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "NoPrivileges")),
                       context.channel)
    else:
        await send("Unknow language:\n**Languages :**\n• English: en\n• French: fr\n• German: de", context.channel)


@client.event
async def on_command_error(context, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await send(returnLanguage(readGuild(context.guild.id)["language"], "commands"), context.message.channel)
        await help(context)
    raise error


def allUser(guild,role:int):
    rolelist=list()
    print(len(guild.members),guild.members)
    for member in guild.members:
        print(member.name,member.roles)
        if got_the_role(role,member.roles):
            rolelist.append(member.id)
    return rolelist

client.remove_command('help')
@client.command()
async def help(ctx):
    
    embed=discord.Embed(color=discord.Colour.green(),title="Help Commands")
    embed.set_author(name="CheckStudents",url="https://github.com/Renaud-Dov/CheckStudents",icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.add_field(name=".Check appel",value=".Check appel ***@class*** -> start the call, *replace by the corresponding class*")
    embed.add_field(name=".Check addRole",value=".Check addRole ***@role1 @role2***, -> add privileges to one or more roles")
    embed.add_field(name=".Check rmRole",value=".Check rmRole ***@role1 @role2***, -> remove privileges from one or more roles")
    embed.add_field(name=".Check language",value=".Check language en|fr|de -> Change bot language in the following languages : English, French or German")
    await ctx.message.author.send("**Here the list of commands you can use with this bot**")
    await ctx.message.author.send(embed=embed)



client.run(token)
client.add_command(appel)
client.add_command(help)
client.add_command(addRole)
client.add_command(rmRole)
client.add_command(ListRoles)
client.add_command(language)