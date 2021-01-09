import json
import glob

for file in glob.glob("./database/*json"):
    with open(file, 'r') as outfile:
        var = json.load(outfile)
    var["admin"] = {"roles": var["admin"], "users": []}
    var["teacher"] = {"roles": var["teacher"], "users": []}
    # var["delay"] = 10
    with open(file, 'w') as outfile:
        json.dump(var, outfile)
