if __name__ == "__main__":
    from discord.ext import commands
    from src.data import *
    from src import Embed
    import sys
    from src.tools import Tools
    from src.Attendance.call import Calling
    from src.adminCmd import Admin
    from src.calendar import calDiscord as Calendar

    import logging

    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    CheckClass = Calling()
    token = sys.argv[1]
    intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, dm_messages=True,
                              guild_reactions=True)
    client = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)
    AdminInstance = Admin()

    calendar = Calendar.CalCog(client)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=".Check help"))
    print("Bot is ready!")
    # TODO : REMOVE COMMENT
    # await calendar.StartCalendar()


def is_teacher():
    async def predicate(context):
        data = Server(context.guild.id)
        if Tools.got_the_role(data.teacher, context.author):
            return True
        await Tools.SendError(context.channel, data.returnLanguage("notTeacher"))
        return False

    return commands.check(predicate)


def is_admin():
    async def predicate(context):
        data = Server(context.guild.id)
        if Tools.got_the_role(data.admin, context.author):
            return True
        await Tools.SendError(context.channel, data.returnLanguage("NoPrivileges"))
        return False

    return commands.check(predicate)


@client.command(aliases=["Call, attendance"])
@is_teacher()
async def call(context, *args):
    await CheckClass.StartCall(client, context, args)


@client.event
async def on_reaction_add(reaction, user):
    if isinstance(reaction.message.channel,
                  discord.DMChannel) and reaction.message.author == client.user \
            and user != client.user and str(reaction.emoji) == "⏰":
        await CheckClass.LateStudent(reaction.message)


@client.group()
async def admin(context):
    if context.invoked_subcommand is None:
        embed = Embed.AdminHelp()
        embed.add_field(name="admin help", value="Show this message")
        await context.channel.send(embed=embed)


@client.group()
async def teacher(context):
    if context.invoked_subcommand is None:
        embed = Embed.TeacherHelp()
        embed.add_field(name="teacher help", value="Show this message")
        await context.channel.send(embed=embed)


@client.group()
async def cal(context):
    await Calendar.IsEpitaServer(context)
    if context.invoked_subcommand is None:
        embed = Embed.CalHelp()
        embed.add_field(name="cal help", value="Show this message")
        await context.channel.send(embed=embed)


@client.event
async def on_guild_join(guild: discord.Guild):  # readGuild(message.guild.id)
    """
    Send help message  when joining a server
    """

    Create_Guild(guild.id)
    if guild.system_channel is not None:
        await guild.system_channel.send(embed=Embed.HelpMsg())
        await guild.system_channel.send(embed=Embed.TeacherHelp())
        await guild.system_channel.send(embed=Embed.AdminHelp())


@client.event
async def on_guild_remove(guild):
    try:
        Remove_Guild(guild.id)
    except FileNotFoundError:
        print("FileNotFoundError", guild, guild.id)


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

    if value == "teacher":
        role = Server(context.guild.id).teacher
    elif value == "admin":
        role = Server(context.guild.id).admin

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


#######################################################
##  Admin/Teacher role gestion
#######################################################
@admin.command()
async def add(context):
    await AdminInstance.addRole(context, "admin")


@teacher.command()
async def add(context):
    await AdminInstance.addRole(context, "teacher")


@admin.command(aliases=['del', 'remove'])
@is_admin()
async def rm(context):
    await AdminInstance.rmRole(context, "admin")


@teacher.command(aliases=['del', 'remove'])
@is_admin()
async def rm(context):
    await AdminInstance.rmRole(context, "teacher")


#######################################################
##  Admin subcommands
#######################################################


@admin.command()
@is_admin()
async def prefix(context, arg):
    await AdminInstance.prefix(context, arg)


@admin.command(aliases=["lang"])
@is_admin()
async def language(context, lang=None):
    await AdminInstance.language(context, lang)


@admin.command()
@is_admin()
async def delay(context, time=None):
    await AdminInstance.Delay(context, time)


@admin.command()
@is_admin()
async def ShowPresents(context):
    await AdminInstance.ShowPresents(context)


@admin.command()
async def reset(context):
    await AdminInstance.Reset(context)


@admin.command(aliases=["sys"])
@is_admin()
async def sysMessages(context):
    await AdminInstance.sysMessages(context)


@admin.command()
@is_admin()
async def DM(context):
    await AdminInstance.DeactivateMP(context)


#######################################################
#######################################################

@client.event
async def on_command_error(context, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await Tools.SendError(context.channel, "Unknown Command. Use help command")
    else:
        await Tools.SendError(context.channel, str(error))
# print(error, context.guild, context.guild.id, context.channel, context.message.jump_url)


@client.command()
async def settings(context):
    data = Server(context.guild.id)
    embed = Embed.CompleteEmbed(color=discord.Colour.orange(), title="Current settings")

    embed.add_field(name="• System Messages", value=str(data.sysMessages), inline=False)
    embed.add_field(name="• Private Messages", value=str(data.mp), inline=False)
    embed.add_field(name="• Show present students after call", value=str(data.showPresents), inline=False)
    embed.add_field(name="• Language", value=str(data.language), inline=False)
    embed.add_field(name="• Prefix", value=str(data.prefix), inline=False)
    embed.add_field(name="• Delay in minutes", value=str(data.delay), inline=False)

    await context.channel.send(embed=embed)


#######################################################
##  Calendar commands
#######################################################
@cal.command()
@is_admin()
async def add(context: commands.Context, arg):
    await Calendar.AddCalendar(context, arg)


@cal.command()
@is_admin()
async def remove(context: commands.Context):
    await Calendar.DelCalendar(context)


@cal.command()
async def list(context: commands.Context):
    await Calendar.ListCalendar(context, client)


#######################################################
##  Help commands
#######################################################
@teacher.command(aliases=["commands,command"])
async def help(context):
    await context.message.author.send("Here the list of subcommand you can use with *teacher*",
                                      embed=Embed.TeacherHelp())


@admin.command(aliases=["commands,command"])
async def help(context):
    await context.message.author.send("Here the list of subcommand you can use with *admin*",
                                      embed=Embed.AdminHelp())


@cal.command(aliases=["commands,command"])
async def help(context):
    await context.message.author.send("Here the list of subcommand you can use with *cal*",
                                      embed=Embed.CalHelp())


@client.command(aliases=["commands,command"])
async def help(context):
    await context.message.author.send(embed=Embed.HelpMsg())


client.add_cog(calendar)
client.run(token)
