from datetime import date, datetime
from time import gmtime, strftime
from src.data import *
from src.tools import Tools
import asyncio
from io import BytesIO


class Check:
    def __init__(self, classroom: discord.Role, message: discord.Message, showAll: bool, delay: int):
        self.role = classroom
        self.message = message
        self.teacher = message.author
        self.showPresents = showAll
        self.listStudents = list()
        self.delay = delay

    async def AddStudents(self, reactions: list):
        for react in reactions:
            if str(react.emoji) == "✅":
                self.listStudents = [user for user in await react.users().flatten() if
                                     Tools.got_the_role(self.role, user)]
                break


class LateStudent:
    def __init__(self, teacher: discord.user, student: discord.User):
        self.teacher: discord.user = teacher
        self.student: discord.User = student

    async def SendLateMessage(self):
        await self.teacher.send(f"**{self.student.name}** {self.student.mention} arrived late")


class Calling:
    def __init__(self):
        self.callList = dict()

    def check(self, entry: str) -> bool:
        return entry in self.callList

    async def finishCall(self, client, classroom: Check):
        data = readGuild(classroom.message.guild.id)
        if not classroom.listStudents:
            embed = discord.Embed(color=discord.Colour.red(),
                                  title="No students present, please use 🛑 to cancel the call")
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            embed.set_thumbnail(url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/remove.png")

            await classroom.message.channel.send(embed=embed)
        else:
            nbStudents = len(classroom.role.members)
            presentsMessage, absents, listAbsents, listPresents = self.returnPresent(classroom.message.guild.id,
                                                                                     classroom.role.members,
                                                                                     classroom.listStudents)
            await classroom.message.channel.send(f"{len(listPresents)} students out of {nbStudents} are present")

            firstMsg = presentsMessage
            if (classroom.showPresents or data["showPresents"]) and presentsMessage:
                await classroom.message.channel.send(firstMsg)

            await classroom.message.channel.send(absents)

            delay = classroom.delay if classroom.delay > 0 and (nbStudents - len(listPresents)) > 0 else 0

            await self.SendList(classroom.message, classroom.role.name, [firstMsg, absents], delay, data["mp"])

            if data["mp"]:
                missingStudent = await self.Send_MP_absents(listAbsents, classroom.message, delay, classroom.teacher)
                if listAbsents and classroom.delay:
                    await classroom.message.channel.send(
                        f"The **{nbStudents - len(listPresents)}** absent have **{delay}** minutes to send me a direct message to report their late arrival")
                    await self.DelayForLateStudents(client, classroom.message.channel, missingStudent, delay)

    @staticmethod
    async def DelayForLateStudents(client, channel: discord.TextChannel, missing: dict, delay: int):

        def check(reaction, user):
            return str(reaction.emoji) == "⏰" and reaction.message.id in missing

        for msg, student in missing.items():
            try:
                reaction, user = await client.wait_for('reaction_add', timeout=delay * 60, check=check)
            except asyncio.TimeoutError:
                pass
            except Exception as e:
                print(e)
            else:
                await student.teacher.send(f"**{user.name}** {user.mention} arrived late")
                await reaction.message.delete()
                await user.send("I told the teacher you were late")
                del missing[msg]

        if missing.values():
            embed = discord.Embed(color=discord.Colour.red(),
                                  title=f"The {delay} minutes are elapsed: absents can no longer send a late ticket.")
            embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                             icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
            await channel.send(embed=embed)
            # await Calling.EndDelay(channel, delay)

    @staticmethod
    async def EndDelay(channel: discord.TextChannel, delay: int):
        embed = discord.Embed(color=discord.Colour.red(),
                              title=f"The {delay} minutes are elapsed: absents can no longer send a late ticket.")
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        await channel.send(embed=embed)

    async def StartCall(self, client: discord.client, context, args: tuple):
        """
        Start Attendance
        """
        if await self.Call(context, args):  # Attendance successfully started
            entry = f"{context.guild.id}-{context.message.id}"

            def check(reaction, user):
                return "{0.guild.id}-{0.id}".format(reaction.message) in self.callList \
                       and user == self.callList[entry].teacher and str(reaction.emoji) in ("🆗", "🛑")

            try:
                reaction, user = await client.wait_for('reaction_add', timeout=600, check=check)
            except asyncio.TimeoutError:  # timeout
                ClassData: Check = self.callList.pop(entry)
                await Tools.embedError(context.channel, "Attendance automatically closed.")

                await ClassData.AddStudents(context.message.reactions)
                await context.message.clear_reactions()
                await self.finishCall(client, ClassData)
            else:  #
                if str(reaction.emoji) == "🆗":
                    ClassData: Check = self.callList.pop(entry)
                    await context.channel.send(
                        f"{user.display_name} :{returnLanguage(readGuild(context.guild.id)['language'], 'FinishCall')} {ClassData.role.name}")
                    await ClassData.AddStudents(context.message.reactions)
                    await context.message.clear_reactions()
                    await self.finishCall(client, ClassData)
                else:  # 🛑 canceled attendance
                    await context.channel.send(
                        returnLanguage(readGuild(context.guild.id)["language"], "cancelCall"))
                    del self.callList[entry]
                    await context.message.clear_reactions()

    async def Call(self, context, args: tuple):
        classroom = context.message.role_mentions
        data = readGuild(context.guild.id)
        showAll = '-a' in args
        if len(classroom) != 1:
            await Tools.embedError(context.channel, "Please precise **one** role to call")
        elif Tools.got_the_role(data["teacher"], context.author):
            try:

                delay = data["delay"] if data["delay"] > 0 else 0
                if '-d' in args:
                    delay = int(args[args.index('-d') + 1])
                    if delay > 60 or delay < 0:
                        raise ValueError

                self.callList[f"{context.guild.id}-{context.message.id}"] = Check(classroom[0], context.message,
                                                                                  showAll, delay)
                message = returnLanguage(data["language"], "startcall")

                embed = discord.Embed(color=discord.Colour.green(), title=message[0], description=message[1])
                embed.set_author(name=Tools.name(context.message.author),
                                 icon_url=context.message.author.avatar_url)
                embed.add_field(name=f"**__{message[2]}__**", value=classroom[0].mention)
                embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"))
                # embed.add_field()
                embed.set_footer(text=message[3])

                await context.channel.send(embed=embed)
                await context.message.add_reaction("✅")  # on rajoute les réactions ✅ & 🆗
                await context.message.add_reaction("🆗")
                await context.message.add_reaction("🛑")

                return True
            except (ValueError, IndexError):
                await Tools.embedError(context.channel, "Invalid Args")
        else:
            await context.channel.send(
                "<@{}> : {}".format(context.author.id, returnLanguage(data["language"], "notTeacher")))

    async def Send_MP_absents(self, absents: list, message: discord.Message, delay: int, teacher: discord.User):
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
        missing = {}
        for member in absents:
            try:
                await member.send(embed=embed)
                if delay:
                    time = datetime.now()
                    message = await member.send(
                        "Click on the emote below to automatically send a late ticket message to the teacher.")
                    await message.add_reaction("⏰")
                    missing[message.id] = LateStudent(teacher, member)
            except discord.errors.Forbidden:
                await teacher.send(f"Unable to send a late ticket to {member.mention}")
        return missing

    async def SendList(self, message: discord.Message, className, students: list, delay: int, mp: bool):
        """
        Send the list of absents and presents students to the teacher
        """
        language_msg = returnLanguage(readGuild(message.guild.id)["language"], "class")
        embed = discord.Embed(color=discord.Colour.blue(), title=language_msg[1])
        embed.set_author(name="CheckStudents", url="https://github.com/Renaud-Dov/CheckStudents",
                         icon_url="https://raw.githubusercontent.com/Renaud-Dov/CheckStudents/master/img/logo.png")
        embed.add_field(name=language_msg[0], value=className)  # classroom
        embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"), inline=False)
        if delay > 0 and mp:
            embed.add_field(name="Time limit for late students", value=f"{delay} minutes")
        await message.author.send(embed=embed)

        for i in students:

            if len(i) > 2000:
                await Calling.file(i, message.author, className)
            else:
                await message.author.send(i)

    async def LateStudent(self, botUser: discord.ClientUser, user, message: discord.Message,
                          reaction: discord.Reaction):
        if str(reaction).strip(" ") == "⏰" and user != botUser and message.id in self.missing:
            if self.missing[message.id][0] in self.callList:
                data = self.callList[self.missing[message.id][0]]
                time_user = datetime.now() - self.missing[message.id][1]
                time_str = strftime(f"{'%H h' if time_user.seconds > 3600 else ''}%M minutes",
                                    gmtime(time_user.seconds))
                await data.teacher.send(f"**{user}** <@{user.id}> arrived {time_str} late")
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
    async def file(message, channel, name):
        as_bytes = map(str.encode, message)
        content = b"".join(as_bytes)
        await channel.send(file=discord.File(BytesIO(content), f"{name}.txt"))
