![Version](https://img.shields.io/github/v/tag/Renaud-Dov/CheckStudents?label=latest%20version)
![Github](https://img.shields.io/github/license/Renaud-Dov/CheckStudents)
![Last commit](https://img.shields.io/github/last-commit/Renaud-Dov/CheckStudents?color=yellow&logo=Python&logoColor=yellow)

# CheckStudents

## Installation

To add this bot to your Discord Server :
[![Click here](https://img.shields.io/badge/-Add%20the%20bot-blue?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/api/oauth2/authorize?client_id=790559693390872596&permissions=2048&scope=applications.commands%20bot)

**Please accept all permission, or the bot will not respond on your server. Please refer
to [this issue](#the-bot-doesnt-respond-to-any-command).**
> **Note : You need the corresponding privileges to add the bot on a server.**

### Read [CHANGELOG](CHANGELOG.md) here.

## How does it work ?

To start attendance, a teacher (or any other user with an authorised role): `/call @role`.

![image](https://user-images.githubusercontent.com/14821642/160217238-a2615018-30b5-4621-8337-80b54807046f.png)


Buttons will appear below your message, the students belonging to the `@class` role would be able to click on
the `I'm present` to notify their presence. The teacher, or anyone with privileges, can end the call by clicking
on `Finish attendance` or cancel with `Cancel attendance`.

![image](https://user-images.githubusercontent.com/14821642/160217288-46ea127e-2b27-487f-897f-61afd807331a.png)

Note : Users can only notify their presence if they are part of the group (External students of a class will not be
counted)
Also, only the teacher who started the call can close it.

![image](https://user-images.githubusercontent.com/14821642/160124714-45836521-c371-4ce8-9524-c170f12dadc2.png)

Once the call is finished, the bot will return the list of present and missing students and send the list to the teacher
in private message.

The teacher who started the call will get a copy of the call in private message:

![image](https://user-images.githubusercontent.com/14821642/160124803-7714fa1b-68e3-46d7-ab7e-2c9e29dde285.png)

Every absent student will get an absence notification in private message, like this:

![image](https://user-images.githubusercontent.com/14821642/160124860-19b5f0da-5c90-4e20-a4f6-d609bb0ba5d1.png)


### Access to commands
> Since 1.1.0, CheckStudents use directly Discord Permission

In Server Settings > Integtations > Bots and Apps > CheckStudents
<img width="690" alt="image" src="https://user-images.githubusercontent.com/14821642/187078389-c092b819-c667-482e-a75c-05efcf76a94a.png">

##### From there you can directly set permissions to users and roles for each command
<img width="691" alt="image" src="https://user-images.githubusercontent.com/14821642/187078642-d8616d5b-3892-4a94-9aa4-3ddd32d5b971.png">



### Panel

In the panel control, you can read actual settings of the bot in the server.
<img width="490" alt="image" src="https://user-images.githubusercontent.com/14821642/160217389-5fa35577-5e3b-4578-abf7-01674c4f5d2c.png">


Let's see the settings of the bot in the server :

#### Activate/Deactivate bot private messages

When a student is marked absent, he will receive a ticket in private message to notify him, and the possibility to
inform the teacher when he's back.
> This functionality is activated by default.

#### Choose the delay for late students

Late students got 10 minutes by default to click on a DM message to inform their teacher.

### Activate/Deactivate the sending of the list of students present

Use this command if you do not want the bot to send the list of students present, and get a shorter list of students.
> This functionality is activated by default.

### Reset the bot

Reset command will reset admin and teacher list, set language to English, and reset other
settings by their default values.


## Common Errors

### The bot doesn't respond to any command

> If the bot doesn't respond to any command, it might be because you did not accept all permission. In that case, remove the bot from the server, and invite him again.

### Any other issue

> Please read [CHANGELOG](CHANGELOG.md) or create an issue.

##### This repository use [Discord.py](https://github.com/Rapptz/discord.py) library from [Rapptz](https://github.com/Rapptz)

###### Icons made by [Freepik](http://www.freepik.com/) from [Flaticon](https://www.flaticon.com/)
