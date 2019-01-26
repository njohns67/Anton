from threading import Thread
from pixel_ring import pixel_ring as pr
from gpiozero import LED
import os
import APICalls
import parseTranscript as pT
import handleTrigger as hT
import tts
import wifiDevices
import time
from roku import Roku
from mpc import MPC
from pandora import Pandora

class Anton:
    def __init__(self, debug=0, verbose=0):
        self.power = LED(5)
        self.power.on()
        self.roku = Roku(self, "192.168.1.75")
        self.mpc = MPC(self)
        self.pandora = Pandora(self)
        pr.set_brightness(100)
        self.isRecording = 0
        self.isPlaying = None
        self.continuePlaying = 0
        self.isDead = 0
        self.debug = debug
        self.verbose = verbose
        self.processes = []
        self.isMuted = 0
        self.bellsOff = 0
        self.isResponding = 0
        self.recordingInfo = {"minRMS": 10000000, "length": 8, "samplerate": 48000,
                              "channels": 1, "width": 2, "chunk": 1024, "tempFileName": "temp.wav"}
        self.filePaths = {"dong": "/home/pi/Anton/Sounds/dong.wav", "ding": "/home/pi/Anton/Sounds/ding.wav"}
        if self.verbose:
            thread = Thread(target=self.printSubprocessOutput)
            thread.daemon = True
            thread.start()
        if not self.debug:
            thread = Thread(target=self.getAverageRMS)
            thread.daemon = True
            thread.start()

    def getJoke(self):
        APICalls.getJoke(self)

    def parseTranscript(self, transcript):
        if self.debug:
            return pT.parse(self, transcript)
        else:
            test = pT.parse(self, transcript)
            if self.continuePlaying:
                self.isPlaying.play()
            return test

    def getForecast(self, city="Menomonee Falls", day="today"):
        APICalls.getForecast(self, city, day)

    def askQuestion(self, question):
        return APICalls.askQuestion(self, question)

    def record(self):
        if self.isPlaying != None and self.isPlaying != self.roku:
            self.isPlaying.pause()
            self.continuePlaying = 0
        transcript = hT.main(self)
        print(transcript)
        self.isRecording = 0
        if transcript == -1:
            self.lightOff()
            return -1
        if self.isResponding:
            self.isResponding = 0
            return transcript
        test = self.parseTranscript(transcript)
        if test == -1:
            print("Something went wrong")
            pass       #Idk maybe do something with this later it's currently handled in parseTranscript()
        self.lightOff()

    def feedScout(self):
        wifiDevices.feedScout()

    def beerMe(self):
        wifiDevices.beerMe()

    def getAverageRMS(self):
        if self.debug == 1:
            return
        else:
            hT.getAverageRMS(self)

    def lightOn(self):
        pr.set_color_delay(r=0, g=0, b=255, delay=.02)

    def lightSuccess(self):
        pr.set_color(r=0, g=255, b=0)

    def lightFail(self):
        pr.set_color(r=255, g=0, b=0)

    def lightOff(self):
        pr.turn_off_color_delay(delay=.02)

    def tts(self, text, file="delme",  play=1):
        APICalls.tts(self, text, file, play)

    def play(self, response):
        directory = "/home/pi/Anton/Responses/"
        if not self.isMuted:
            APICalls.play(self, directory+response)
    
    def playShow(self, show, season="", channel=""):
        self.roku.playShow(show=show, season=season, channel=channel)

    def printSubprocessOutput(self):
       while self.isDead != 1:
           for x in self.processes:
               if x.poll() != None:
                   print("process removed")
                   self.processes.remove(x)
               print(x.stdout.read().decode())
               print(x.stderr.read().decode())
