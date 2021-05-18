# Version Changelog 
All notable changes to this project will be documented in this file.
## [0.9.2] - 2021-05-18
### Changed
* Changed language architecture system.

## [0.9.1] - 2021-03-21
### Added
* Extensions (calendar, admin, teacher) can be loaded or unloaded
  > Command : `load {module} | unload {module} | reload {module}`
  > 
  > Example : `.Check load src.roles.admin`
### Changed
* Call embed will show how many students got the role.

* You can now add as many calendars as you want for your channel.
> The remove calendar command now need the class_link argument
> 
> Example : `.Check cal remove INFOS2E1-1`

## [0.9.0] - 2021-03-18
### Added
* Added calendar (for Epita servers only)
  >The bot send calendar around 19H (UTC time)
  > 
  > Use `cal add {calendar}` using CHRONOS calendar label
  > 
  > `cal remove {calendar}`
  > 
  > `cal list`

### Changed
* Some files and functions have been moved to get a cleaner code.
### Fixed
For some servers using a high level of moderation, the bot was unable to finish the attendance because he was 
using some restricted permission. Now the bot will add the emojis on his message and delete it after the attendance.
## [0.8.1] - 2021-01-23
### Changed
* Attendance automatically close after 10 minutes if you forgot to close it.
* For performance reasons, the client will get users who clicked on ✅ when the attendance is closed.
## [0.8.0] - 2021-01-09
### Added
* Absents students got ten minutes (default delay) after call to send a late ticket with the bot.
  > Note that this only work if you activated private messages. (See admin DeactivateMP command)
* New command to change delay : `admin delay value`
  > Example : `.Check admin value 15` will set the delay to 15 minutes.
  > If you want to deactivate it : `admin value 0`

* Add `-a` option to force display of present student
  > Use `-a` after the class. Example : `.Check call @Class -a`
### Changed
* Only the teacher who started the call can close it.
* When a student try to stop the call, or doing something forbidden during the call, the bot warn in DM instead in text channel.

### Fixed
* Admins and Teachers subcommands doesn't respond.
* The bot displays the wrong number of present students in class

## [0.7.2] - 2021-01-05
### Added
* New command if you don't want the bot to send the list of present students : `admin showPresents`
  > In that case, the bot will send how many students are present.
### Changed
* Sort is now case-sensitive.
### Fixed
* Command for unknown emojis was not working.

## [0.7.1] - 2021-01-04
### Added
* Bot remind default prefix in Discord Activity
* Bot will receive both of `.Check ` default prefix (with and without a space)
  > Example : `.Check help` or `.Checkhelp`
  
### Changed
* List are now sorted in alphabetical order (by the nickname or pseudo if null).

## [0.7.0] - 2020-12-24
### Added
* Permissions are now split in two categories : Admins and Teachers.
  >Only teachers can start a call.
  > 
  >Only admin can change settings and roles privileges.
* Even if you changed bot prefix, you still can use the bot with default prefix.
### Changed
_Commands have changed, here the new commands list:_ 
* **Teacher command**
  * `teacher add @role`: Add a teacher permission to a role
  * `teacher rm @role`: Remove a teacher permission to a role
  * `teacher list`: List teacher list
* **Admin Command**
  * `admin add @role`: Add a admin permission to a role
  * `admin rm @role`: Remove a admin permission to a role
  * `admin list`: List admin list
  * `admin sys`: Activate/Deactivate system messages
  * `admin DeactivateMP`: Activate/Deactivate private messages
  * `admin prefix`: Change bot prefix
  * `admin language`: Set server language bot
  * `admin reset`: Reset server settings
  

## [0.6.1] - 2020-12-20
### Added
* `settings` command to get language, and private and system messages status values.
* Admins Activate/Deactivate private messages with `DeactivateMP` command.
### Changed
* Rewrite [README.md](README.md) help commands
* Factorisation of the main code and its variables
* Add comments to all functions


### Fixed
* When invited on a server without accepting permissions, the bot was not able to create a config json for the server.
    > Owner server will receive a message inviting him to re-add the bot accepting the permissions this time.
* When the list of the students is too long, the bot was not able to send the list
* Raised an error when the bot was trying to send a system message and didn't have the permissions.
* Few functions were not awaited
## [0.6.0] - 2020-12-20
### Added

* Owner server can reset without having admin role
* Added System Messages
* Activate/Deactivate System Messages
* Send a message when the bot join a server 
### Changed
* Update help messages
-----------------
