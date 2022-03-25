import json
import discord
import os


class Server:
    def __init__(self, guild_id: int):
        self.guild = guild_id
        if guild_id is None:
            raise ValueError("Guild ID is None")
        with open('database/{}.json'.format(self.guild), 'r') as outfile:
            var = json.load(outfile)
        self.delay: int = var["delay"]
        self.mp: bool = var["mp"]
        self.sysMessages: bool = var["sysMessages"]
        self.showPresents: bool = var["showPresents"]
        self.admin: dict = var["admin"]
        self.teacher: dict = var["teacher"]

    def __toDict(self):
        return {"mp": self.mp, "sysMessages": self.sysMessages, "showPresents": self.showPresents, "delay": self.delay,
                "admin": self.admin, "teacher": self.teacher}

    def Save_Settings(self):
        with open("database/{}.json".format(self.guild), "w") as outfile:
            json.dump(self.__toDict(), outfile)

    def Reset(self):
        self.delay = 10
        self.mp = True
        self.sysMessages = True
        self.showPresents = True
        self.admin = {"roles": [], "users": []}
        self.teacher = {"roles": [], "users": []}


def Create_Guild(guild_id):
    with open("database/{}.json".format(guild_id), "x") as outfile:
        json.dump(
            {"mp": True, "sysMessages": True, "showPresents": True, "delay": 10, "admin": {"roles": [], "users": []},
             "teacher": {"roles": [], "users": []}}, outfile)


def Remove_Guild(guild_id):
    os.remove("database/{}.json".format(guild_id))
