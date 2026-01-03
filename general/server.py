import redis
from rq import Queue

import paho.mqtt.client as mqtt
import time
import os
import random
import json
import validators
import srt
import yt_dlp
import asyncio
import string
from telegram import Bot
import subprocess
from dotenv import load_dotenv
from datetime import datetime
import aiohttp
import hashlib
import asyncio
from bip32utils import BIP32Key
from mnemonic import Mnemonic
import colorama
from termcolor import colored

load_dotenv()
r = redis.Redis()
q = Queue(connection=r)


def generate_mc():
    mnemo = Mnemonic("english")

    return mnemo.generate(256)

def generate_BTCereum_address(words):
    seed = hashlib.pbkdf2_hmac('sha512', words.encode('utf-8'), "mnemonic", 2048)
    master_key = BIP32Key.fromEntropy(seed)
    btc_address = master_key.Address()
    return btc_address

async def check_balance_BTCereum(session, address):
    url = f"https://blockchain.info/rawaddr/{address}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            if 'final_balance' in data:
                balance = data['final_balance'] / 100000000  # Convert from satoshis to BTC
                return balance
    return "0"

async def process_address(session, words, live_counter_list, dead_counter_list, balanced_addresses):
    words = words
    for wg in words:
        BTC_address = generate_BTCereum_address(wg)
        balance = await check_balance_BTCereum(session, BTC_address)

        if balance is not None:
            if balance != "0":
                live_counter_list[0] += 1
                if balance > 0.000000:
                    balanced_addresses.append(f'{BTC_address} |{words} | BALANCE: {balance:.6f} BTC')
                print(colored(f'TOTAL LIVE: {live_counter_list[0]} | MNEMONIC: {words} | BALANCE: {balance:.6f} BTC | ADDRESS: {BTC_address}', 'green'))
            else:
                dead_counter_list[0] += 1
                print(colored(f'TOTAL DEAD: {dead_counter_list[0]} | MNEMONIC: {words} | BALANCE: 0 [DEAD] | ADDRESS: {BTC_address}', 'red'))

async def mine_loop():

    num_threads = 5  # Adjust as needed
    live_counter_list = [0]  # Using a list to make it mutable
    dead_counter_list = [0]  # Using a list to make it mutable
    balanced_addresses = []
    loop_while = True
    async with aiohttp.ClientSession() as session:
        while loop_while:
            tasks = [process_address(session, live_counter_list, dead_counter_list, balanced_addresses) for _ in range(num_threads)]
            await asyncio.gather(*tasks)

            # Check for balanced addresses and save them to a file
            if len(balanced_addresses) > 0:
                filename = f'data_{random.randint(1, 1000000)}.txt'
                with open(filename, 'w') as file:
                    file.write('\n'.join(balanced_addresses))
                print(colored(f'{len(balanced_addresses)} Balanced addresses saved to {filename}', 'yellow'))
                balanced_addresses = []  # Clear the list after saving
                loop_while = False


def srt_to_plain_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        subtitle_generator = srt.parse(f)
        transcript = ""
        for subtitle in subtitle_generator:
            # Add the content to the transcript, preserving internal line breaks
            transcript += subtitle.content + "\n\n"
    return remove_punctuation(str(transcript))

async def get_missing_messages(bot_token):
    bot = Bot(token=bot_token)
    updates = await bot.get_updates()

    if updates:
        print(f"Found {len(updates)} missing messages.")
        for update in updates:
            # Process your message here (e.g., store in DB, react)
            print(f"Processing message ID: {update.message.message_id} from {update.message.chat_id}")
            # print(update.message.text)

        # Acknowledge all retrieved updates by setting the offset
        last_update_id = updates[-1].update_id
        # By calling get_updates again with an offset+1, we tell Telegram to stop sending these
        await bot.get_updates(offset=last_update_id + 1)
        print("Acknowledged all retrieved messages.")
    else:
        print("No missing messages found.")


def switch_wifi_network(ssid, psk, interface='wlan0'):
    """
    Switches the Raspberry Pi to a new WiFi network.

    Args:
        ssid (str): The network SSID (name).
        psk (str): The network password (passphrase).
        interface (str): The wireless interface (default is 'wlan0').
    """
    print(f"Attempting to connect to network: {ssid}")

    # 1. Generate the network configuration string for wpa_supplicant
    # Add quotes around SSID and PSK to handle special characters or spaces
    config_line = f'network={{ ssid="{ssid}" psk="{psk}" }}'

    # 2. Add the new network configuration using wpa_cli
    # This command adds a new network entry and returns its ID
    add_cmd = f'sudo wpa_cli -i {interface} add_network'
    try:
        network_id_output = subprocess.check_output(add_cmd.split(), encoding='utf-8').strip()
        if not network_id_output.isdigit():
            print(f"Failed to add network, wpa_cli output: {network_id_output}")
            return
        network_id = int(network_id_output)
    except subprocess.CalledProcessError as e:
        print(f"Error adding network: {e}")
        return

    # 3. Set the SSID and PSK for the new network ID
    subprocess.run(['sudo', 'wpa_cli', '-i', interface, 'set_network', str(network_id), 'ssid', f'"{ssid}"'],
                   check=True)
    subprocess.run(['sudo', 'wpa_cli', '-i', interface, 'set_network', str(network_id), 'psk', f'"{psk}"'], check=True)

    # 4. Enable the new network
    subprocess.run(['sudo', 'wpa_cli', '-i', interface, 'enable_network', str(network_id)], check=True)

    # 5. Save the configuration to wpa_supplicant.conf
    subprocess.run(['sudo', 'wpa_cli', '-i', interface, 'save_config'], check=True)

    # 6. Reconfigure wpa_supplicant to apply changes
    subprocess.run(['sudo', 'wpa_cli', '-i', interface, 'reconfigure'], check=True)

    print("Network configuration updated. The device should now connect.")

    # Optional: Add a delay and check connectivity
    time.sleep(10)
    check_connection()


def check_connection():
    # A simple way to check for a valid IP address on the interface
    try:
        ip_addr = subprocess.check_output(['hostname', '-I'], encoding='utf-8').strip()
        if ip_addr:
            print(f"Successfully connected with IP: {ip_addr.split()[0]}")
        else:
            print("Connection status uncertain, no IP found.")
    except subprocess.CalledProcessError:
        print("Could not verify IP address.")


def remove_punctuation(text):
    """
    Removes all common punctuation from a string.

    Args:
      text: The input string with potential punctuation.

    Returns:
      A new string with punctuation removed.
    """
    # Create a translation table that maps every punctuation character to None (effectively removing it)
    # The first two arguments are empty strings (no character mapping), and the third specifies characters to delete
    translator = str.maketrans('', '', string.punctuation)

    # Apply the translation table to the input string
    return text.translate(translator)

class Manila:
    def __init__(self, debug=False):
        self.debug = debug
        self.topics = ["General", "materials", "sync", "chain_of_command"]
        self.recon = []
        self.materials = []
        self.r_materials = []
        self.ammo = []
        self.count = 0
        self.rank = "General"
        self.home_network = {"ssid": "Jewel", "password": os.getenv("JEWEL_PASSWORD")}
        self.other_networks = [
            {"ssid": "Common Ground", "password": os.getenv("CG_PASSWORD")},
        ]
        self.mode = "init"
        self.the_loop = True
        self.BOT_TOKEN = os.getenv("TELEGRAM_BOT_KEY")
        self.broker_address = "192.168.4.1"
        self.broker_port = 1883
        self.username = "0"
        self.password = "secret"
        # Function to handle incoming messages
        
        # Create MQTT client
        try:
            self.client = mqtt.Client()
            # Set username and password
            self.client.username_pw_set(self.username, self.password)
            # Assign the message handling function
            self.client.on_message = self.on_message
            # Connect to MQTT broker
            self.client.connect(self.broker_address, self.broker_port)
            self.army = []
            for topic in self.topics:
                self.client.subscribe(topic)
            pack = {
                
                "username": self.username,
                "as": "General",
            }
            self.client.publish("sync", pack)
        except:
            ii = input("switch to other wifi? y/n")
            if ii == "y":

                print("switching wifi...")
                TARGET_SSID = "Common Ground"
                TARGET_PSK = "newkings"
                switch_wifi_network(TARGET_SSID, TARGET_PSK)


    def scrape_youtube(self):
        pass
    def init(self):
        if self.debug:
            with open('debug_data.json', 'r') as f:
                self.recon = json.load(f)
                self.mode = "push_down"
        else:
            # scrape from telegram recommendations(youtube)
            res = asyncio.run(get_missing_messages(self.BOT_TOKEN))

            for rr in res:
                if validators.url(rr["message"]):
                    with open('data.json', 'r') as f:
                        the_data = json.load(f)
                        pack = {
                            "id": len(the_data) + 1,
                            "url": rr["message"],
                            "timestamp": datetime.utcnow(),
                            "status": 0
                        }
                        the_data.append(pack)

                        with open('data.json', 'w') as e:
                            json.dump(the_data, e)
                else:
                    print(r["message"], " is not a valid URL")

            with open('data.json', 'r') as f:
                data = json.load(f)
                for d in data:
                    if d["status"] == 0:
                        try:
                            ydl_opts = {
                                'writeautomaticsub': True,# Download automatic subtitles (use 'writesubtitles': True for manually added)
                                'subtitlesformat': 'srt',  # Specify format (srt, vtt, etc.)
                                'skip_download': True,  # Only download subtitles, not the video
                                'outtmpl': f'{d["id"]}',  # Output filename template (e.g., 'aKEatGCJUGM.en.srt')
                                'subtitleslangs': ['en']  # Specify language(s)
                            }
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                ydl.download([d["url"]])
                            file_path = f'{d["id"]}.en.srt'
                            plain_text = srt_to_plain_text(file_path)
                            self.recon.append({"pt": plain_text})
                            #delete srt?
                            d["status"] = 1

                        except Exception as e:
                            print(e)
                    else:
                        pass
                #writes in the new statuses
                with open('data.json', 'w') as f:
                    json.dump(data, f)
        self.mode = "push_down"
    def push_up(self):
        # push bitcoin addresses
        self.client.disconnect()
        TARGET_SSID = "Common Ground"
        TARGET_PSK = "newkings"
        switch_wifi_network(TARGET_SSID, TARGET_PSK)
        # add bitcoin stuff


    def push_down(self):
        repetitions = len(self.recon)
        appender = []
        counter = 0
        for i in range(repetitions):
            for troop in self.army:
                packi = {

                    "for": troop["username"],
                    "payload": self.recon[counter]
                }
                counter += 1
                print(packi)
                self.client.publish("materials", packi)
        self.client.publish("stat", {'status': "waiting"})
        self.mode = "waiting"
    def waiting(self):
        wait = True
        while wait:
            # build own mnemonics
            for i in range(1, 25):
                mm = generate_mc()
                self.materials.append(mm)
            item_counter = 1
            for item in self.materials:
                print(item_counter)
                print('item: ', item)
                item_counter += 1

                for i in range(len(self.materials)):
                    fe = [sublist[i] for sublist in self.materials]
                    print("fe: ", fe)
                    print("fe len: ", len(fe))
                    #check for duplicates
                    no_dupes = list(dict.fromkeys(fe))
                    if len(no_dupes) == len(fe):
                        gg = " ".join(fe)
                        self.r_materials.append(gg)
                    else:
                        nd_len = len(fe) - len(no_dupes)
                        gen = generate_mc()
                        for i in range(nd_len):
                            r_gen_loop = True
                            while r_gen_loop:
                                r_gen = random.choice(gen.split(" "))
                                if r_gen not in no_dupes:
                                    no_dupes.append(r_gen)
                                    r_gen_loop = False
                                else:
                                    pass
                        gg = " ".join(no_dupes)
                        self.r_materials.append(gg)

    def loop(self):
        while self.the_loop:
            if self.mode == "init":
                self.init()
                self.mode = "push_down"
            elif self.mode == "push_up":
                self.push_up()
            elif self.mode == "push_down":
                self.push_down()
            elif self.mode == "waiting":
                self.waiting()
            if self.debug:
                packk = {
                    "army": self.army,
                    "mode": self.mode,
                    "rank": self.rank,
                    "recon": self.recon,

                }
                print("debug: ")
                print(packk)

    async def mine_loop(self, the_words):

        num_threads = 5  # Adjust as needed
        live_counter_list = [0]  # Using a list to make it mutable
        dead_counter_list = [0]  # Using a list to make it mutable
        balanced_addresses = []
        loop_while = True
        async with aiohttp.ClientSession() as session:
            while loop_while:
                tasks = [process_address(session, the_words, live_counter_list, dead_counter_list, balanced_addresses) for _ in
                         range(num_threads)]
                await asyncio.gather(*tasks)

                # Check for balanced addresses and save them to a file
                if len(balanced_addresses) > 0:
                    filename = f'data_{random.randint(1, 1000000)}.txt'
                    with open(filename, 'w') as file:
                        file.write('\n'.join(balanced_addresses))
                    print(colored(f'{len(balanced_addresses)} Balanced addresses saved to {filename}', 'yellow'))
                    balanced_addresses = []  # Clear the list after saving
                    loop_while = False

    def on_message(self, client, userdata, message):
        print("client:", client)
        print("topic:", message.topic)
        print("userdata:", userdata)
        print("Received message:", message.payload.decode("utf-8"))
        mm = message.payload.decode("utf-8")
        if message.topic == "sync":
            print("sync message!!!")
            if len(self.army) == 0:
                packi = {"username": mm["username"], "rank": "team_leader", "status": "init"}
                self.army.append(packi)
                new_packi = {
                    "type": "promotion",
                    "subject_username": mm["username"],
                    "set_rank_to": "team_leader",
                }
                self.client.publish("command", new_packi)

            else:
                dupe_count = 0
                for troop in self.army:
                    if troop["name"] == mm["username"]:
                        dupe_count += 1
                if dupe_count == 0:
                    packi = {"name": mm["username"], "rank": "soldier"}
                    self.army.append(packi)
                else:
                    pass

        elif message.topic == "ammo":
            self.ammo.append(mm["payload"])
            #the return
            # needs int to tell how many came back from materials
            pass


if "__main__" == __name__:
    debug = input("debug mode? (y/n)")
    if debug == "y":
        m = Manila(debug=True)

    if debug == "n":
        m = Manila()
