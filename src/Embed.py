import discord


def AdminHelp():
    embed = CompleteEmbed(color=discord.Colour.green(), title="Admin settings subcommands:",
                          description="You must be an admin in order to execute these commands")

    embed.add_field(name="admin add @role1/@user...", value="Add admin privileges to one or more roles or users")
    embed.add_field(name="admin rm @role1/@user...", value="Remove admin privileges to one or more roles or users")
    embed.add_field(name="admin list", value="Return roles and users that have admin privileges")
    embed.add_field(name="admin sys", value="Enable/Disable system messages")
    embed.add_field(name="admin DeactivateMP", value="Enable/Disable private messages")
    embed.add_field(name="admin language", value="Set server language bot")
    embed.add_field(name="admin prefix", value="Changes bot prefix")
    embed.add_field(name="admin reset", value="Resets settings for the server")
    embed.add_field(name="admin ShowPresents", value="Enable/Disable presents students display in call summary")
    embed.add_field(name="admin delay", value="Set delay for absent students to get marked as late")
    return embed


def TeacherHelp():
    embed = CompleteEmbed(color=discord.Colour.green(), title="Teacher settings subcommands:",
                          description="You must be an admin in order to execute these commands")

    embed.add_field(name="teacher add @role1 @role2...", value="Add teacher privileges to one or more roles or users")
    embed.add_field(name="teacher rm @role1 @role2...", value="Remove teacher privileges to one or more roles or users")
    embed.add_field(name="teacher list", value="Return roles and users that have admin privileges")
    return embed


def HelpMsg():
    embed = CompleteEmbed(color=discord.Colour.green(), title="CheckStudents commands",
                          description="Here the list of commands you can use with the bot")

    embed.add_field(name="call @class", value="Start the call, *replace by the corresponding class*", inline=False)
    embed.add_field(name="admin *subcommand*", value="admin roles commands (see admin subcommands)", inline=False)
    embed.add_field(name="teacher *subcommand*", value="teacher role commands (see teacher subcommands)", inline=False)
    embed.add_field(name="cal *subcommand*", value="cal role commands (see cal subcommands)", inline=False)
    embed.add_field(name="settings", value="Return settings values", inline=False)
    embed.add_field(name="admin help", value="Return admin subcommands", inline=False)
    embed.add_field(name="teacher help", value="Return teacher subcommands", inline=False)
    embed.add_field(name="cal help", value="Return calendar subcommands", inline=False)
    return embed



def BasicEmbed(title=None, description=None, color=None):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    return embed


def CompleteEmbed(title=None, description=None, color=None):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    embed.set_footer(text="Made with ❤️ by BugBear",
                     icon_url="https://avatars.githubusercontent.com/u/14821642")
    return embed
