import json
import glob

for file in glob.glob("./database/*json"):
    if file != "epita.serv.json":
        with open(file, 'r') as outfile:
            var = json.load(outfile)
        for i in var["calendar"]:
            var["calendar"][i] = [var["calendar"][i]]

        with open(file, 'w') as outfile:
            json.dump(var, outfile)
