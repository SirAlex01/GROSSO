#!/usr/bin/env python3
import requests
import os
import sys
import string
import random
import re
import json
import hashlib
from base64 import b64encode, b64decode

from Crypto.Util.number import getPrime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import inverse

from pwn import *

# ========================== CONFIG ==========================
PORT = 3000
SERVICE = "XXX"
BLACKLISTED_TEAMS = []
# ============================================================


def generate(length=16, alphabet=string.ascii_letters + string.digits):
    return "".join(random.choices(alphabet, k=length))


addr = sys.argv[1] if len(sys.argv) > 1 else "10.60.0.1"
team_id = addr.split(".")[2]

if int(team_id) in BLACKLISTED_TEAMS:
    exit()

FLAGID_URL = "http://10.10.0.1:8081/flagIds"
flag_ids = requests.get(FLAGID_URL, params={"service": SERVICE, "team": team_id}).json()
flag_ids = flag_ids[SERVICE][team_id]


def exploit():
    r = remote(addr, PORT)


for flag_id, flag_data in flag_ids.items():
    try:
        exploit(*flag_data.values())
    except KeyboardInterrupt:
        exit()
    except:
        pass
