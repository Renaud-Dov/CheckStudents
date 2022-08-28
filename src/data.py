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
        except FileNotFoundError:
            self.Reset()
            self.Save_Settings()

    def __toDict(self):
        return {"mp": self.mp, "showPresents": self.showPresents, "delay": self.delay}

    def Save_Settings(self):
        with open("database/{}.json".format(self.guild), "w") as outfile:
            json.dump(self.__toDict(), outfile)

    def Reset(self):
        self.delay = 10
        self.mp = True
        self.showPresents = True



def Remove_Guild(guild_id):
    os.remove("database/{}.json".format(guild_id))
