# Version Changelog 
All notable changes to this project will be documented in this file.

<!-- ## Unreleased [0.7.0]-->
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