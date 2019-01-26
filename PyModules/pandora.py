from threading import Thread
import pexpect
import time

class Pandora:
    def __init__(self, anton, station=""):
        self.station = station
        self.anton = anton
        self.isRunning = 0
        self.isPlaying = 0
        self.pandora = None
        if self.station != "":
            pass

    def startPandora(self, station):
        self.anton.isPlaying = self.anton.pandora
        self.anton.continuePlaying = 1
        self.isRunning = 1
        self.isPlaying = 1
        self.pandora = pexpect.spawn("pianobar")
        self.pandora.expect_exact("stations...")
        print("Before: ", self.pandora.before.decode())
        print("After: ", self.pandora.after.decode())
        self.pandora.logfile = open("test", "wb")
        try:
            self.pandora.sendline(station)
        except Exception as e:
            print(e)
            print("Bad station. I think")

    def sendCommand(self, command):
        try:
            self.pandora.send(command)
            self.pandora.expect(".*")
        except Exception as e:
            print("Something went wrong with Pandora")
            print(e)

    def pause(self):
        if self.isPlaying and self.isRunning:
            self.sendCommand("p")
            self.isPlaying = 0
        else: #TODO: Handle if pandora isn't running
            return

    def play(self):
        if not self.isPlaying and self.isRunning:
            self.sendCommand("p")
            self.isPlaying = 1
            self.anton.continuePlaying = 1
            self.anton.isPlaying = self.anton.pandora
        else: #TODO: Handle if pandora isn't running
            return

    def skip(self):
        self.sendCommand("n")

    def likeSong(self):
        self.sendCommand("+")

    def dislikeSong(self):
        self.sendCommand("-")

    def tiredSong(self):
        self.sendCommand("t")

    def changeStation(self, station):
        if self.pandora == None:
            self.startPandora(station)
            return
        self.sendCommand("s")
        self.pandora.sendline(station)
        self.pandora.expect("station:")
        print("Before: ", self.pandora.before.decode())
        print("After: ", self.pandora.after.decode())
        try:
            self.pandora.expect("Ok", timeout=2)
            print("Before: ", self.pandora.before.decode())
            print("After: ", self.pandora.after.decode())
        except:
            self.requestCreate(station)
        if "select" in self.pandora.before.decode():
            self.requestCreate(station)
        else:
            self.station = station
            self.isPlaying = 1

    def createStation(self, station):
        self.sendCommand("c")
        self.pandora.sendline(station)
        self.pandora.send("0")  #TODO: Make sure station is correct
        self.isPlaying = 1
        self.station = station
        
    def requestCreate(self, station):
        print("Request Create")
        return
        anton.tts("The station " + station + " does not exist. Would you like me to create it?")
        if anton.record() == 1:
            self.createStation(station)

