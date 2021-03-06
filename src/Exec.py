from discord.ext.commands import Context


class NotEpitaServ(Exception):
    def __init__(self, context: Context = None):
        super().__init__(f"{context.author} is trying to use calendar for \"{context.guild.name}\" server")