import json
import os


def returnLanguage(lg, stat):
    with open('language/{}.json'.format(lg)) as outfile:
        var = json.load(outfile)
    return var[stat]


def createGuild(guild_id, role_bot):
    with open("database/{}.json".format(guild_id), "x") as outfile:
        json.dump(
            {"botID": role_bot, "prefix": ".Check ", "mp": True, "language": "en", "sysMessages": True, "admin": [],"teacher":[]},
            outfile)


def removeGuild(guild_id):
    os.remove("database/{}.json".format(guild_id))


def editGuild(guild_id, data):
    with open("database/{}.json".format(guild_id), "w") as outfile:
        json.dump(data, outfile)


def readGuild(guild_id):
    with open('database/{}.json'.format(guild_id), 'r') as outfile:
        return json.load(outfile)


def get_prefix(client, message):
    with open("database/{}.json".format(message.guild.id), "r") as outfile:
        var = json.load(outfile)
    return ['.Check ', var["prefix"]]


def set_prefix(guild_id, prefix):
    var = readGuild(guild_id)
    var["prefix"] = prefix
    editGuild(guild_id, var)
