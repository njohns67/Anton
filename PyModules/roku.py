import requests
import xml.etree.ElementTree as ET
import time

class Roku:
    def __init__(self, anton="", ip="192.168.1.75", port="8060"):
        self.isOn = 0
        self.anton = anton
        self.ip = ip
        self.port = port
        self.url = "http://" + ip + ":" + port + "/"
        self.letterPosition = [['a', 'g', 'm', 's', 'y', '5'],
                               ['b', 'h', 'n', 't', 'z', '6'],
                               ['c', 'i', 'o', 'u', '1', '7'],
                               ['d', 'j', 'p', 'v', '2', '8'],
                               ['e', 'k', 'q', 'w', '3', '9'],
                               ['f', 'l', 'r', 'x', '4', '0']]
        self.appIDs = {}
        response = requests.get(self.url+"query/apps").text
        root = ET.fromstring(response)
        for child in root:
            id = child.get("id")
            name = child.text
            nameSplit = name.split()
            self.appIDs[name] = id
            for s in nameSplit:
                self.appIDs[s.lower()] = id
        response = requests.get(self.url+"query/device-info").text
        root = ET.fromstring(response)
        child = root.find("power-mode")
        if child.text != "PowerOn":
            self.isOn = 0
        else:
            self.isOn = 1

    def sendString(self, string):
        for c in string:
            requests.post(self.url+"keypress/Lit_"+c)

    def pressKey(self, key, num=1):
        print(num)
        for x in range(0, num):
            requests.post(self.url+"keypress/"+key)
            time.sleep(.5)

    def launchApp(self, name="", id=""):
        if not self.isOn:
            self.power()
            time.sleep(5)
        if id != "":
            requests.post(self.url+"launch/"+id)
        else:
            name = name.lower()
            requests.post(self.url+"launch/"+self.appIDs[name])

    def playShowNetflix(self, show, channel="hulu"):
        self.launchApp("netflix")
        time.sleep(15)
        self.pressKey("select")
        self.pressKey("left")
        self.pressKey("up")
        self.pressKey("select")
        self.sendString(show)
        for x in range(0, len(self.letterPosition)):
            print(x)
            if show[len(show)-1] in self.letterPosition[x]:
                num = x
                break
        time.sleep(5)
        self.pressKey("right", 6-num)
        self.pressKey("select")
        self.pressKey("select")

    def power(self):
        requests.post(self.url+"keypress/power")
        self.isOn = not self.isOn

    def playShow(self, show, channel="hulu", season=""):
        channel = channel.lower()
        print(self.isOn)
        if not self.isOn:
            self.power()
        requests.post(self.url+"search/browse", params={"provider": channel, "season": season, "match-any": "true", "launch": "true", "title": show})
        time.sleep(23)
        self.pressKey("select")

    def play(self):
        self.anton.continuePlaying = 1
        self.pressKey("play")

    def pause(self):
        self.pressKey("play")

    def continueHulu(self):
        if not self.isOn:
            self.power()
            time.sleep(15)
        self.launchApp("hulu")
        time.sleep(12)
        self.pressKey("right")
        self.pressKey("down")
        self.pressKey("select")

    def volumeUp(self, num=2):
        self.pressKey("VolumeUp", num)

    def volumeDown(self, num=2):
        self.pressKey("VolumeDown", num)
