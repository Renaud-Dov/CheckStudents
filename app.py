from src.settings import Settings

if __name__ == "__main__":
    from discord import app_commands
    from src.data import *
    import os
    from src.tools import Tools
    from src.call import Calling
    # from src.roles.teacher import is_teacher

    import logging

    logger = logging.getLogger('discord')
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

intents = discord.Intents(messages=True, dm_messages=True, guild_reactions=True, members=True, guilds=True)
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

CheckClass = Calling(client)


@client.event
async def on_ready():
    print("Bot is ready!")
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=f"{len(client.guilds)} servers"))


@tree.command(guild=discord.Object(id=760808606672093184), name="update", description="Update commands")
async def updateCommands(interaction: discord.Interaction):
    await tree.sync(guild=discord.Object(id=760808606672093184))
    await tree.sync()
    await interaction.response.send_message("Updated commands")


@tree.command(description="Start the attendance")
@app_commands.describe(role="Which role you want to check the attendance")
@app_commands.describe(delay="Time for absent to be counted as late 0-60 (If 0, no late)")
async def call(interaction: discord.Interaction, role: discord.Role, delay: app_commands.Range[int, 0, 60] = 10):
    data = Server(interaction.guild_id)
    delay *= 60
    if not Tools.has_permission(data.teacher, interaction.user):
        await Tools.SendError(interaction, "You don't have teacher role")
    else:
        await CheckClass.StartCall(interaction, role, delay)



@client.event
async def on_guild_join(guild: discord.Guild):  # readGuild(message.guild.id)
    """
    Send help message  when joining a server
    """

    Create_Guild(guild.id)
    await tree.sync(guild=guild)
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                           name=f"{len(client.guilds)} servers"))


@client.event
async def on_guild_remove(guild):
    try:
        Remove_Guild(guild.id)
    except FileNotFoundError:
        print("FileNotFoundError", guild, guild.id)


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


tree.add_command(Settings())
client.run(os.environ.get("DISCORD_TOKEN"))
