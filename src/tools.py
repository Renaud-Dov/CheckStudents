import discord
from discord.ext import commands
from src.data import *


class Tools:
    @staticmethod
    def convert(role: str):
        try:
            return int(role.replace(" ", "").lstrip("<@&").rstrip(">"))
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def got_the_role(role, user: discord.Member):
        """
        Check if a user got at least one role in author list
        """

        if isinstance(role, dict):
            if user.id in role["users"]:
                return True
            for i in role["roles"]:
                if i in [y.id for y in user.roles]:
                    return True
        elif isinstance(role, list):
            for i in role:
                if i in [y.id for y in user.roles]:
                    return True
        elif isinstance(role, discord.Role):
            return role in user.roles
        elif isinstance(role, int):
            return role in [y.id for y in user.roles]

    @staticmethod
    def name(member):
        """
        Return server nickname of a user, and if he doesn't have one, return his pseudo
        """
        if member.nick is not None:
            return member.nick
        else:
            return member.name

    @staticmethod
    async def SendError(channel, message: str, desc: str = None):
        embed = discord.Embed(color=discord.Color.red(), title=message)
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        # embed.add_field(name="Permission Denied",value=message)
        if desc is not None:
            embed.description = desc
        embed.set_thumbnail(url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/remove.png")
        await channel.send(embed=embed)

    @staticmethod
    async def AdminCommand(context, embed: discord.Embed, title=None):
        await context.channel.send(embed=embed)

        if Server(context.guild.id).sysMessages and context.guild.system_channel is not None \
                and context.guild.system_channel != context.channel:
            embed.add_field(name="Link to the action", value=f"[Link]({context.message.jump_url})")
            embed.add_field(name="Used by", value=context.message.author.mention)
            if title is not None:
                embed.title = title
            try:
                await context.guild.system_channel.send(embed=embed)

            except commands.CommandInvokeError:
                print(context.guild, context.guild.id, "raised commands.CommandInvokeError")
