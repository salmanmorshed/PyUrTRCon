#!/usr/bin/env python

import os
import hashlib
import random
import base64
import urllib2
import json
from Crypto.Cipher import AES
from Crypto import Random
from pyurtrcon import rcon, GistAuth


RCON_LEN = 5


def create_password(server_address):
    rand_num = random.randint(10000, 99999)
    data = '{}+{}'.format(rand_num, server_address)
    hashed_data = hashlib.sha1(data).hexdigest()
    start_index = random.randint(1, len(hashed_data) - RCON_LEN) - 1
    end_index = start_index + RCON_LEN
    return hashed_data[start_index:end_index]


def set_new_rcon(server_address, server_port, password, new_password):
    return rcon(server_address, int(server_port), password, ' rconpassword {}'.format(new_password))


def encrypt_password(enc_key, raw_password):
    padded = (lambda x: x + (16 - len(x) % 16) * chr(16 - len(x) % 16))(raw_password)
    iv = Random.new().read(16)
    cipher = AES.new(enc_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(padded))


def update_gist(gist_id, access_token, gist_content):
    url = 'https://api.github.com/gists/{}'.format(gist_id)
    data = json.dumps({'files': {'RconCipherData': {'content': gist_content}}})
    headers = {'Authorization': 'token {}'.format(access_token)}
    request = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(request)
    return response.readlines()


def main():
    ga_server = os.environ.get('PYURTRCON_SERVER')
    ga_gist_id = os.environ.get('PYURTRCON_GIST_ID')
    ga_enc_key = os.environ.get('PYURTRCON_ENC_KEY')
    access_token = os.environ.get('PYURTRCON_GHTOKEN')

    if ga_server is not None and ga_gist_id is not None and ga_enc_key is not None:
        old_password = GistAuth(ga_gist_id, ga_enc_key).get_password()
        print('[1/4] Retrieving old password: {}'.format(old_password))
        new_password = create_password(ga_server)
        print('[2/4] Creating new password: {}'.format(new_password))

        host, port = ga_server.split(':')
        print('[3/4] Setting new password to server: {}:{}'.format(host, port))
        res = set_new_rcon(host, port, old_password, new_password)
        if res: print(res)

        password_cipher = encrypt_password(ga_enc_key, new_password)
        print('[4/4] Updating Gist with new cipher: {}'.format(password_cipher))
        update_gist(ga_gist_id, access_token, password_cipher)
        print('Done!')


if __name__ == '__main__': main()
