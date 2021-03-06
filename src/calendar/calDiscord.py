import src.calendar.Calendar as Calendar
from src.data import *
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import src.Exec as Exec
import src.Embed as Embed
from src.tools import Tools


def UpdateGrandtedGuild():
    with open('database/epita.serv.json', 'r') as outfile:
        var: dict = json.load(outfile)
    return [int(x) for x in var.keys()]


async def IsEpitaServer(context: commands.Context):
    if not context.guild.id in UpdateGrandtedGuild():
        await Tools.SendError(context.channel,
                              "You can't use Calendar functionality, it is reserved for Epita school servers.")
        raise Exec.NotEpitaServ(context)


class CalCog(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot

    async def StartCalendar(self):
        self.SendEventsOfTomorrow.start()

    @commands.command(aliases=["agenda", "calendar"])
    async def Calendar(self, context):
        await IsEpitaServer(context)
        data = Server(context.guild.id).calendar
        if str(context.channel.id) not in data:
            await Tools.SendError(context.channel, "There is no calendar set for this channel.")
            return None
        await self.SendEvents(context.channel, data[str(context.channel.id)])

    @staticmethod
    def RemoveCalAuto(channel: discord.TextChannel):
        data = Server(channel.guild.id)
        del data.calendar[str(channel.id)]
        data.Save_Settings()

    @staticmethod
    async def SendEvents(channel: discord.TextChannel, classroom_link: str):
        calendar = Calendar.Calendar(f"https://Ichronos.net/feed/{classroom_link}.ics")
        events = calendar.getClassOfTomorrow()

        embed = discord.Embed(
            title=f"Summary of tomorrow ({(datetime.utcnow() + timedelta(days=1)).strftime('%d/%m/%y')})",
            color=discord.Color.gold())
        embed.set_footer(text="Powered by iChronos Reloaded", icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/ichronos.png")
        if not events:
            embed.description = "There is no event for tomorrow"

        for event in events:
            if event.name.startswith("SEMAINE"):
                embed.description = f"Journée en {event.name.lstrip('SEMAINE EN ').casefold()}"
            else:
                # emoji = Data.GetEmoji(event.name.casefold()) if not None else ''
                start = event.beginTime.strftime("%Hh%M")
                end = event.endTime.strftime("%Hh%M")
                teacher = ' with {}'.format(event.teacher) if event.teacher != '' else ''

                embed.add_field(name=f"{event.name}{teacher}", value=f"{start} - {end}", inline=False)
        await channel.send(embed=embed)

    @tasks.loop(hours=24)
    async def SendEventsOfTomorrow(self):
        for guild in UpdateGrandtedGuild():
            data: dict = Server(guild).calendar
            for channel in data.items():
                a = self.bot.get_channel(int(channel[0]))
                await self.SendEvents(a, channel[1])


async def AddCalendar(context: commands.Context, arg):
    data = Server(context.guild.id)
    if str(context.channel.id) in data.calendar:
        await Tools.SendError(context.channel, "Calendar already added")
        return None

    embed = discord.Embed(color=discord.Color.red(), title=f"Added {arg} calendar for {context.channel} channel")
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    data.calendar[context.channel.id] = arg
    data.Save_Settings()
    await Tools.AdminCommand(context, embed)
    await CalCog.SendEvents(context.channel, data.calendar[context.channel.id])


async def DelCalendar(context: commands.Context):
    data = Server(context.guild.id)

    if str(context.channel.id) not in data.calendar:
        await Tools.SendError(context.channel, "Unknown calendar")
        return None

    cal = data.calendar.pop(str(context.channel.id))
    data.Save_Settings()

    embed = discord.Embed(color=discord.Color.red(), title=f"Removed {cal} calendar from {context.channel} channel")
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")

    await Tools.AdminCommand(context, embed)


async def ListCalendar(context: commands.Context, bot):
    data: dict = Server(context.guild.id).calendar
    embed = discord.Embed(color=discord.Color.green())
    embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                     icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
    for calendar in data.items():
        embed.add_field(name=bot.get_channel(int(calendar[0])), value=calendar[1])

    await context.channel.send(embed=embed)
