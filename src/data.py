import json
import discord
import os


class Server:
    def __init__(self, guild_id: int):
        self.guild = guild_id
        if guild_id is None:
            raise ValueError("Guild ID is None")
        try:
            with open('database/{}.json'.format(self.guild), 'r') as outfile:
                var = json.load(outfile)
            self.delay: int = var["delay"]
            self.mp: bool = var["mp"]
            self.showPresents: bool = var["showPresents"]
            self.admin: dict = var["admin"]
            self.teacher: dict = var["teacher"]
        except FileNotFoundError:
            self.Reset()
            self.Save_Settings()

    def __toDict(self):
        return {"mp": self.mp, "showPresents": self.showPresents, "delay": self.delay,
                "admin": self.admin, "teacher": self.teacher}

    def Save_Settings(self):
        with open("database/{}.json".format(self.guild), "w") as outfile:
            json.dump(self.__toDict(), outfile)

    def Reset(self):
        self.delay = 10
        self.mp = True
        self.showPresents = True
        self.admin = {"roles": [], "users": []}
        self.teacher = {"roles": [], "users": []}

    @property
    def sum_admin(self):
        return len(self.admin["roles"]) + len(self.admin["users"])
    @property
    def sum_teacher(self):
        return len(self.teacher["roles"]) + len(self.teacher["users"])



def Remove_Guild(guild_id):
    os.remove("database/{}.json".format(guild_id))
