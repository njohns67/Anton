from threading import Thread
import pexpect

class Pandora:
    def __init__(self, anton, station=""):
        self.anton = anton
        self.station = station
        self.isRunning = 0
        self.isPlaying = 0
        self.pandora = None
        if self.station != "":
            pass

    def startPandora(self, station):
        self.isRunning = 1
        self.isPlaying = 1
        self.pandora = pexpect.spawn("pianobar")
        try:
            self.pandora.send(station)
        except Exception as e:
            print(e)
            print("Bad station. I think")

    def sendCommand(self, command):
        try:
            self.pandora.send(command)
        except Exception as e:
            print("Something went wrong with Pandora")
            print(e)

    def pause(self):
        if self.isPlaying and self.isRunning:
            self.sendCommand("S")
            self.isPlaying = 1
        else: #TODO: Handle if pandora isn't running
            return

    def play(self):
        if not self.isPlaying and self.isRunning:
            self.sendCommand("P")
            self.isPlaying = 1
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
        self.sendCommand("s")
        self.pandora.sendline(station)
        self.pandora.expect("[?] Select station:")
        if "select" in self.pandora.before:
            self.requestCreate(station)
        else:
            self.station = 1
            self.isPlaying = 1

    def createStation(self, station):
        self.sendCommand("c")
        self.pandora.sendline(station)
        self.pandora.sendline("0")  #TODO: Make sure station is correct
        self.isPlaying = 1
        self.station = station
        
    def requestCreate(self, station):
        anton.tts("The station " + station + " does not exist. Would you like me to create it?")
        if anton.record() == 1:
            self.createStation(station)

