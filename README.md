PyUrTRCon
=========

A small tool for Urban Terror (or any other similar Quake3-based games) server administrators written in Python that can execute RCon commands on remote servers.


Usage
-----
The tool is a Python 2.7.x script. Start it using the python interpreter.
	
	$ python pyurtrcon.py
	
Optionally, we can pass it the game-server address, port and the password.

	$ python pyurtrcon.py urtbd.com:27960 12345
	
The game-server information can also be set during a session using the `gameserver` and `password` commands (see below).

Once in a session, type `help` to get a list of available commands and their usages.

#### Common Commands

+ The `rcon` command sends RCon request to the server. Examples:

	> \>\> rcon g\_nextmap ut4\_turnpike
	
	> \>\> rcon cyclemap

+ The `history` command lists all previously executed commands during the current session.
+ The `gameserver` command sets the address and port number of the game-server.
+ The `password` command sets the RCon password for the game-server. 

#### Auto-complete
Press the `tab` button to auto-complete partially typed commands. It can also complete some RCon commands as well. You can extend the list of RCon commands the tool can auto-complete by editing the script. Add the commands you frequently use in this list:

	common_commands = ['exec', 'bigtext', 'map', 'cyclemap', 'g_nextmap', 'g_gametype']

Also, add servers you frequently manage in this list:
	
	common_addresses = []

License
-------
This software is released under the [GNU General Public License, version 2](http://opensource.org/licenses/gpl-2.0.php).