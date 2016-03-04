#!/usr/bin/env python

import os
import sys
import cmd
import socket
import re
import json
import urllib2
import base64


class Console(cmd.Cmd):
    magic = '\377\377\377\377'
    timeout = 5
    common_commands = ['exec', 'bigtext', 'map', 'cyclemap', 'g_nextmap', 'g_gametype']
    common_addresses = []
    server_host = '127.0.0.1'
    server_port = 27960
    rcon_password = ''

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = '>> '
        self.intro  = 'Welcome to PyUrTRCon. Type "help" or "?" for instructions.'

        try:
            import readline
        except:
            self.intro += '\n(!) "readline" isn\'t installed. Autocomplete unavailable!'

    def do_gameserver(self, args):
        """Set or display the gameserver address.\nSupply the address in host:port format to set it."""
        if args == '':
            print('Address of the gameserver is "{}:{}"'.format(self.server_host, self.server_port))
        else:
            self.server_host = args.split(':')[0]
            self.server_port = int(args.split(':')[1])

    def do_password(self, args):
        """Set or display the RCon password."""
        if args == '':
            print('RCon password is "{}"'.format(self.rcon_password))
        else:
            self.rcon_password = args

    def do_rcon(self, args):
        """Send RCon commands to UrT server."""
        try:
            socket_handle = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            socket_handle.connect((self.server_host, self.server_port))
            socket_handle.settimeout(self.timeout)
            socket_handle.send('{}rcon {} {}'.format(self.magic, self.rcon_password, args))
            (response, address) = socket_handle.recvfrom(1024)
            socket_handle.close()
            formatted_response = re.sub(r'\^.', '', response.split('\n')[1])
            if len(formatted_response):
                print(formatted_response)
        except Exception as e:
            print('Error! Details: {}'.format(e.message))

    def complete_rcon(self, primitive, *_):
        if primitive:
            return [ command for command in self.common_commands if command.startswith(primitive) ]
        else:
            return self.common_addresses

    def do_history(self, _):
        """Prints all the previous commands of this session."""
        for entry in self._hist:
            print(entry)

    def do_help(self, args):
        """'help' or '?' with no arguments will print all commands.\n'help <command>' or '? <command>' will print help on <command>."""
        cmd.Cmd.do_help(self, args)

    def do_exit(self, _):
        """Exits from the PyUrTRCon tool."""
        return -1

    def do_EOF(self, _):
        return -1

    def preloop(self):
        self._hist  = []
        self._locals  = {}
        self._globals = {}
        cmd.Cmd.preloop(self)

    def postloop(self):
        cmd.Cmd.postloop(self)

    def precmd(self, line):
        self._hist += [ line.strip() ]
        return line

    def postcmd(self, stop, line):
        return stop

    def emptyline(self):   
        pass

    def default(self, line):      
        print('Unrecognized command. Type "help" for instructions.')

    undoc_header = None

    def print_topics(self, header, cmds, cmdlen, maxcol):
        if header is not None:
            cmd.Cmd.print_topics(self, header, cmds, cmdlen, maxcol)


class GistAuth(object):
    gist_api = 'https://api.github.com/gists'

    def __init__(self, gist_id, enc_key):
        self.gist_id = gist_id
        self.enc_key = enc_key

    def _load_gist_content(self):
        gist = urllib2.urlopen('{}/{}'.format(self.gist_api, self.gist_id))
        gist_data = json.load(gist)
        return gist_data.get('files').get('RconCipherData').get('content')

    def _decrypt_password(self, rcon_cipher):
        try:
            from Crypto.Cipher import AES

            data = base64.b64decode(rcon_cipher)
            iv = data[:16]
            cipher = AES.new(self.enc_key, AES.MODE_CBC, iv)
            return (lambda x: x[:-ord(x[(len(x) - 1):])])(cipher.decrypt(data[16:]))

        except ImportError:
            print('(!) Install the PyCrypto library for GistAuth to work.')
            return ''

    def get_password(self):
        pw_cipher = self._load_gist_content()
        pw_raw = self._decrypt_password(pw_cipher)
        return pw_raw


def main():
    console = Console()
    if len(sys.argv) >= 2:
        console.server_host = sys.argv[1].split(':')[0] if (':' in sys.argv[1]) else sys.argv[1]
        console.server_port = int(sys.argv[1].split(':')[1]) if (':' in sys.argv[1]) else 27960

    ga_server = os.environ.get('PYURTRCON_SERVER')
    ga_gist_id = os.environ.get('PYURTRCON_GIST_ID')
    ga_enc_key = os.environ.get('PYURTRCON_ENC_KEY')

    if ga_server is not None and ga_gist_id is not None and ga_enc_key is not None:
        if ga_server == '{}:{}'.format(console.server_host, console.server_port):
            ga = GistAuth(ga_gist_id, ga_enc_key)
            console.rcon_password = ga.get_password()
            console.intro += '\n(+) Authenticated using GistAuth.'

    if len(sys.argv) >= 3 and console.rcon_password == '':
        console.rcon_password = sys.argv[2]
    console.cmdloop()


if __name__ == '__main__': main()
