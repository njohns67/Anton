from threading import Thread
from pixel_ring import pixel_ring as pr
from gpiozero import LED
import APICalls
import parseTranscript as pT
import handleTrigger as hT
import tts
import wifiDevices
import time

class Anton:
    def __init__(self, isRecording=0, isPlaying=0):
        self.power = LED(5)
        self.power.on()
        pr.set_brightness(100)
        self.isRecording = isRecording
        self.isPlaying = isPlaying
        self.isDead = 0
        thread = Thread(target=self.getAverageRMS)
        thread.daemon = True
        thread.start()
        self.recordingInfo = {"minRMS": 5000000, "length": 8, "samplerate": 48000,
                              "channels": 1, "width": 2, "chunk": 1024, "tempFileName": "temp.wav"}
        self.filePaths = {"dong": "/home/pi/Anton/Sounds/dong.wav", "ding": "/home/pi/Anton/Sounds/ding.wav"}
        self.processes = []

    def getJoke(self):
        APICalls.getJoke()

    def parseTranscript(self, transcript):
        pT.parse(self, transcript)

    def getForecast(self, city="Menomonee Falls", day="today"):
        APICalls.getForecast(city, day)

    def askQuestion(self, question):
        APICalls.askQuestion(question)

    def record(self):
        hT.main(self)
    
    def textToSpeech(self, text, play=1):
        tts.text2speech(text, PLAY=play)

    def feedScout(self):
        wifiDevices.feedScout()

    def beerMe(self):
        wifiDevices.beerMe()

    def getAverageRMS(self):
        hT.getAverageRMS(self)

    def lightOn(self):
        pr.set_color_delay(r=0, g=0, b=255, delay=.02)

    def lightSuccess(self):
        pr.set_color(r=0, g=255, b=0)

    def lightFail(self):
        pr.set_color(r=255, g=0, b=0)

    def lightOff(self):
        pr.turn_off_color_delay(delay=.02)
