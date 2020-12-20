import json, os


def returnLanguage(lg, stat):
    with open('language/{}.json'.format(lg)) as outfile:
        var = json.load(outfile)
    return var[stat]


def createGuild(guildID, rolebot):
    with open("database/{}.json".format(guildID), "x") as outfile:
        json.dump({"botID": rolebot,"prefix":".Check ","mp":True, "language": "en","sysMessages":True, "admin": []}, outfile)


def removeGuild(guildID):
    os.remove("database/{}.json".format(guildID))


def editGuild(guildID, data):
    with open("database/{}.json".format(guildID), "w") as outfile:
        json.dump(data, outfile)


def readGuild(guild):
    with open('database/{}.json'.format(guild), 'r') as outfile:
        return json.load(outfile)

def get_prefix(client,message):
    with open("database/{}.json".format(message.guild.id),"r") as outfile:
        var = json.load(outfile)
    return var["prefix"]

def set_prefix(guildID,prefix):
    var =readGuild(guildID)
    var["prefix"]=prefix
    editGuild(guildID,var)

#{"760808606672093184":".Check "}