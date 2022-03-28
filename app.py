import discord.ui

if __name__ == "__main__":
    from discord.ext import commands
    from src.data import *
    from src import Embed
    import sys, os
    from src.tools import Tools
    from src.Attendance.call import Calling
    from src.roles.teacher import is_teacher

    import logging

    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

    CheckClass = Calling()
    intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, dm_messages=True,
                              guild_reactions=True, message_content=True)
    client = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)


@client.event
async def on_ready():
    print("Bot is ready!")


def updateEmbed() -> [discord.Embed, discord.ui.View]:
    embed = Embed.CompleteEmbed(title="CheckStudents v1.0.0 is now available!",
                                description="**You may need to kick the bot and invite it again to the server to "
                                            "update completely the bot.**")
    embed.set_image(
        url="https://user-images.githubusercontent.com/14821642/160217288-46ea127e-2b27-487f-897f-61afd807331a.png")

    view = discord.ui.View()
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.green, label=f"Update now", emoji="🚀",
                                    url=f"https://discord.com/oauth2/authorize?client_id=760157065997320192&permissions=2048&scope=applications.commands%20bot",
                                    ))
    view.add_item(discord.ui.Button(style=discord.ButtonStyle.green, label=f"Changelog", emoji="📝",
                                    url=f"https://github.com/Renaud-Dov/CheckStudents/blob/master/CHANGELOG.md"))

    return embed, view


@client.command(aliases=["Call, attendance"])
async def call(context, *args):
    embed, view = updateEmbed()
    embed.add_field(name="Command call", value="Now replaced by /call @role")
    await context.message.author.send(embed=embed, view=view)


#######################################################
#######################################################

# @client.event
# async def on_command_error(context: commands.Context, error):
#     if isinstance(error, commands.errors.CommandNotFound):
#         await Tools.SendError(context.channel, "Unknown Command. Use help command")
#     elif isinstance(error, commands.errors.MissingRequiredArgument):
#         await Tools.SendError(context.channel, "Missing argument", desc=str(error))
#     elif isinstance(error, commands.errors.CheckFailure):
#         pass
#     else:
#         await Tools.SendError(context.channel, "An error occurred", str(error))
#         logger.error(f"{context.guild}-{context.channel} ({context.message.author}):{error}")
#         raise error


@client.command()
async def settings(context):
    embed, view = updateEmbed()
    embed.add_field(name="Command settings", value="Now replaced by /panel")
    await context.message.author.send(embed=embed, view=view)


@client.command()
async def admin(context):
    embed, view = updateEmbed()
    embed.add_field(name="Command admin", value="Now replaced by /panel")
    await context.message.author.send(embed=embed, view=view)


#######################################################
##  Help commands
#######################################################


@client.command(aliases=["commands,command"])
async def help(context):
    await context.message.author.send(embed=Embed.HelpMsg())


client.run(os.environ.get("DISCORD_TOKEN"))
