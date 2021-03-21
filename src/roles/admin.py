from src.data import *
from src import Embed
from src.roles.role import ListRoles, addRole, rmRole
from src.tools import Tools
from discord.ext import commands


def is_admin():
    async def predicate(context):
        data = Server(context.guild.id)
        if Tools.got_the_role(data.admin, context.author):
            return True
        await Tools.SendError(context.channel, data.returnLanguage("NoPrivileges"))
        return False

    return commands.check(predicate)


def setup(bot):
    bot.add_cog(Admin(bot))


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: discord.Client = bot

    @commands.group()
    async def admin(self, context):
        if context.invoked_subcommand is None:
            embed = Embed.AdminHelp()
            embed.add_field(name="admin help", value="Show this message")
            await context.channel.send(embed=embed)

    @admin.command(aliases=["commands,command"])
    async def help(self, context):
        await context.message.author.send("Here the list of subcommand you can use with *admin*",
                                          embed=Embed.AdminHelp())

    @admin.command(aliases=['Roles', 'list', 'admin', 'admins'])
    async def roles(self, context):
        await ListRoles(context, "admin")

    @admin.command()
    @is_admin()
    async def add(self, context):
        await addRole(context, "admin")

    @admin.command(aliases=['del', 'remove'])
    @is_admin()
    async def rm(self, context):
        await rmRole(context, "admin")

    @admin.command()
    @is_admin()
    async def prefix(self, context, arg):
        data = Server(context.guild.id)
        try:
            data.prefix = arg
            embed = Embed.BasicEmbed(color=discord.Colour.orange(),
                                     title=data.returnLanguage("newPrefix") + f"**{arg}**",
                                     description="You still can use \"`.Check `\"")
            await Tools.AdminCommand(context, embed)

            data.Save_Settings()
        except commands.errors.MissingRequiredArgument:
            await Tools.SendError(context.channel, "You did not specify a prefix")

    @admin.command(aliases=["lang"])
    @is_admin()
    async def language(self, context, lang=None):
        if lang not in ["fr", "en", "de"]:
            await Tools.SendError(context.channel,
                                  "Unknown language:\n**Languages :**\n• English: en\n• French: fr\n• German: de")
            return None

        data = Server(context.guild.id)
        data.language = lang
        embed = Embed.BasicEmbed(color=discord.Colour.orange(), title=data.returnLanguage("changeLanguage"))

        await Tools.AdminCommand(context, embed)
        data.Save_Settings()

    @admin.command()
    @is_admin()
    async def ShowPresents(self, context):
        """
            Activate/Deactivate Show presents students in call summary
        """
        data = Server(context.guild.id)

        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Call summary will only show absents students" if data.showPresents else "Call summary will show absents and presents students")

        data.showPresents = not data.showPresents

        data.Save_Settings()
        await Tools.AdminCommand(context, embed)

    @admin.command()
    @is_admin()
    async def Reset(self, context):
        data = Server(context.guild.id)
        if not Tools.got_the_role(data.admin, context.author) and context.message.author != context.guild.owner:
            await Tools.SendError(context.channel, data.returnLanguage("NoPrivileges"))
            return None

        data.Reset()
        data.Save_Settings()

        embed = Embed.BasicEmbed(color=discord.Colour.orange(),
                                 title="**__Factory reset:__**\nLanguage set to English\nAdmins and teachers list "
                                       "reseted\n**Prefix :** `.Check`\n**Show presents students, Sys Messages and "
                                       "Private Messages :** Activated\nDelay for for late students after a call : "
                                       "10 minutes")

        await Tools.AdminCommand(context, embed)

    @admin.command(aliases=["sys"])
    @is_admin()
    async def sysMessages(self, context):
        """
        Activate/Deactivate system message
        """
        data = Server(context.guild.id)

        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="System Messages are now disabled" if data.showPresents else "System Messages are now activated")

        data.sysMessages = not data.sysMessages
        data.Save_Settings()

        await Tools.AdminCommand(context, embed)

    @admin.command()
    @is_admin()
    async def DeactivateMP(self, context):
        data = Server(context.guild.id)

        embed = Embed.BasicEmbed(color=discord.Color.red(),
                                 title="Private messages are now disabled" if data.showPresents else "Private messages are now disabled")
        data.mp = not data.mp
        data.Save_Settings()

        await Tools.AdminCommand(context, embed)

    @admin.command()
    @is_admin()
    async def Delay(self, context, delay: str = None):
        data = Server(context.guild.id)

        try:
            delay = int(delay)
            if delay < 0 or delay > 60:
                raise ValueError
            data.delay = delay

            embed = Embed.BasicEmbed(color=discord.Color.red(), title=f"New delay : **{delay} minutes**")

            data.Save_Settings()
            await Tools.AdminCommand(context, embed)
        except ValueError:
            await Tools.SendError(context.channel,
                                  "Value must be between 0 and 60 minutes\nEnter 0 if you do not want to have any delay")
