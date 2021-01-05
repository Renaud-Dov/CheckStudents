# Version Changelog 
All notable changes to this project will be documented in this file.

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