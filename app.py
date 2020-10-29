from typing import List
import discord
import json
from discord.ext import commands
import langues as lg

import sys
# import time



client = commands.Bot(command_prefix= '.Check ')

def jsonread():
    with open('guild.json', 'r') as outfile:
        return json.load(outfile)

token=sys.argv[1]
liste_eleves=jsonread()

def jsonWrite():
    with open('guild.json', 'w') as outfile:
        json.dump(liste_eleves, outfile)

def got_the_role(role,authorRoles:list):
    if isinstance(role,list):
        for i in role:
            if i in [y.id for y in authorRoles]:
                return True
    elif isinstance(role,int):
        return role in [y.id for y in authorRoles]

def returnPresent(message):
    liste=liste_eleves[str(message.guild.id)]['appels'][str(message.id)]['listStudents']
    if liste==[]:
        return lg.language(liste_eleves[str(message.guild.id)]["language"],"NoStudents")
    else:
        message=lg.language(liste_eleves[str(message.guild.id)]["language"],"Studentsnotify")
        for i in liste:
            message+="• *{}* <@{}>\n".format(i[0],i[1])  #[user.display_name,user.id]
        return message

def convert(id):
    return int(id.replace(" ","").lstrip("<@&").rstrip(">"))

async def on_ready():
    """Initilisation du bot"""
    print('Bot started')

@client.event
async def on_guild_join(guild):
    global liste_eleves
    rolebot=discord.utils.get(guild.roles, name="CheckStudents").id
    liste_eleves[str(guild.id)]={"botID":rolebot,"language":"fr","admin":[],"appels":{}}
    jsonWrite()

@client.event
async def on_guild_remove(guild):
    global liste_eleves
    del liste_eleves[str(guild.id)]
    jsonWrite()

@client.command()
async def send(message,channel):
    await channel.send(message)

@client.command()
async def add_reaction(emoji,message):
    await message.add_reaction(emoji)

@client.command()
async def remove_reaction(emoji,message,user):
    await message.remove_reaction(emoji,user)

@client.command()
async def clear_reaction(emoji,message):
    await message.clear_reaction(emoji)

@client.event
async def on_reaction_add(reaction, user):
    global liste_eleves
    idMessage=str(reaction.message.id)
    idGuild=str(reaction.message.guild.id)

    if idMessage in liste_eleves[idGuild]['appels']: #si c'est un message d'appel lancé par un professeur
        reactionContent=str(reaction).strip(" ")

        if reactionContent=="✅": #si l'utilisateur a coché présent
            if  got_the_role(liste_eleves[idGuild]['appels'][idMessage]['ClasseRoleID'],user.roles): #si user a le role de la classe correspondante
                liste_eleves[idGuild]['appels'][idMessage]['listStudents'].append([user.display_name,user.id]) #on le rajoute à la liste d'appel

            elif not got_the_role(liste_eleves[idGuild]['botID'],user.roles):
                await remove_reaction("✅",reaction.message,user)
                await send("<@{}> : {}".format(user.id,lg.language(liste_eleves[idGuild]["language"],"cantNotify")),reaction.message.channel)


        elif reactionContent=="🆗": #si l'utilisateur a coché OK
            if got_the_role(liste_eleves[idGuild]["admin"],user.roles): # est prof

                await send("<@{}> :{} <@&{}>".format(user.id,lg.language(liste_eleves[idGuild]["language"],"FinishCall"),liste_eleves[idGuild]['appels'][idMessage]['ClasseRoleID']),reaction.message.channel)
                await clear_reaction("✅",reaction.message)
                await clear_reaction("🆗",reaction.message)
                await send(returnPresent(reaction.message),reaction.message.channel)
                del liste_eleves[idGuild]['appels'][idMessage]

            elif not got_the_role(liste_eleves[idGuild]['botID'],user.roles): #pas le bot
                await remove_reaction("🆗",reaction.message,user)
                await send("<@{}> : {}".format(user.id,lg.language(liste_eleves[idGuild]["language"],"NoRightEnd")),reaction.message.channel)

        else: # autre emoji
            await remove_reaction(reactionContent,reaction.message,user)
            await send("<@{}> : {}".format(user.id,lg.language(liste_eleves[idGuild]["language"],"unknowEmoji")),reaction.message.channel)


@client.command()
async def appel(context,args):
    global liste_eleves
    print(liste_eleves[str(context.guild.id)])

    # if len(args)>1:
    #     raise commands.errors.CommandNotFound
    classe=convert(args)
    print(liste_eleves[str(context.guild.id)]["language"])
    if got_the_role(liste_eleves[str(context.guild.id)]["admin"],context.author.roles):
        liste_eleves[str(context.guild.id)]['appels'][str(context.message.id)]={'ClasseRoleID':classe,'listStudents':[]}
        await send(lg.language(liste_eleves[str(context.guild.id)]["language"],"startCall"),context.channel)
        await add_reaction("✅",context.message) #on rajoute les réactions ✅ & 🆗
        await add_reaction("🆗",context.message)
    else:
        await send("<@{}> : {}".format(context.author.id,lg.language(liste_eleves[str(context.guild.id)]["language"],"notTeacher")),context.channel)

@client.command()
async def ListRoles(context):
    for i in liste_eleves[str(context.guild.id)]["admin"]:
        await send("<@&{}> : {}".format(i,discord.utils.get(context.guild.roles, id=i)),context.channel)

@client.command()
async def addRole(context,*args):
    global liste_eleves

    guild=str(context.guild.id)

    if len(liste_eleves[guild]["admin"])>0:
        if got_the_role(liste_eleves[guild]["admin"],context.author.roles):
            for i in args:
                liste_eleves[guild]["admin"].append(convert(i))
                await send('*{} :*{}'.format(lg.language(liste_eleves[guild]["language"],"newAdmin"),i),context.channel)
            jsonWrite()
        else:
            await send("<@{}> : {}".format(context.author.id,lg.language(liste_eleves[guild]["language"],"NoPrivileges")),context.channel)
    else:
        for i in args:
            liste_eleves[guild]["admin"].append(convert(i))
            
            await send('*{}: *{}'.format(lg.language(liste_eleves[guild]["language"],"newAdmin"),i),context.channel)
        jsonWrite()


@client.command()
async def rmRole(context,*args):
    global liste_eleves
    guild=str(context.guild.id)
    if len(liste_eleves[guild]["admin"])>0:
        if got_the_role(liste_eleves[guild]["admin"],context.author.roles):
            for i in args:
                i=convert(i)
                if i in liste_eleves[guild]["admin"]:
                    liste_eleves[guild]["admin"].remove(i)
                    await send('*{}:*<@&{}>'.format(lg.language(liste_eleves[guild["language"]],"removeAdmin"),i),context.channel)
                else:
                    await send("*<@&{}> {}*".format(i,lg.language(liste_eleves[guild["language"]],"notAdmin")),context.channel)
            jsonWrite()
        else:
            await send("<@{}> : {}".format(context.author.id,lg.language(liste_eleves[guild["language"]],"NoPrivileges")),context.channel)
    else:
        await send(lg.language(liste_eleves[guild["language"]],"zeroPrivileges"),context.channel)

@client.command()
async def language(context,langue):
    if langue in ["fr","en"]:
        liste_eleves[str(context.guild.id)]["language"]=langue
        await send(lg.language(langue,"changeLanguage"),context.channel)
        jsonWrite()
    else:
        await send("Unknow language",context.channel)



@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await send(lg.language(liste_eleves[str(ctx.guild.id)]["language"],"commands"),ctx.message.channel)
    raise error

client.run(token)
client.add_command(appel)
client.add_command(addRole)
client.add_command(rmRole)
client.add_command(ListRoles)
client.add_command(language)