import json
import glob

for file in glob.glob("./database/*json"):
    with open(file, 'r') as outfile:
        var = json.load(outfile)
    var["teacher"] = var["admin"]
    with open(file, 'w') as outfile:
        json.dump(var, outfile)
