from datetime import date
from src.data import *
from src.tools import Tools
from src.log import DiscordLog


class Calling:
    def __init__(self):
        self.callList = dict()

    def check(self, entry: str) -> bool:
        return entry in self.callList

    async def finishCall(self, channel: discord.TextChannel, entry, guild_id, reaction: discord.Reaction):
        data = readGuild(guild_id)
        if not self.callList[entry]['listStudents']:
            embed = discord.Embed(color=discord.Colour.red(),
                                  title="No students presents, please use 🛑 to cancel the call")
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            embed.set_thumbnail(url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/remove.png")

            await channel.send(embed=embed)
        else:
            role_list = reaction.message.guild.get_role(self.callList[entry]['ClasseRoleID']).members
            nbStudents: int = len(role_list)
            presentsMessage, absents, listAbsents, listPresents = self.returnPresent(guild_id, role_list,
                                                                                     self.callList[entry][
                                                                                         'listStudents'])

            firstMsg = presentsMessage if (self.callList[entry]["showPresents"] or data[
                "showPresents"]) and presentsMessage \
                else f"{len(listPresents)} students out of {nbStudents} are present"
            await channel.send(firstMsg)

            await channel.send(absents)
            await self.SendList(reaction.message, entry, [firstMsg, absents])

            if data["mp"]:
                await self.Send_MP_absents(listAbsents, reaction.message)

    async def Call(self, context, classe, showAll: bool):
        class_role = Tools.convert(classe)
        data = readGuild(context.guild.id)
        if class_role is None:
            await Tools.embedError("This is not a role, but a specific user")
        else:
            if Tools.got_the_role(data["teacher"], context.author):
                self.callList[f"{context.guild.id}-{context.message.id}"] = {'ClasseRoleID': class_role,
                                                                             "teacher": context.message.author,
                                                                             "showPresents": showAll,
                                                                             'listStudents': []}
                message = returnLanguage(data["language"], "startcall")

                embed = discord.Embed(color=discord.Colour.green(), title=message[0], description=message[1])
                embed.set_author(name=Tools.name(context.message.author),
                                 icon_url=context.message.author.avatar_url)
                embed.add_field(name=f"**__{message[2]}__**", value=classe)
                embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"))
                embed.set_footer(text=message[3])

                await context.channel.send(embed=embed)
                await context.message.add_reaction("✅")  # on rajoute les réactions ✅ & 🆗
                await context.message.add_reaction("🆗")
                await context.message.add_reaction("🛑")
            else:
                await context.channel.send(
                    "<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "notTeacher")))

    async def CheckReaction(self, reaction: discord.Reaction, user, entry: str):
        reactionContent = str(reaction).strip(" ")
        if reactionContent == "✅":  # si l'utilisateur a coché présent
            if Tools.got_the_role(self.callList[entry]['ClasseRoleID'],
                                  user):  # si user a le role de la classe correspondante
                self.callList[entry]['listStudents'].append(user)  # on le rajoute à la liste d'appel
            elif not Tools.got_the_role(readGuild(reaction.message.guild.id)['botID'], user):
                await reaction.message.remove_reaction("✅", user)
                await Tools.embedError(user,
                                       "You do not have the right to click on ✅, you're not part of this class!")
                DiscordLog.Spam(user, "CheckReaction (not part of the class)")

        elif reactionContent in ("🆗", "🛑"):
            # Check if user got teacher privileges
            if Tools.got_the_role(readGuild(reaction.message.guild.id)["teacher"], user):

                if reactionContent == "🆗":
                    await reaction.message.channel.send(
                        "<@{}> :{} <@&{}>".format(user.id,
                                                  returnLanguage(readGuild(reaction.message.guild.id)["language"],
                                                                 "FinishCall"),
                                                  self.callList[entry]['ClasseRoleID']))
                    await self.finishCall(reaction.message.channel, entry, reaction.message.guild.id, reaction)
                else:
                    await reaction.message.channel.send(
                        returnLanguage(readGuild(reaction.message.guild.id)["language"], "cancelCall"))
                await reaction.message.clear_reactions()
                del self.callList[entry]

            elif not Tools.got_the_role(readGuild(reaction.message.guild.id)['botID'], user):  # pas le bot
                await reaction.message.remove_reaction(reactionContent, user)
                await Tools.embedError(user, "You can't stop the call, you do not have teacher privileges!")
                DiscordLog.Spam(user, f"CheckReaction : Trying to stop the call {reaction.message.jump_url}")
        else:  # autre emoji
            await reaction.message.remove_reaction(reactionContent, user)
            await Tools.embedError(user, "Do not use another emoji on this message while the call is not finished!")
            DiscordLog.Spam(user, f"CheckReaction : Trying to use another emoji during the call {reaction.message.jump_url}")

    def returnPresent(self, guild_id: int, role_list: list, class_list: list):
        """
        Return presents and absents students who have reacted on a message
        """
        class_list.sort(key=lambda x: Tools.name(x).lower())
        role_list.sort(key=lambda x: Tools.name(x).lower())
        messages = returnLanguage(readGuild(guild_id)["language"], "endcall")

        presents_msg = messages[0]
        absents_msg = str()
        students = []

        for member in class_list:
            if member.id not in students:
                presents_msg += f"• *{Tools.name(member)}* <@{member.id}>\n"  # [user.display_name,user.id]
                students.append(member.id)
                if role_list is not None:
                    role_list.remove(member)
        # if there is no more people
        if not role_list:
            absents_msg += messages[2]
        # if there is still people
        else:
            absents_msg = "\n" + messages[1]
            for member in role_list:
                absents_msg += f"• *{Tools.name(member)}* <@{member.id}>\n"
        return presents_msg, absents_msg, role_list, students

    async def Send_MP_absents(self, absents: list, message: discord.Message):  # guild, url: str, author, channel
        """
        Send a mp message to all absents
        """
        language_msg = returnLanguage(readGuild(message.guild.id)["language"], "sendabsents")

        embed = discord.Embed(color=discord.Colour.red(), title="Absence")
        embed.set_author(name=Tools.name(message.author), icon_url=message.author.avatar_url)
        embed.add_field(name=language_msg[0], value=Tools.name(message.author))
        embed.add_field(name=language_msg[1], value=message.guild)
        embed.add_field(name=language_msg[2], value=message.guild)
        embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"))
        embed.add_field(name=language_msg[3][0], value=f"[{language_msg[3][1]}]({message.jump_url})")
        for member in absents:
            await member.send(embed=embed)

    async def SendList(self, message: discord.Message, entry, students: list):
        """
        Send the list of absents and presents students to the teacher
        """
        language_msg = returnLanguage(readGuild(message.guild.id)["language"], "class")
        embed = discord.Embed(color=discord.Colour.blue(), title=language_msg[1])
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        embed.add_field(name=language_msg[0], value=message.guild.get_role(self.callList[entry]['ClasseRoleID']))
        embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"), inline=False)

        await message.author.send(embed=embed)

        await message.author.send(students[0])
        if students[1]:
            await message.author.send(students[1])
