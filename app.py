if __name__ == "__main__":
    from discord.ext import commands
    from src.data import *
    from src import helpEmbed
    import sys
    from src.tools import Tools
    from src.call import Calling
    from src.adminCmd import Admin

    CheckClass = Calling()
    token = sys.argv[1]
    intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, dm_messages=True,
                              guild_reactions=True)
    client = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)
    AdminInstance = Admin()


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=".Check help"))
    print("Bot is ready!")


@client.command(aliases=["call"])
async def Call(context, *args):
    await CheckClass.Call(context, args)


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


@client.event
async def on_guild_join(guild: discord.Guild):  # readGuild(message.guild.id)
    """
    Send help message  when joining a server
    """

    createGuild(guild.id)
    if guild.system_channel is not None:
        await guild.system_channel.send(embed=helpEmbed.HelpMsg())
        await guild.system_channel.send(embed=helpEmbed.TeacherHelp())
        await guild.system_channel.send(embed=helpEmbed.AdminHelp())


@client.event
async def on_guild_remove(guild):
    try:
        removeGuild(guild.id)
    except FileNotFoundError:
        print("FileNotFoundError", guild, guild.id)


@client.event
async def on_reaction_add(reaction: discord.Reaction, user):
    if isinstance(reaction.message.channel, discord.TextChannel):
        idMessage = str(reaction.message.id)
        idGuild = str(reaction.message.guild.id)
        entry = idGuild + "-" + idMessage

        if CheckClass.check(entry):  # if the message is a calling message
            await CheckClass.CheckReaction(client.user, reaction, user, entry)
    elif isinstance(reaction.message.channel, discord.DMChannel) and reaction.message.author == client.user:
        await CheckClass.LateStudent(client.user, user, reaction.message, reaction)


@admin.command(aliases=['Roles', 'list', 'admin', 'admins'])
async def roles(context):
    await ListRoles(context, "admin")


@teacher.command(aliases=['Roles', 'list', 'admin', 'admins'])
async def roles(context):
    await ListRoles(context, "teacher")


async def ListRoles(context, value: str):

    embed = discord.Embed(color=discord.Colour.orange())
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    role = readGuild(context.guild.id)[value]
    if not role["roles"] and not role["users"]:
        embed.add_field(name=f"**{value} :**", value=f"There is no {value} yet")
    else:
        if role["roles"]:
            message = ""
            for i in role["roles"]:
                message += f"<@&{i}>\n"
            embed.add_field(name=f"**{value.capitalize()} roles :**", value=message)

        if role["users"]:
            message = ""
            for i in role["users"]:
                message += f"<@{i}>\n"
            embed.add_field(name=f"**{value.capitalize()} users :**", value=message)
    await context.channel.send(embed=embed)


@admin.command()
async def add(context):
    await AdminInstance.addRole(context, "admin")


@teacher.command()
async def add(context):
    await AdminInstance.addRole(context, "teacher")


@admin.command(aliases=['del', 'remove'])
async def rm(context):
    await AdminInstance.rmRole(context, "admin")


@teacher.command(aliases=['del', 'remove'])
async def rm(context):
    await AdminInstance.rmRole(context, "teacher")


@admin.command()
async def prefix(context, arg):
    await AdminInstance.prefix(context, arg)


@admin.command(aliases=["lang"])
async def language(context, lang=None):
    await AdminInstance.language(context, lang)


@admin.command()
async def delay(context, time=None):
    await AdminInstance.Delay(context, time)


@client.event
async def on_command_error(context, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await Tools.embedError(context.channel, "Unknown Command. Use help command")
    # print(error, context.guild, context.guild.id, context.channel, context.message.jump_url)


@admin.command()
async def ShowPresents(context):
    await AdminInstance.ShowPresents(context)


@admin.command()
async def reset(context):
    await AdminInstance.reset(context)


@admin.command(aliases=["sys"])
async def sysMessages(context):
    await AdminInstance.sysMessages(context)


@admin.command()
async def DM(context):
    await AdminInstance.DeactivateMP(context)


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
    embed.add_field(name="• Delay in minutes", value=str(data["delay"]), inline=False)

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
