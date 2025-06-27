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

# ========================== CONFIG ==========================
PORT = 5555
SERVICE = 'CC-Manager'
EXCLUDED_IDS= []
USER_AGENT = None
# USER_AGENT = 'CHECKER'
# ============================================================

def generate(length=32):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


addr = sys.argv[1]
team_id = addr.split(".")[2]

if int(team_id) in EXCLUDED_IDS:
    print(f"Team ID {team_id} is excluded from the challenge.", flush=True)
    sys.exit(0)

# URL setup
URL = f'http://{addr}:{PORT}'
FLAGID_URL = f'http://10.10.0.1:8081/flagIds?service={SERVICE}&team={team_id}'

response = requests.get(FLAGID_URL)
flag_ids = json.loads(response.text)[SERVICE][team_id]


for key, info in flag_ids.items():

    username = info['username']

    s = requests.Session()
    if USER_AGENT:
        s.headers.update({'User-Agent': USER_AGENT})

    usr = generate(10)
    psw = generate(10)

    #REMOVE NEXT LINES
    r = s.post(URL + '/register', data={
        'username': usr,
        'password': psw
    })

    print(r.text, flush=True)
