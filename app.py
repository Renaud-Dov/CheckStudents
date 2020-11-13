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


def returnPresent(idmessage: str, guildID: int,rolelist):
    """
    Retourne la liste des élèves ayant notifié leur présence sur un message.
    """
    liste = appelList[idmessage]['listStudents']
    messages=returnLanguage(readGuild(guildID)["language"], "endcall")
    if liste == []:
        return returnLanguage(readGuild(guildID)["language"], "NoStudents")
    else:
        print(rolelist)
        message = messages[0]
        eleve = []
        for member in liste:
            if not member.id in eleve:
                message += "• *{}* <@{}>\n".format(member.name, member.id)  # [user.display_name,user.id]
                eleve.append(member.id)
                rolelist.remove(member)
        if rolelist !=[]:
            message+="\n"+messages[1]
            for member in rolelist:
                message += "• *{}* <@{}>\n".format(member.name,member.id)
        else:
            message+=messages[2]
        return message


def convert(role: str):
    return int(role.replace(" ", "").lstrip("<@&").rstrip(">"))


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
                appelList[entry]['listStudents'].append(user)  # on le rajoute à la liste d'appel
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
                presents=returnPresent(entry, idGuild,reaction.message.guild.get_role(appelList[entry]['ClasseRoleID']).members)
                
                await send(presents, reaction.message.channel)
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


@client.command(aliases= ['listroles','roles','Roles'])
async def ListRoles(context):
    for i in readGuild(context.guild.id)["admin"]:
        await send("<@&{}> : {}".format(i, discord.utils.get(context.guild.roles, id=i)), context.channel)


@client.command(aliases= ['add'])
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


@client.command(aliases= ['rm','del','remove'])
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
        await send(returnLanguage(readGuild(context.guild.id)["language"], "unknowCommand"), context.message.channel)
        await help(context)
    raise error


def allUser(guild,roleID:int):
    role=guild.get_role(roleID)
    print(role.members)


client.remove_command('help')
@client.command()
async def help(ctx):
    
    message=returnLanguage(readGuild(ctx.guild.id)["language"], "commands")
    
    embed=discord.Embed(color=discord.Colour.green(),title="Help Commands")
    embed.set_author(name="CheckStudents",url="https://github.com/Renaud-Dov/CheckStudents",icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.add_field(name=".Check call",value=message[1])
    embed.add_field(name=".Check addRole",value=message[2])
    embed.add_field(name=".Check rmRole",value=message[3])
    embed.add_field(name=".Check language",value=message[4])
    embed.add_field(name=".Check ListRoles",value=message[5])

    await ctx.message.author.send(message[0])
    await ctx.message.author.send(embed=embed)



client.run(token)
client.add_command(appel)
client.add_command(help)
client.add_command(addRole)
client.add_command(rmRole)
client.add_command(ListRoles)
client.add_command(language)