class English:
    changeLanguage = "The language is now set to **English**"
    unknownCommand = "Unknown command: I sent you the list of available commands list in a private message"
    commands = [
        "**List of the commands you can use with this bot:**",
        ["call ***@class***", "Start the attendance, *replace @class by the corresponding class*"],
        ["add ***@role1 @role2***", "Add privileges to one or more roles"],
        ["remove (or rm) ***@role1 @role2***", "Remove privileges from one or more roles"],
        ["admin language en|fr|de","Change the bot's language to one of the following languages : English, French or German"],
        ["list (or roles)", "Return roles with privileges"],
        ["admin reset", "Resets the bot"],
        ["admin prefix", "Changes the bot's prefix"],
        ["admin sys", "Enable/Disable the bot's system messages"],
        ["admin DeactivateMP", "Enable/Disable private messages"],
        ["For more information", "[Click here](https://github.com/Renaud-Dov/CheckStudents)"],
        ["settings", "Return the settings' values for this server"]
    ]
    NoStudents =  "⚠ **No student present** ⚠"
    EndCall = [
        "**Present students:**\n",
        "**Missing students:\n**",
        "\n ✅ **All students are present** ✅"
    ]
    FinishCall = " finished the attendance of"
    cancelCall = "⚠ **Canceled the attendance** ⚠"
    NoRightEnd = "**You do not have the rights to close the attendance!**"
    unknownEmoji = "**Unknown emote.\nStudents must click ✅ to notify themselves present.**"
    cantNotify = "You cannot notify yourself present"
    notTeacher =  "**You are not a teacher! You cannot start the call.**"
    NoPrivileges = "**You don't have privileges!** \n *Use the `admin list` command to see the admin roles*"
    zeroPrivileges = "**There is no role with privileges! To add more: .Check add @ role1 @ role2, etc ...**"
    removeAdmin =  "Admin removed"
    notAdmin = "is not admin"
    newAdmin = ["New Admin :","role already added","not a valid role"]
    rolenotValid = "Invalid role : For more information : `.Check help`"




class French:
    toto = 7


def getlang(_lang: str):
    if _lang == "en":
        return English
    if _lang == "fr":
        return French
