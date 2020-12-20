![Version](https://img.shields.io/badge/version-1.6-green)
![Github](https://img.shields.io/badge/license-GNU3-orange)
![Last commit](https://img.shields.io/github/last-commit/Renaud-Dov/CheckStudents?color=yellow&logo=Python&logoColor=yellow)

# CheckStudents
To add this bot to your Discord Server :
[![Click here](https://img.shields.io/badge/-Add%20the%20bot-blue?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=760157065997320192&permissions=8&scope=bot
)

>**Note : You need the corresponding privileges to add the bot on a server.**

## How it works ?



For make a call, a teacher (or any other user with an authorized role): `.Check call @class`

![startcall](img/startcall.png)

Emojis will appear below your message, the students belonging to the `@class` role would be able to click on the ✅ to notify their presence.
The teacher, or anyone with privileges, can end the call by clicking 🆗 or cancel with 🛑.

![cantnotify](img/cantnotify.png)

Note : Users can only notify their presence if they are part of the group (External students will not be counted)
Also, someone who does not have privileges cannot close the call.

![noright](img/noright.png)


Once the call is finished, the bot will return the list of present and missing students and send the list to the teacher in private message.

![finishcall](img/endcall.png)

The teacher who started the call will get a copy of the call in private message:

![CallSumarry](img/summary.png)

Every absent student will get an absence notification in private message, like this:

![absence](img/absence.png)
## Add/Remove Admin privileges to a role

>Only a user with privileges can add/remove roles.
* Add : `.Check add @role1 @role2,...` 
* Remove : `.Check remove @role1 @role2,...`
>Note: You can add / remove as many roles as you want at the same time.

Note that the admin rights will not be checked if no admin has been registered beforehand.

**To see the list of admins,** use command `.Check list` or `.Check roles` (same command)

## Change bot prefix
If you want to change bot prefix, use command `prefix` followed by the new prefix. Default prefix is "`.Check `"
>You must be an admin in order to execute this command
## Translation

You can also use the bot in different languages (French,English,German only for the moment)
Use `.Check language fr|en|de`. The language is applied to all the server.
If you want to add another language, please check english json prototype (`language/en.json`) and pull-request your translation!

## Reset the bot

To reset the bot, use command `reset`. Reset command will reset admin list, put default prefix, and set language to english.
>You must be an admin or the server owner in order to execute this command

## Activate/Deactivate bot system messages

If you have a system messages on your server and wants the bot to send a message when someone has changed bot settings, you can activate this functionality. This functionality is activated by default.

> Command : `sys or sysMessages`

## Data privacy

The bot communicates with the server every time you use it. We only keep IDs guilds, roles with privileges, and just during a call, guilds usernames and their users IDs.

We also analyse every discord reaction on every servers to see if it corresponds to a call message.
##### This repository use [Discord.py](https://github.com/Rapptz/discord.py) library from [Rapptz](https://github.com/Rapptz)
###### Icons made by [Freepik](http://www.freepik.com/) from [Flaticon](https://www.flaticon.com/)