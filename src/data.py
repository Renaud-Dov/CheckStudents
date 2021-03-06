import json
import discord
import os


class Server:
    def __init__(self, guild_id: int):
        self.guild = guild_id

        with open('database/{}.json'.format(self.guild), 'r') as outfile:
            var = json.load(outfile)
        self.language: str = var["language"]
        self.prefix: str = var["prefix"]
        self.delay: int = var["delay"]
        self.mp: bool = var["mp"]
        self.sysMessages: bool = var["sysMessages"]
        self.showPresents: bool = var["showPresents"]
        self.admin: dict = var["admin"]
        self.teacher: dict = var["teacher"]
        self.calendar: dict = var["calendar"]

    def __toDict(self):
        return {"prefix": self.prefix, "language": self.language, "mp": self.mp,
                "sysMessages": self.sysMessages, "showPresents": self.showPresents, "delay": self.delay,
                "admin": self.admin, "teacher": self.teacher, "calendar": self.calendar}

    def Save_Settings(self):
        with open("database/{}.json".format(self.guild), "w") as outfile:
            json.dump(self.__toDict(), outfile)

    def returnLanguage(self, stat):
        with open('language/{}.json'.format(self.language)) as outfile:
            var = json.load(outfile)
        return var[stat]

    def Reset(self):
        self.language = "en"
        self.prefix = ".Check "
        self.delay = 10
        self.mp = True
        self.sysMessages = True
        self.showPresents = True
        self.admin = {"roles": [], "users": []}
        self.teacher = {"roles": [], "users": []}
        self.calendar = dict()


def Create_Guild(guild_id):
    with open("database/{}.json".format(guild_id), "x") as outfile:
        json.dump(
            {"prefix": ".Check ", "language": "en", "mp": True,
             "sysMessages": True, "showPresents": True, "delay": 10,
             "admin": {"roles": [], "users": []}, "teacher": {"roles": [], "users": []}, "calendar": {}}, outfile)


def Remove_Guild(guild_id):
    os.remove("database/{}.json".format(guild_id))


async def get_prefix(client, message: discord.Message):
    try:
        if isinstance(message.channel, discord.TextChannel):
            with open("database/{}.json".format(message.guild.id), "r") as outfile:
                var = json.load(outfile)
            return [".Check ", ".Check", var["prefix"]]
        else:
            return [".Check ", ".Check"]
    except AttributeError as e:
        print(message, e)
