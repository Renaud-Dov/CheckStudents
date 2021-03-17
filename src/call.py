from datetime import date, datetime
from time import gmtime, strftime
from src.data import *
from src.tools import Tools
import asyncio
from io import BytesIO
from src import Embed


class Check:
    def __init__(self, classroom: discord.Role, message: discord.Message, showAll: bool, delay: int,
                 author: discord.Member):
        self.role = classroom
        self.message = message
        self.teacher = author
        self.showPresents = showAll
        self.listStudents = list()
        self.delay = delay

    async def AddStudents(self, context, messageID):
        msg = await context.fetch_message(messageID)
        for react in msg.reactions:
            if str(react.emoji) == "✅":
                self.listStudents = [user for user in await react.users().flatten() if
                                     Tools.got_the_role(self.role, user)]
                break


class LateStudent:
    def __init__(self, teacher: discord.user, student: discord.User, message=discord.Message):
        self.teacher: discord.user = teacher
        self.student: discord.User = student
        self.message = message
        self.time = datetime.now()

    async def SendLateMessage(self):
        await self.teacher.send(f"**{self.student.name}** {self.student.mention} arrived late")

    def DeltaTime(self):
        return datetime.now() - self.time


class Calling:
    def __init__(self):
        self.callList = dict()
        self.missing = dict()

    def check(self, entry: str) -> bool:
        return entry in self.callList

    async def finishCall(self, client: discord.Client, classroom: Check):
        data = Server(classroom.message.guild.id)
        if not classroom.listStudents:
            await classroom.message.channel.send(
                embed=Embed.BasicEmbed(color=discord.Colour.red(),
                                       title="No students present, please use 🛑 to cancel the call"))
        else:
            nb_students = len(classroom.role.members)
            presents_message, absents, list_absents, list_presents = self.returnPresent(classroom.message.guild.id,
                                                                                        classroom.role.members,
                                                                                        classroom.listStudents)
            await classroom.message.channel.send(f"{len(list_presents)} students out of {nb_students} are present")

            first_msg = presents_message
            if (classroom.showPresents or data.showPresents) and presents_message:
                await classroom.message.channel.send(first_msg)

            await classroom.message.channel.send(absents)

            delay = classroom.delay if classroom.delay > 0 and (nb_students - len(list_presents)) > 0 else 0

            await self.SendList(classroom.message.guild, classroom.teacher, classroom.role.name, [first_msg, absents],
                                delay, data.mp)

            if data.mp:
                missing_student = await self.Send_MP_absents(list_absents, classroom.message, delay, classroom.teacher)
                if list_absents and classroom.delay:
                    await classroom.message.channel.send(
                        f"The **{nb_students - len(list_presents)}** absent have **{delay}** minutes to send me a direct message to report their late arrival")
                    self.missing[classroom.message.id] = missing_student
                    await self.DelayForLateStudents(client.user, classroom.message.id, classroom.message.channel, delay)

    async def DelayForLateStudents(self, clientUser: discord.ClientUser, classroomMsg: int,
                                   channel: discord.TextChannel, delay: int):
        await asyncio.sleep(delay * 60)
        if self.missing[classroomMsg]:
            missing = self.missing.pop(classroomMsg)
            await Calling.EndDelay(channel, delay)
            for student in missing.values():
                await student.message.edit(
                    content=f"The {delay} minute(s) are elapsed: you can no longer send a late ticket.")
                await student.message.remove_reaction("⏰", clientUser)

    @staticmethod
    async def EndDelay(channel, delay):
        embed = Embed.BasicEmbed(color=discord.Colour.red(),
                              title=f"The {delay} minute(s) are elapsed: absents can no longer send a late ticket.")
        await channel.send(embed=embed)

    async def StartCall(self, client: discord.client, context, args: tuple):
        """
        Start Attendance
        """
        Botmessage: discord.Message = await self.Call(context, args)
        entry = f"{context.guild.id}-{Botmessage.id}"

        def check(reaction, user):
            a = "{0.guild.id}-{0.id}".format(reaction.message) in self.callList
            b = (user == self.callList[entry].teacher)
            return a and b and str(reaction.emoji) in ("🆗", "🛑")

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=600, check=check)
        except asyncio.TimeoutError:  # timeout
            ClassData: Check = self.callList.pop(entry)
            await Tools.SendError(context.channel, "Attendance automatically closed.")

            await ClassData.AddStudents(context, Botmessage.id)
            await self.finishCall(client, ClassData)
        else:
            if str(reaction.emoji) == "🆗":
                ClassData: Check = self.callList.pop(entry)
                await context.channel.send(
                    f"{user.display_name} :{Server(context.guild.id).returnLanguage('FinishCall')} {ClassData.role.name}")
                await ClassData.AddStudents(context, Botmessage.id)

                msg = await context.fetch_message(Botmessage.id)
                await msg.delete()

                await self.finishCall(client, ClassData)



            else:  # 🛑 canceled attendance
                await context.channel.send(
                    Server(context.guild.id).returnLanguage("cancelCall"))
                del self.callList[entry]



    async def Call(self, context, args: tuple):
        classroom = context.message.role_mentions
        data = Server(context.guild.id)
        showAll = '-a' in args
        try:
            if len(classroom) != 1:
                await Tools.SendError(context.channel, "Please precise **one** role to call")
                raise ValueError

            delay = data.delay if data.delay > 0 else 0
            if '-d' in args:
                delay = int(args[args.index('-d') + 1])
                if delay > 60 or delay < 0:
                    raise ValueError

            message = data.returnLanguage("startcall")

            embed = discord.Embed(color=discord.Colour.green(), title=message[0], description=message[1])
            embed.set_author(name=Tools.name(context.message.author),
                             icon_url=context.message.author.avatar_url)
            embed.add_field(name=f"**__{message[2]}__**", value=classroom[0].mention)
            embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"))
            # embed.add_field()
            embed.set_footer(text=message[3])

            Botmessage = await context.channel.send(embed=embed)
            await Botmessage.add_reaction("✅")  # on rajoute les réactions ✅ & 🆗
            await Botmessage.add_reaction("🆗")
            await Botmessage.add_reaction("🛑")

            self.callList[f"{context.guild.id}-{Botmessage.id}"] = Check(classroom[0], Botmessage,
                                                                         showAll, delay, context.author)

            return Botmessage
        except (ValueError, IndexError):
            await Tools.SendError(context.channel, "Invalid Args")

    async def Send_MP_absents(self, absents: list, message: discord.Message, delay: int, teacher: discord.Member):
        """
        Send a mp message to all absents
        """
        language_msg = Server(message.guild.id).returnLanguage("sendabsents")

        embed = discord.Embed(color=discord.Colour.red(), title="Absence")
        embed.set_author(name=Tools.name(teacher), icon_url=teacher.avatar_url)
        embed.add_field(name=language_msg[0], value=Tools.name(teacher))
        embed.add_field(name=language_msg[1], value=message.guild)
        embed.add_field(name=language_msg[2], value=message.channel)
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
                    missing[message.id] = LateStudent(teacher, member, message)
            except discord.errors.Forbidden:
                await teacher.send(f"Unable to send a late ticket to {member.mention}")
        return missing

    async def SendList(self, guild: discord.Guild, teacher: discord.Member, className, students: list, delay: int,
                       mp: bool):
        """
        Send the list of absents and presents students to the teacher
        """
        language_msg = Server(guild.id).returnLanguage("class")
        embed = Embed.BasicEmbed(color=discord.Colour.blue(), title=language_msg[1])
        embed.add_field(name=language_msg[0], value=className)  # classroom
        embed.add_field(name="Date", value=date.today().strftime("%d/%m/%Y"), inline=False)
        if delay > 0 and mp:
            embed.add_field(name="Time limit for late students", value=f"{delay} minutes")
        await teacher.send(embed=embed)

        for i in students:

            if len(i) > 2000:
                await Calling.file(i, teacher, className)
            else:
                await teacher.send(i)

    async def LateStudent(self, message: discord.Message):
        for attendance, students in self.missing.items():
            if message.id in students:
                student: LateStudent = self.missing[attendance].pop(message.id)
                latetime = student.DeltaTime()
                time_str = strftime(f"{'%H h' if latetime.seconds > 3600 else ''}%M minutes", gmtime(latetime.seconds))
                await student.teacher.send(f"**{student.student}** <@{student.student.id}> arrived {time_str} late")
                await student.student.send("I told your teacher you were late")
                await student.message.delete()
                break

    @staticmethod
    def returnPresent(guild_id: int, role_list: list, class_list: list):
        """
        Return presents and absents students who have reacted on a message
        """
        class_list.sort(key=lambda x: Tools.name(x).lower())
        role_list.sort(key=lambda x: Tools.name(x).lower())
        messages = Server(guild_id).returnLanguage("endcall")

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
