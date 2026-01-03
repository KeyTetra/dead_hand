import time
import paho.mqtt.client as mqtt
import time
import random
import json
import asyncio
from datetime import datetime
from mnemonic import Mnemonic
import spacy
from itertools import batched

nlp = spacy.load("en_core_web_lg")

class Manila:
    def __init__(self, debug=False):
        self.topics = ["General", "materials", "sync", "chain_of_command"]
        self.materials = []
        self.r_materials = []
        self.rank = "soldier"
        self.count = 0
        self.mode = "init"
        self.the_loop = True
        self.broker_address = "192.168.4.1"
        self.broker_port = 1883
        self.username = "1"
        self.password = "secret"
        # Function to handle incoming messages
        # Create MQTT client
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
            "as": self.rank,
        }
        self.client.publish("sync", pack)





    def loop(self):
        while self.the_loop:
            if self.mode == "init":
                self.init()
            elif self.mode == "push_up":
                if self.rank == "soldier":
                    p = {
                        "username": self.username,
                        "payload": self.materials,
                    }
                    self.client.publish("materials", p)
                elif self.rank == "team_leader":
                    p = {
                        "username": self.username,
                        "payload": self.r_materials,
                    }
                    self.client.publish("stat", p)

            packk = {
                "army": self.army,
                "mode": self.mode,
                "rank": self.rank,
                "materials": self.materials,
                "r_materials": self.r_materials,

            }
            print("debug: ")
            print(packk)

    def on_message(self, client, userdata, message):
        print("client:", client)
        print("topic:", message.topic)
        print("userdata:", userdata)
        print("Received message:", message.payload.decode("utf-8"))
        mm = message.payload.decode("utf-8")
        if message.topic == "sync":
                print("sync message!!!")
                if mm["as"] == "General":
                    dupe_count = 0
                    for troop in self.army:
                        if troop["username"] == mm["username"]:
                            dupe_count += 1
                    if dupe_count == 0:
                        packi = {"username": mm["username"], "rank": "General", "status": "init"}
                        self.army.append(packi)
                if mm["as"] == "team_leader":
                    dupe_count = 0
                    for troop in self.army:
                        if troop["username"] == mm["username"]:
                            if troop["rank"] == "team_leader":
                                dupe_count += 1
                    if dupe_count == 0:
                        packi = {"username": mm["username"], "rank": "team_leader", "status": "init"}
                        self.army.append(packi)
                if mm["as"] == "soldier":
                    dupe_count = 0
                    for troop in self.army:
                        if troop["username"] == mm["username"]:
                            if troop["rank"] == "soldier":
                                dupe_count += 1
                    if dupe_count == 0:
                        packi = {"username": mm["username"], "rank": "soldier" }
                        self.army.append(packi)
                else:
                    pass
        elif message.topic == "stat":
            if self.rank == "team_leader":
                for soldier in self.army:
                    if soldier["username"] == mm["username"]:
                        print("username match!")
                    else:
                        print("username not match!")
            # the return
            # needs int to tell how many came back from materials
        elif message.topic == "command":
            print("command recieved:", mm)
            if mm["type"] == "promotion":
                if mm["subject_username"] == self.username:
                    self.rank = mm["set_rank_to"]
                else:
                    pass

        elif message.topic == "materials":
            if mm["for"] == self.username:
                self.materials.append(mm["payload"])


    def refine_materials(self):
        if self.rank == "soldier":
            self.client.publish("stat", {'status': "busy"})
        wl = Mnemonic('english').wordlist
        for material in self.materials:
            vounter = 0
            true_keeper = []
            for mat in material.split():
                word1 = nlp(mat)
                score_keeper = []
                for word in wl:
                    word2 = nlp(word)
                    similarity_score = word1.similarity(word2)
                    score_keeper.append([similarity_score, word])
                true_keeper.append(score_keeper.sort(key=lambda x: x[0])[-1][1])
            chunk_size = 24
            chunks = list(batched(true_keeper, chunk_size))
            for ch in chunks:
                if len(ch) == chunk_size:
                    pass
                else:
                    rando_try = True
                    for i in range(chunk_size - len(ch)):
                        while rando_try:
                            rando_word = random.choice(wl)
                            if rando_word not in ch:
                                ch.append(rando_word)
                                rando_try = False
                            else:
                                pass
                seen = set()
                replaced_list = []
                for item in ch:
                    rando_try = True
                    if item in seen:
                        while rando_try:
                            rando_word = random.choice(wl)
                            if rando_word not in replaced_list:
                                replaced_list.append(rando_word)
                                rando_try = False
                    else:
                        replaced_list.append(item)
                        seen.add(item)
                self.r_materials.append(replaced_list)
        self.materials = []
        
        if self.rank == "soldier":
            self.client.publish("stat",{'status': "done", "username": self.username})
            print(len(self.r_materials)," refined materials")
        elif self.rank == "team_leader":
            self.client.publish("stat",{'status': "busy", "username": self.username})


if "__main__" == __name__:
    debug = input("debug mode? (y/n)")
    if debug == "y":
        m = Manila(debug=True)

    if debug == "n":
        m = Manila()
