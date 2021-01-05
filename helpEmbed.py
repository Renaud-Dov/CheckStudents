import discord


def AdminHelp():
    embed = discord.Embed(color=discord.Colour.green(), title="Admin settings subcommands:",
                          description="You must be an admin in order to execute these commands")
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.add_field(name="admin add @role1 @role2...", value="Add admin privileges to one or more roles")
    embed.add_field(name="admin rm @role1 @role2...", value="Remove admin privileges to one or more roles")
    embed.add_field(name="admin list", value="return admin list")
    embed.add_field(name="admin sys", value="Activate/Deactivate system messages")
    embed.add_field(name="admin DeactivateMP", value="Activate/Deactivate private messages")
    embed.add_field(name="admin language", value="Set server language bot")
    embed.add_field(name="admin prefix", value="Change bot prefix")
    embed.add_field(name="admin reset", value="Reset settings")
    embed.add_field(name="admin ShowPresents", value="Activate/Deactivate Show presents students in call summary")
    return embed


def TeacherHelp():
    embed = discord.Embed(color=discord.Colour.green(), title="Teacher settings subcommands:",
                          description="You must be an admin in order to execute these commands")
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.add_field(name="teacher add @role1 @role2...", value="Add teacher privileges to one or more roles")
    embed.add_field(name="teacher rm @role1 @role2...", value="Remove teacher privileges to one or more roles")
    embed.add_field(name="teacher list", value="return teachers list")
    return embed


def HelpMsg():
    embed = discord.Embed(color=discord.Colour.green(), title="CheckStudents commands",
                          description="Here the list of commands you can use with the bot")
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.add_field(name="call @class", value="Start the call, *replace by the corresponding class*", inline=False)
    embed.add_field(name="admin *subcommand*", value="admin roles commands (see admin subcommands)", inline=False)
    embed.add_field(name="teacher *subcommand*", value="teacher role commands (see teacher subcommands)", inline=False)
    embed.add_field(name="settings", value="Return settings values", inline=False)
    embed.add_field(name="admin help", value="Return admin subcommands", inline=False)
    embed.add_field(name="teacher help", value="Return teacher subcommands", inline=False)
    return embed
