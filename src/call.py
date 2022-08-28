from datetime import datetime
from typing import List, Dict, Optional

from discord import Member, Message

from src.data import *
from src.tools import Tools

from src import Embed


class Check:
    def __init__(self, interaction: discord.Interaction, role: discord.Role, delay: int):
        self.interaction = interaction
        self.role = role
        self.teacher = interaction.user
        self.students: List[Member] = list()
        self.delay = delay


class Calling:
    def __init__(self, client: discord.client):
        self.client = client
        self.calls: Dict[int, Check] = dict()

    async def finish(self, check: Check, interaction: discord.Interaction):
        data = Server(check.interaction.guild_id)
        # if not check.students:
        #     # await check.interaction.response.send_message(embed=Embed.BasicEmbed(color=discord.Colour.red(),
        #     #                                                             title="No students present."))
        #     return

        presents_message, absents_message, absents, presents = self.ProcessStudents(check.role.members,
                                                                                    check.students)
        nb_students = len(check.role.members)
        nb_presents = len(presents)
        nb_absents = len(absents)
        try:
            await interaction.response.defer()
        except:
            pass

        await check.interaction.followup.send(content=f"{nb_presents} students out of {nb_students} are present")

        if data.showPresents and presents_message:
            await check.interaction.followup.send(content=presents_message)

        await check.interaction.followup.send(content=absents_message)

        delay = check.delay if check.delay > 0 and nb_absents > 0 else 0

        await self.Send_Teacher(check, presents_message, absents_message, nb_presents, nb_absents,
                                nb_students, delay, data.mp)

        if data.mp:
            await self.Send_Absents(check, absents, delay)

    # async def DelayForLateStudents(self, classroomMsg: int,
    #                                channel: discord.TextChannel, delay: int):
    #     await asyncio.sleep(delay * 60)
    #     if self.missing[classroomMsg]:
    #         missing = self.missing.pop(classroomMsg)
    #         await channel.send(embed=Embed.BasicEmbed(
    #             title=f"The {delay} minute(s) are elapsed: absents can no longer send a late ticket.",
    #             color=discord.Color.red()))
    #         for student in missing.values():
    #             await student.message.edit(
    #                 content=f"The {delay} minute(s) are elapsed: you can no longer send a late ticket.")
    #             await student.message.remove_reaction("⏰", self.client)

    async def StartCall(self, interaction: discord.Interaction, role: discord.Role, delay: int = 10):
        """
        Start Attendance
        """

        embed = discord.Embed(color=discord.Colour.green(), title="Attendance")
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
        embed.add_field(name="**__Class called:__**", value=role.mention)
        embed.add_field(name="Date", value=f"<t:{int(datetime.timestamp(datetime.now()))}:R>")
        embed.add_field(name="Number of students in this class", value=str(len(role.members)))
        # embed.add_field()
        embed.set_footer(text="Need help ? Use the help command")

        check = Check(interaction, role, delay)
        self.calls[interaction.id] = check
        view = ButtonView(interaction, check, self)
        await interaction.response.send_message(embed=embed, view=view)

    @staticmethod
    async def Send_Absents(check: Check, absents: list, delay: int):
        """
        Send a mp message to all absents
        """

        embed = discord.Embed(color=discord.Colour.red(), title="Absence")
        embed.set_author(name=check.teacher.display_name, icon_url=check.teacher.avatar.url)
        embed.add_field(name="**By:**", value=check.teacher.display_name)
        embed.add_field(name="**Server:**", value=check.interaction.guild)
        embed.add_field(name="**Channel:**", value=check.interaction.channel)
        embed.add_field(name="Date", value=f"<t:{int(datetime.timestamp(datetime.now()))}:R>")
        for member in absents:
            try:
                await member.send(embed=embed)
                if delay:
                    view = LateStudentsView(check.teacher, delay)
                    message = await member.send(
                        "Click on the emote below to automatically send a late ticket message to the teacher.",
                        view=view)
                    view.message = message

            except discord.errors.Forbidden:
                await check.teacher.send(f"Unable to send a late ticket to {member.mention}")
            except discord.errors.HTTPException:
                await check.teacher.send(f"Unable to send a late ticket to {member.mention}")

    async def Send_Teacher(self, check: Check, present_message: str, absents_message: str, nb_presents, nb_absents,
                           nb_students, delay: int, mp: bool):
        """
        Send the list of absents and presents students to the teacher
        """

        embed = Embed.BasicEmbed(color=discord.Colour.blue(), title="**__Attendance summary__**")
        embed.add_field(name="**Class:**", value=check.role.name)  # classroom
        embed.add_field(name="Date", value=f"<t:{int(datetime.timestamp(datetime.now()))}:R>")
        embed.add_field(name="Number of students in the class", value=nb_students)
        embed.add_field(name="Presents ✅ ", value=nb_presents)
        embed.add_field(name="Absents ⚠", value=nb_absents)

        if delay > 0 and mp:
            embed.add_field(name="Time limit for late students", value=f"{delay / 60} minutes", inline=False)
        await check.teacher.send(embed=embed)
        await check.teacher.send(present_message)
        await check.teacher.send(absents_message)

    @staticmethod
    def ProcessStudents(role_list: List[Member], class_list: List[Member]):
        """
        Return presents and absents students who have reacted on a message
        """
        class_list.sort(key=lambda x: x.display_name.lower())
        role_list.sort(key=lambda x: x.display_name.lower())

        presents_msg = "**Present students:**\n"
        absents_msg = str()
        students = []

        for member in class_list:
            if member.id not in students:
                presents_msg += f"• *{member.display_name}* {member.mention}\n"  # [user.display_name,user.id]
                students.append(member.id)
                if role_list is not None:
                    role_list.remove(member)
        # if there is no more people
        if not role_list:
            absents_msg += "\n ✅ **All students are present** ✅"
        # if there is still people
        else:
            absents_msg = "\n" + "**Missing students:\n**"
            for member in role_list:
                absents_msg += f"• *{member.display_name}* {member.mention}\n"
        return presents_msg, absents_msg, role_list, students
        # return [presents_msg[index: index + 2000] for index in range(0, len(presents_msg), 2000)], [
        #     absents_msg[index: index + 2000] for index in range(0, len(absents_msg), 2000)], role_list, students

    async def cancel(self, check: Check, interaction: discord.Interaction):
        del self.calls[check.interaction.id]
        await interaction.channel.send(content="⚠ **Canceled the attendance** ⚠")


class ButtonView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, check: Check, calling: Calling):
        super().__init__(timeout=600)
        self.check = check
        self.interaction = interaction
        self.calling = calling

    @discord.ui.button(label="I'm present", style=discord.ButtonStyle.blurple, emoji="👋")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not Tools.has_permission(self.check.role, interaction.user):
            await interaction.response.send_message("You are not in the class", ephemeral=True)
        else:
            # if student already present
            if interaction.user in self.check.students:
                await interaction.response.send_message("You are already present", ephemeral=True)
            else:
                self.check.students.append(interaction.user)
                await interaction.response.send_message("You are noted present.", ephemeral=True)

    @discord.ui.button(label='Finish attendance', style=discord.ButtonStyle.green, emoji="✅")
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.check.teacher:
            await interaction.response.send_message("You are not the teacher", ephemeral=True)
        else:
            await self.calling.finish(self.check, interaction)
            self.stop()
            await self.check.interaction.edit_original_response(view=None)

    @discord.ui.button(label='Cancel attendance', style=discord.ButtonStyle.red, emoji="🛑")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.check.teacher:
            await interaction.response.send_message("You are not the teacher", ephemeral=True)
        else:
            await self.calling.cancel(self.check, interaction)
            self.stop()
            await self.check.interaction.edit_original_response(view=None)

    async def on_timeout(self):
        await self.calling.cancel(self.check, self.interaction)
        self.clear_items()
        await self.check.interaction.edit_original_response(view=None)


class LateStudentsView(discord.ui.View):
    def __init__(self, teacher: discord.Member, timeout: int):
        super().__init__(timeout=timeout)
        self.timestamp = datetime.now()
        self.teacher = teacher
        self.message: Optional[Message] = None

    @discord.ui.button(label="I'm present", style=discord.ButtonStyle.blurple, emoji="⏰")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        new_time = datetime.now()
        delta = (new_time - self.timestamp).seconds // 60
        await self.teacher.send(f"{interaction.user.mention} was {delta} minute(s) late.")

        self.stop()
        await self.message.edit(view=None)
        await interaction.response.send_message("You are noted late.", ephemeral=True)

    async def on_timeout(self):
        self.stop()
        await self.message.edit(view=None, content=f"The {self.timeout} minute(s) are elapsed:"
                                                   f" you can no longer send a late ticket.")
