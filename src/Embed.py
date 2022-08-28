import discord


def HelpMsg():
    embed = CompleteEmbed(color=discord.Colour.green(), title="CheckStudents commands",
                          description="Here the list of commands you can use with the bot")

    embed.add_field(name="/call @class", value="Start the call, *replace by the corresponding class*", inline=False)
    embed.add_field(name="/panel", value="Edit bot config", inline=False)
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
