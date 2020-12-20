import discord
from datetime import datetime
from discord import embeds
from discord.ext import commands
from discord.ext.commands.core import is_owner
from data import *

import sys

# import time
token = sys.argv[1]
intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, dm_messages=True,
                          guild_reactions=True)
client = commands.Bot(command_prefix= get_prefix, intents=intents)

appelList = {}


def got_the_role(role, author: list):
    if isinstance(role, list):
        for i in role:
            if i in [y.id for y in author]:
                return True
    elif isinstance(role, int):
        return role in [y.id for y in author]

def name(member):
    if member.nick is not None:
        return member.nick
    else:
        return member.name

def returnPresent(idmessage: str, guildID: int, rolelist: list):
    """
    Retourne la liste des élèves ayant notifié leur présence sur un message.
    """
    liste = appelList[idmessage]['listStudents']
    # messages = returnLanguage(readGuild(guildID)["language"], "endcall")
    
    messageA = ""
    messageB = ""
    eleve = []
    for member in liste:
        if not member.id in eleve:
            messageA += "*{}* <@{}>\n".format(name(member), member.id)
            eleve.append(member.id)
            if rolelist is not None: rolelist.remove(member)
    if rolelist != []:
        for member in rolelist:
            messageB += "*{}* <@{}>\n".format(name(member), member.id)
    return (messageA,messageB,rolelist)

async def sendabsents(absents: list,guild,url : str, author,channel):
    langmsg=returnLanguage(readGuild(guild.id)["language"], "sendabsents")
    embed = discord.Embed(color=discord.Colour.red(), title="Absence")
    embed.set_author(name=name(author),icon_url=author.avatar_url)
    embed.add_field(name=langmsg[0],value=name(author))
    embed.add_field(name=langmsg[1],value=guild)
    embed.add_field(name=langmsg[2],value=channel)
    embed.add_field(name=langmsg[3][0],value="[{}]({})".format(langmsg[3][1],url))
    for member in absents:
        await member.send(embed=embed)

async def sendlist(member,classe,guildID,students):
    """
    Send the list to the teacher
    """
    langmsg=returnLanguage(readGuild(guildID)["language"], "class")
    embed = discord.Embed(color=discord.Colour.blue(), title=langmsg[1])
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.add_field(name=langmsg[0], value=classe)

    embed.add_field(name="Present students",value=students[0])
    if students[1]!= "": embed.add_field(name="Absents students",value=students[1])
    else: embed.add_field(name="All students are present",value=":thumbsup:")


    await member.send(embed=embed)

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
    if guild.system_channel is not None:
        message = returnLanguage("en","commands")
        embed = discord.Embed(color=discord.Colour.blue(), title="I joined the Server",description="Here the list of commands you can use:")
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        # embed.add_field(name="call", value=classe)
        embed = CompleteHelpEmbed(embed,message)
        await guild.system_channel.send(embed=embed)



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
                    await finishCall(reaction.message.channel,entry,idGuild,reaction)
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

async def finishCall(channel,entry,idGuild,reaction):
    embed = discord.Embed(color=discord.Colour.blue())
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    if appelList[entry]['listStudents']==[]:
        embed.title = "No students presents, please use 🛑 to cancel the call"
        embed.color=discord.Color.red()
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/remove.png")

        await channel.send(embed=embed)
    else:
        presentsMessage, absentsMessage, listAbsents =returnPresent(entry, idGuild,reaction.message.guild.get_role(appelList[entry]['ClasseRoleID']).members)
        
        
        embed.add_field(name="Present students",value=presentsMessage)

        if absentsMessage != "":embed.add_field(name="Absents students",value=absentsMessage) 
        else: embed.add_field(name="All students are present",value=":thumbsup:")
        # embed.set_footer("The teacher and  MP")
        # send the list of students to the teacher who started the call
        await channel.send(embed=embed)
        await sendlist(reaction.message.author,reaction.message.guild.get_role(appelList[entry]['ClasseRoleID']),idGuild,[presentsMessage,absentsMessage])

        await sendabsents(listAbsents,reaction.message.guild,"https://discord.com/channels/{}/{}/{}".format(idGuild,reaction.message.channel.id,reaction.message.id),reaction.message.author,reaction.message.channel)

@client.command(aliases=['call'])
async def appel(context, *args):
    global appelList
    classe = convert(args[0])
    data = readGuild(context.guild.id)
    if classe is None:
        await context.channel.send(returnLanguage(data["language"], "rolenotValid"))
    else:
        if got_the_role(data["admin"], context.author.roles):
            appelList["{}-{}".format(context.guild.id, context.message.id)] = {'ClasseRoleID': classe,'listStudents': []}
            message=returnLanguage(data["language"], "startcall")

            embed = discord.Embed(color=discord.Colour.green(), title=message[0],description=message[1])
            embed.set_author(name=name(context.message.author),
                     icon_url=context.message.author.avatar_url)
            embed.add_field(name="**__{}__**".format(message[2]), value=args[0])
            embed.set_footer(text=message[3])

            await context.channel.send(embed=embed)
            await  context.message.add_reaction("✅")  # on rajoute les réactions ✅ & 🆗
            await  context.message.add_reaction("🆗")
            await  context.message.add_reaction("🛑")
        else:
            await context.channel.send("<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "notTeacher")))


@client.command(aliases=['roles', 'Roles', 'list','admin','admins'])
async def ListRoles(context, *args):
    message = ""
    embed = discord.Embed(color=discord.Colour.orange())
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    admins = readGuild(context.guild.id)["admin"]
    if admins == []:
        embed.add_field(name="**Admins :**",value="There is no admin yet")
    else:
        for i in admins:
            message += "<@&{}>\n".format(i)
        embed.add_field(name="**Admins :**",value=message)
    await context.channel.send(embed=embed)


@client.command(aliases=['add'])
async def addRole(context, *args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if data["admin"]!=[] and not got_the_role(data["admin"], context.author.roles):
        await embedError(context.channel,returnLanguage(data["language"], "NoPrivileges"))
    else:
        message = str()
        langMessage=returnLanguage(data["language"], "newAdmin")
        embed = discord.Embed(color=discord.Colour.orange())
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            
        a = ""
        b = ""
        for i in args:
            role = convert(i)

            if not role in data["admin"]:
                data["admin"].append(role)
                a += i + "\n"
            else:
                b += i + "\n"
        
        if a == "" and b == "":
            embed.add_field(name="You need to add roles to use the command",value="add @role1 @role2")
            await context.channel.send(embed=embed)
        else:
            if a != "" : embed.add_field(name="Added roles",value=a)
            if b != "" : embed.add_field(name="Already added",value=b)
            editGuild(guild, data)
            await AdminCommand(context,embed)

@client.command(aliases=['rm', 'del', 'remove'])
async def rmRole(context, *args):
    guild = str(context.guild.id)
    data = readGuild(guild)
    if data["admin"] !=[]:
        if got_the_role(data["admin"], context.author.roles):
            embed = discord.Embed(color=discord.Colour.orange())
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            
            a = ""
            b = ""

            for i in args:
                role = convert(i)
                if role in data["admin"]:
                    a+= "<@&{}>\n".format(role)
                    data["admin"].remove(role)
                else:
                    b+= "<@&{}>\n".format(role)
            if a == "" and b == "":
                embed.add_field(name="You need to write role(s) to use the command",value="rm @role")
                await context.channel.send(embed=embed)
            else:
                if a != "" : embed.add_field(name="Removed roles",value=a)
                if b != "" : embed.add_field(name="Was not an admin",value=b)
                editGuild(guild, data)
                await AdminCommand(context,embed)
        else:
            await embedError(context.channel,returnLanguage(data["language"], "NoPrivileges"))
    else:
        await embedError(context.channel,returnLanguage(data["language"], "zeroPrivileges"))

@client.command()
async def prefix(context, arg):
    data = readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author.roles):
        try:
            set_prefix(context.guild.id,arg)
            embed = discord.Embed(color=discord.Colour.orange(), title=returnLanguage(readGuild(context.guild.id)["language"], "newPrefix")+"**{}**".format(arg))
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                        icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            await AdminCommand(context,embed)
        except commands.errors.MissingRequiredArgument:
            embedError("You did not specify a prefix")
    else:
        await embedError(context.channel,returnLanguage(data["language"], "NoPrivileges"))


@client.command(aliases=["lang"])
async def language(context, langue=None):
    if langue in ["fr", "en", "de"]:
        data = readGuild(context.guild.id)
        if got_the_role(data["admin"], context.author.roles):
            data["language"] = langue
            embed = discord.Embed(color=discord.Colour.orange(), title=returnLanguage(langue, "changeLanguage"))
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            await AdminCommand(context,embed)
            editGuild(context.guild.id, data)
        else:
            
            await embedError(context.channel,returnLanguage(data["language"], "NoPrivileges"))
    else:
        await embedError(context.channel,"Unknow language:\n**Languages :**\n• English: en\n• French: fr\n• German: de")


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
    embed = CompleteHelpEmbed(embed,message)
    

    await context.message.author.send(message[0], embed=embed)
    # await ctx.message.author.send()

@client.command()
async def reset(context):
    data=readGuild(context.guild.id)
    if got_the_role(data["admin"], context.author.roles):
        data["admin"]=[]
        data["language"]="en"
        data["prefix"]=".Check "
        data["sysMessages"]=True
        editGuild(context.guild.id,data)

        embed = discord.Embed(color=discord.Colour.orange(), title="**__Factory reset:__**\nLanguage set to English\nAdmins list reseted\n**Prefix :** `.Check`")
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        
        await AdminCommand(context,embed)
        
    else:
        await embedError(context.channel,returnLanguage(data["language"], "NoPrivileges"))

async def embedError(channel,message):
    embed = discord.Embed(color=discord.Color.red(), title=message)
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    # embed.add_field(name="Permission Denied",value=message)
    embed.set_thumbnail(url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/remove.png")
    await channel.send(embed=embed)

@client.command(aliases=["sys"])
async def sysMessages(context):
    """
    Activate/Desactivate system message
    
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
        await AdminCommand(context,embed)
    else:
        await embedError(context.channel,returnLanguage(data["language"], "NoPrivileges"))

async def AdminCommand(context,embed: discord.Embed):
    
    await context.channel.send(embed=embed)
    #  
    
    if readGuild(context.guild.id)["sysMessages"] and context.guild.system_channel is not None and context.guild.system_channel != context.channel:
        embed.add_field(name="Link to the action",value="[Link]({})".format(context.message.jump_url))
        embed.add_field(name="Used by",value=context.message.author.mention)
        await context.guild.system_channel.send(embed=embed)
    # jump_url

    
def CompleteHelpEmbed(embed: discord.Embed,message):
    embed.add_field(name=message[1][0], value=message[1][1])
    embed.add_field(name=message[2][0], value=message[2][1])
    embed.add_field(name=message[3][0], value=message[3][1])
    embed.add_field(name=message[4][0], value=message[4][1])
    embed.add_field(name=message[5][0], value=message[5][1])
    embed.add_field(name=message[6][0], value=message[6][1])
    embed.add_field(name=message[7][0], value=message[7][1])
    embed.add_field(name=message[8][0], value=message[8][1])
    embed.add_field(name=message[9][0], value=message[9][1])
    return embed

client.run(token)
client.add_command(appel)
client.add_command(help)
client.add_command(addRole)
client.add_command(rmRole)
client.add_command(ListRoles)
client.add_command(language)
client.add_command(prefix)
client.add_command(reset)
client.add_command(sysMessages)
