from datetime import date
from src.data import *
from src.tools import Tools
import asyncio
from io import BytesIO


class Check:
    def __init__(self, classroom: int, teacher: discord.Member, showAll: bool, delay: int):
        self.classroom = classroom
        self.teacher = teacher
        self.showPresents = showAll
        self.listStudents = list()
        self.delay = delay

    async def AddStudent(self, student: discord.Member):
        self.listStudents.append(student)

    @staticmethod
    async def SplitMessages(msg: str):
        list


class Calling:
    def __init__(self):
        self.callList = dict()
        self.missing = dict()

    def check(self, entry: str) -> bool:
        return entry in self.callList

    async def finishCall(self, channel: discord.TextChannel, entry, guild_id, reaction: discord.Reaction):
        data = readGuild(guild_id)
        if not self.callList[entry].listStudents:
            embed = discord.Embed(color=discord.Colour.red(),
                                  title="No students presents, please use 🛑 to cancel the call")
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            embed.set_thumbnail(url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/remove.png")

            await channel.send(embed=embed)
        else:
            self.callList[entry].classroom.members
            nbStudents: int = len(self.callList[entry].classroom.members)
            presentsMessage, absents, listAbsents, listPresents = self.returnPresent(guild_id, self.callList[entry].classroom.members,
                                                                                     self.callList[entry].listStudents)
            await channel.send(f"{len(listPresents)} students out of {nbStudents} are present")

            firstMsg = presentsMessage
            if (self.callList[entry].showPresents or data["showPresents"]) and presentsMessage:
                await channel.send(firstMsg)

            await channel.send(absents)

            delay = self.callList[entry].delay if self.callList[entry].delay > 0 and (
                    nbStudents - len(listPresents)) > 0 else 0

            await self.SendList(reaction.message, entry, [firstMsg, absents], delay, data["mp"])

            if data["mp"]:
                await self.Send_MP_absents(listAbsents, entry, reaction.message, delay)
            if listAbsents and self.callList[entry].delay and data["mp"]:
                await channel.send(
                    f"The **{nbStudents - len(listPresents)}** absent have **{delay}** minutes to report their late arrival by private message with me")
                await asyncio.sleep(delay * 60)
                await self.EndDelay(channel, delay)
            del self.callList[entry]

    @staticmethod
    async def EndDelay(channel: discord.TextChannel, delay: int):
        embed = discord.Embed(color=discord.Colour.red(),
                              title=f"The {delay} minutes are elapsed: absents can no longer send a late ticket")
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        await channel.send(embed=embed)

    async def Call(self, context, args):
        classroom = context.message.role_mentions
        data = readGuild(context.guild.id)
        showAll = '-a' in args
        if len(classroom) != 1:
            await Tools.embedError(context.channel, "Please precise **one** role to call")
        else:
            if Tools.got_the_role(data["teacher"], context.author):
                self.callList[f"{context.guild.id}-{context.message.id}"] = Check(classroom[0], context.message.author,
                                                                                  showAll, data["delay"] if data["delay"] > 0 else 0)
                message = returnLanguage(data["language"], "startcall")

                embed = discord.Embed(color=discord.Colour.green(), title=message[0], description=message[1])
                embed.set_author(name=Tools.name(context.message.author),
                                 icon_url=context.message.author.avatar_url)
                embed.add_field(name=f"**__{message[2]}__**", value=classroom[0].mention)
                embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"))
                embed.set_footer(text=message[3])

                await context.channel.send(embed=embed)
                await context.message.add_reaction("✅")  # on rajoute les réactions ✅ & 🆗
                await context.message.add_reaction("🆗")
                await context.message.add_reaction("🛑")
            else:
                await context.channel.send(
                    "<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "notTeacher")))

    async def CheckReaction(self, botUser: discord.ClientUser, reaction: discord.Reaction, user, entry: str):
        reactionContent = str(reaction).strip(" ")
        if reactionContent == "✅":  # si l'utilisateur a coché présent
            if Tools.got_the_role(self.callList[entry].classroom,
                                  user):  # si user a le role de la classe correspondante
                await self.callList[entry].AddStudent(user)  # on le rajoute à la liste d'appel
            elif user != botUser:
                await reaction.message.remove_reaction("✅", user)
                await Tools.embedError(user,
                                       "You do not have the right to click on ✅, you're not part of this class!")

        elif reactionContent in ("🆗", "🛑"):
            # Check if user got teacher privileges
            if self.callList[entry].teacher == user:
                await reaction.message.clear_reactions()

                if reactionContent == "🆗":
                    await reaction.message.channel.send(
                        "<@{}> :{} {}".format(user.id,
                                                  returnLanguage(readGuild(reaction.message.guild.id)["language"],
                                                                 "FinishCall"),
                                                  self.callList[entry].classroom.name))
                    await self.finishCall(reaction.message.channel, entry, reaction.message.guild.id, reaction)
                else:
                    await reaction.message.channel.send(
                        returnLanguage(readGuild(reaction.message.guild.id)["language"], "cancelCall"))
                    del self.callList[entry]

            elif user != botUser:  # pas le bot
                await reaction.message.remove_reaction(reactionContent, user)
                await Tools.embedError(user, "You can't stop the call, you do not have teacher privileges!")
        else:  # other emoji
            await reaction.message.remove_reaction(reactionContent, user)
            await Tools.embedError(user, "Do not use another emoji on this message while the call is not finished!")

    async def Send_MP_absents(self, absents: list, entry: str, message: discord.Message, delay: int):
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

        if delay:
            embed.add_field(name="Time on receipt of the message to report late", value=f"{delay} minutes")
        for member in absents:
            await member.send(embed=embed)
            if delay:
                message = await member.send("Click to send a message to the teacher that you're late")
                await message.add_reaction("⏰")
                self.missing[message.id] = entry

    async def SendList(self, message: discord.Message, entry, students: list, delay: int, mp: bool):
        """
        Send the list of absents and presents students to the teacher
        """
        language_msg = returnLanguage(readGuild(message.guild.id)["language"], "class")
        embed = discord.Embed(color=discord.Colour.blue(), title=language_msg[1])
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        embed.add_field(name=language_msg[0], value=message.guild.get_role(self.callList[entry].classroom))
        embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"), inline=False)
        if delay > 0 and mp:
            embed.add_field(name="Deadline for late students", value=f"{delay} minutes")
        await message.author.send(embed=embed)

        for i in students:
            await message.author.send(i)
            # if len(i) > 2000:
            #     # await Calling.file(i, message.author)
            #     pass
            # else:
            #
            #     await Calling.file(i, message.author)

    async def LateStudent(self, botUser: discord.ClientUser, user, message: discord.Message,
                          reaction: discord.Reaction):
        if str(reaction).strip(" ") == "⏰" and user != botUser and message.id in self.missing:
            if self.missing[message.id] in self.callList:
                data = self.callList[self.missing[message.id]]
                await data.teacher.send(f"**{user}** <@{user.id}> arrived late")
                await message.delete()
                await user.send("I told the teacher you were late")

            else:
                await user.send("It's too late to notify your delay")
                await message.delete()

    @staticmethod
    def returnPresent(guild_id: int, role_list: list, class_list: list):
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
        # return [presents_msg[index: index + 2000] for index in range(0, len(presents_msg), 2000)], [
        #     absents_msg[index: index + 2000] for index in range(0, len(absents_msg), 2000)], role_list, students

    @staticmethod
    def splitText(message: str) -> list:
        pass

    @staticmethod
    async def file(message, channel):
        as_bytes = map(str.encode, message)
        content = b"\n".join(as_bytes)
        await channel.send(file=discord.File(BytesIO(content), "presents.txt"))
