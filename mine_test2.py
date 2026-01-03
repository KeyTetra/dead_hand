import random
import hashlib


from mnemonic import Mnemonic
from concurrent.futures import ThreadPoolExecutor

import colorama
import requests  # Import requests module

def generate_mc():
    mnemo = Mnemonic("english")
    print(type(mnemo.generate(256)))
    print(type("thkvg"))

generate_mc()