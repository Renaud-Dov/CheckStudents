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
    await client.change_presence(activity=discord.Game(name=".Check help"))
    print("Bot is ready!")
    client.load_extension("src.roles.admin")
    client.load_extension("src.roles.teacher")


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


#######################################################
#######################################################

@client.event
async def on_command_error(context: commands.Context, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await Tools.SendError(context.channel, "Unknown Command. Use help command")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await Tools.SendError(context.channel, "Missing argument", desc=str(error))
    elif isinstance(error, commands.errors.CheckFailure):
        pass
    else:
        await Tools.SendError(context.channel, "An error occurred", str(error))
        logger.error(f"{context.guild}-{context.channel} ({context.message.author}):{error}")
        raise error


@client.command()
async def settings(context):
    data = Server(context.guild.id)
    embed = Embed.BasicEmbed(color=discord.Colour.orange(), title="Current settings")

    embed.add_field(name="• System Messages", value=str(data.sysMessages), inline=False)
    embed.add_field(name="• Private Messages", value=str(data.mp), inline=False)
    embed.add_field(name="• Show present students after call", value=str(data.showPresents), inline=False)
    embed.add_field(name="• Language", value=str(data.language), inline=False)
    embed.add_field(name="• Prefix", value=str(data.prefix), inline=False)
    embed.add_field(name="• Delay in minutes", value=str(data.delay), inline=False)

    await context.channel.send(embed=embed)


@client.command(hidden=True)
@commands.is_owner()
async def load(context, *, module: str):
    """Loads a module."""
    try:
        client.load_extension(module)
    except Exception as e:
        print(f"Error on load {module}.", e)
        await context.channel.send(f"Error on load **{module}**.")
    else:
        print(f"successfully loaded {module}.")
        await context.channel.send(f"successfully loaded **{module}**.")


@client.command()
@commands.is_owner()
async def unload(context, module: str):
    """Unloads a module."""
    try:
        client.unload_extension(module)
    except Exception as e:
        print(f"Error on unload {module}.", e)
        await context.channel.send(f"Error on unload **{module}**.")
    else:
        print(f"successfully unloaded {module}.")
        await context.channel.send(f"successfully unloaded **{module}**.")


@client.command()
@commands.is_owner()
async def reload(context, module: str):
    """Reloads a module."""
    try:
        client.reload_extension(module)
    except Exception as e:
        print(f"Error on reload {module}.", e)
        # await self.bot.say('{}: {}'.format(type(e).__name__, e))
        await context.channel.send(f"Error on reload **{module}**.")
    else:
        print(f"successfully reloaded {module}.")
        await context.channel.send(f"successfully reloaded **{module}**.")


#######################################################
##  Help commands
#######################################################


@client.command(aliases=["commands,command"])
async def help(context):
    await context.message.author.send(embed=Embed.HelpMsg())


client.run(os.environ.get("DISCORD_TOKEN"))
