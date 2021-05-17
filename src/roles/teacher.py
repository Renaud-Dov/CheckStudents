from discord.ext import commands

from src import Embed
from src.roles.admin import is_admin
from src.data import Server
from src.roles.role import ListRoles, addRole, rmRole
from src.tools import Tools


def is_teacher():
    async def predicate(context):
        data = Server(context.guild.id)
        if Tools.got_the_role(data.teacher, context.author):
            return True
        await Tools.SendError(context.channel, data.GetLanguage().NoPrivileges)
        return False

    return commands.check(predicate)


def setup(bot):
    bot.add_cog(Teacher(bot))


class Teacher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def teacher(self, context):
        if context.invoked_subcommand is None:
            embed = Embed.TeacherHelp()
            embed.add_field(name="teacher help", value="Show this message")
            await context.channel.send(embed=embed)

    @teacher.command(aliases=['Roles', 'list', 'admin', 'admins'])
    async def roles(self, context):
        await ListRoles(context, "teacher")

    @teacher.command(aliases=["commands,command"])
    async def help(self, context):
        await context.message.author.send("Here the list of subcommand you can use with *teacher*",
                                          embed=Embed.TeacherHelp())

    @teacher.command()
    @is_admin()
    async def add(self, context):
        await addRole(context, "teacher")

    @teacher.command(aliases=['del', 'remove'])
    @is_admin()
    async def rm(self, context):
        await rmRole(context, "teacher")
