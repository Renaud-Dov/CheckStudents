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


def setup(bot: commands.Bot):
    bot.add_cog(CalCog(bot))


class CalCog(commands.Cog):
    def __init__(self, bot):
        self.started = False
        self.bot: discord.Client = bot

    @commands.group()
    async def cal(self, context):
        await IsEpitaServer(context)
        if context.invoked_subcommand is None:
            embed = Embed.CalHelp()
            embed.add_field(name="cal help", value="Show this message")
            await context.channel.send(embed=embed)

    @cal.command(aliases=["commands,command"])
    async def help(self, context):
        await context.message.author.send("Here the list of subcommand you can use with *cal*",
                                          embed=Embed.CalHelp())

    @cal.command()
    @commands.is_owner()
    async def StartCalendar(self, context):
        if not self.started:
            self.started = True
            await context.channel.send("Agenda activé")
            self.SendEventsOfTomorrow.start()

    @cal.command()
    @commands.is_owner()
    async def StopCalendar(self, context):
        if self.started:
            self.started = False
            self.SendEventsOfTomorrow.cancel()
            await context.channel.send("Agenda stoppé")

    @cal.command(aliases=["agenda", "calendar"])
    async def Calendar(self, context):
        await IsEpitaServer(context)
        data = Server(context.guild.id).calendar
        if str(context.channel.id) not in data:
            await Tools.SendError(context.channel, "There is no calendar set for this channel.")
            return None
        for cal in data[str(context.channel.id)]:
            await self.SendEvents(context.channel, cal)

    @staticmethod
    def RemoveCalAuto(channel: discord.TextChannel):
        data = Server(channel.guild.id)
        del data.calendar[str(channel.id)]
        data.Save_Settings()

    @staticmethod
    async def SendEvents(channel: discord.TextChannel, classroom_link: str):
        calendar = Calendar.Calendar(classroom_link)
        events = calendar.getClassOfTomorrow()

        embed = discord.Embed(
            title=f"Summary of tomorrow ({(datetime.utcnow() + timedelta(days=1)).strftime('%d/%m/%y')})",
            color=discord.Color.gold())
        embed.set_footer(text="Powered by iChronos Reloaded",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/ichronos.png")
        embed.set_author(name=classroom_link, url=calendar.link)
        if len(events) == 0:
            embed.description = "There is no event for tomorrow"
        else:
            embed.description = events[0].name
            for i in range(1, len(events)):
                embed.add_field(name=f"{events[i].name}", value=str(events[i]), inline=False)
        await channel.send(embed=embed)

    @tasks.loop(hours=24)
    async def SendEventsOfTomorrow(self):
        for guild in UpdateGrandtedGuild():
            try:
                data: dict = Server(guild).calendar
                for channel in data.items():
                    a = self.bot.get_channel(int(channel[0]))
                    for cal in channel[1]:
                        await self.SendEvents(a, cal)
            except FileNotFoundError as e:
                print(f"Unable to send events for '{guild}' , the file doesn't not exist",e)

    @cal.command(name="add")
    async def AddCalendar(self, context: commands.Context, class_link):
        data = Server(context.guild.id)
        s = str(context.channel.id)
        if s in data.calendar and class_link in data.calendar[s]:
            await Tools.SendError(context.channel, "Calendar already added")
            return None

        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title=f"Added {class_link} calendar for {context.channel} channel")

        if s not in data.calendar:
            data.calendar[s] = []

        data.calendar[s].append(class_link)
        data.Save_Settings()
        await Tools.AdminCommand(context, embed)
        await CalCog.SendEvents(context.channel, class_link)

    @cal.command(name="remove", aliases=["del,rm"])
    async def DelCalendar(self, context: commands.Context, class_link: str):
        data = Server(context.guild.id)

        s = str(context.channel.id)
        if s not in data.calendar or class_link not in data.calendar[s]:
            await Tools.SendError(context.channel, "Unknown calendar")
            return None

        data.calendar[s].remove(class_link)

        if not data.calendar[s]:
            data.calendar.pop(s)

        data.Save_Settings()

        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title=f"Removed {class_link} calendar from {context.channel} channel")

        await Tools.AdminCommand(context, embed)

    @cal.command(name="list")
    async def ListCalendar(self, context: commands.Context):
        data: dict = Server(context.guild.id).calendar
        embed = Embed.BasicEmbed(color=discord.Color.green())
        for calendar in data.items():
            embed.add_field(name=self.bot.get_channel(int(calendar[0])), value='\n'.join(calendar[1]))

        await context.channel.send(embed=embed)
