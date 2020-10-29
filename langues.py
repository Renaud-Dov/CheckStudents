import json


def language(lg,stat):
    with open('language/{}.json'.format(lg)) as outfile:
        var=json.load(outfile)
    return var[stat]

print(language("fr","startCall"))