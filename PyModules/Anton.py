from __future__ import division
from threading import Thread
from pixel_ring import pixel_ring as pr
from gpiozero import LED
import APICalls, tts, wifiDevices
import parseTranscript as pT
import handleTrigger as hT
import time, os
from roku import Roku
from mpc import MPC
from pandora import Pandora
from thermostat import Thermostat
from command import Command
import re, sys
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue
from subprocess import Popen, PIPE

class Anton:
    def __init__(self, debug=0, verbose=0):
        self.power = LED(5)
        self.power.on()
        self.roku = Roku(self, "192.168.1.75")
        self.mpc = MPC(anton=self)
        self.pandora = Pandora(self)
        self.thermostat = Thermostat(self)
        pr.set_brightness(100)
        self.isRecording = 0
        self.isPlaying = self.roku
        self.continuePlaying = 0
        self.isDead = 0
        self.debug = debug
        self.verbose = verbose
        self.processes = []
        self.isMuted = 0
        self.bellsOff = 0
        self.isResponding = 0
        self.endSTT = -1
        self.transcriptTries = 0
        self.transcript = ""
        self.turnLightOff = True
        self.recordingInfo = {"minRMS": 12000000, "length": 8, "samplerate": 48000,
                              "channels": 1, "width": 2, "chunk": 1024, "tempFileName": "temp.wav"}
        self.filePaths = {"dong": "/home/pi/Anton/Sounds/dong.wav", "ding": "/home/pi/Anton/Sounds/ding.wav"}
        if self.verbose:
            thread = Thread(target=self.printSubprocessOutput)
            thread.daemon = True
            thread.start()
        #if not self.debug:
        #       thread = Thread(target=self.getAverageRMS)
        #       thread.daemon = True
        #       thread.start()

    def getJoke(self):
        APICalls.getJoke(self)

    def parseTranscript(self, transcript):
        if self.debug:
            return pT.parse(self, transcript)
        else:
            test = pT.parse(self, transcript)
            return test

    def getForecast(self, city="Menomonee Falls", day="today"):
        APICalls.getForecast(self, city, day)

    def askQuestion(self, question):                #Future development needed; not used
        return APICalls.askQuestion(self, question)

    def record(self):
        '''Records a transcript and checks the return status of the transcript.
        This function is mostly used for handling playback after pausing for transcription'''
        self.sttCountdown()
        self.isRecording = 1
        self.lightOn()
        self.playDong()
        if self.isPlaying != None and self.isPlaying != self.roku:
            self.isPlaying.pause()
        STTRet = self.speechToText()
        print(self.transcript)
        print(STTRet)
        if STTRet == -1:
            self.lightFail()
            with open("log.txt", "a") as f:
                f.write("Bad transcript\n")
            print("Something went wrong")
            self.endRecord()
            return -1
        if self.isResponding:
            self.isResponding = 0
            return self.transcript
        self.endRecord()

    def endRecord(self):
        if self.continuePlaying and self.continuePlaying != self.roku:
            self.isPlaying.play()
        while not self.turnLightOff:
            pass
        self.lightOff()
        self.endSTT = -1
        self.transcriptTries = 0
        self.isRecording = 0

    def speechToText(anton):
        '''Copied straight from google's documentation. Slightly modified.
        When a transcript's "is_final" variable is True then a Command class 
        is created and the transcript is passed to it. If the Command's __init__
        returns -1 then the transcript did not contain a keyword and the function
        continues listening for another transcript. A max of 2 transcripts will
        be recorded before exiting'''
        RATE = 48000
        CHUNK = 1024 
        count = 0
        class MicrophoneStream(object):
            def __init__(self, rate, chunk, anton):
                self._rate = rate
                self._chunk = chunk
                self._buff = queue.Queue()
                self.closed = True
                self.anton = anton
                self.count = 0
                self.ended = False

            def __enter__(self):
                self._audio_interface = pyaudio.PyAudio()
                self._audio_stream = self._audio_interface.open(
                    format=pyaudio.paInt16,
                    channels=1, rate=self._rate,
                    input=True, frames_per_buffer=self._chunk,
                    stream_callback=self._fill_buffer)

                self.closed = False
                return self

            def __exit__(self, type, value, traceback):
                self._audio_stream.stop_stream()
                self._audio_stream.close()
                self.closed = True
                self._buff.put(None)
                self._audio_interface.terminate()

            def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
                self._buff.put(in_data)
                return None, pyaudio.paContinue

            def generator(self):
                while not self.closed:
                    if self.anton.endSTT > 7:
                        print("Ending")
                        self.ended = True
                        self.closed = True
                        self.anton.lightFail()
                    chunk = self._buff.get()
                    if chunk is None:
                        return
                    data = [chunk]

                    while True:
                        try:
                            chunk = self._buff.get(block=False)
                            if chunk is None:
                                return
                            data.append(chunk)
                        except queue.Empty:
                            break

                    yield b''.join(data)


        def listen_print_loop(responses, anton):
            num_chars_printed = 0
            for response in responses:
                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue
                transcript = result.alternatives[0].transcript
                overwrite_chars = ' ' * (num_chars_printed - len(transcript))

                if not result.is_final:
                    sys.stdout.write(transcript + overwrite_chars + '\r')
                    sys.stdout.flush()
                    num_chars_printed = len(transcript)

                else:
                    anton.transcriptTries += 1
                    checkValid = anton.checkTranscript(transcript)
                    if checkValid == -1 and anton.transcriptTries < 2:
                        print("Passing")
                        sys.stdout.flush()
                        anton.endSTT = 0
                        pass
                    else:
                        anton.transcript = transcript
                        return checkValid
                    num_chars_printed = 0

        def start(anton):
            client = speech.SpeechClient()
            language_code = 'en-US'
            config = types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code=language_code)
            streaming_config = types.StreamingRecognitionConfig(
                config=config,
                interim_results=True)

            with MicrophoneStream(RATE, CHUNK, anton) as stream:
                audio_generator = stream.generator()
                requests = (types.StreamingRecognizeRequest(audio_content=content)
                                for content in audio_generator)
                responses = client.streaming_recognize(streaming_config, requests)
                return listen_print_loop(responses, anton)
        return start(anton)

    def checkTranscript(self, transcript):
        command = Command(self, transcript)
        result = command.execCommand()
        return result

    def feedScout(self):
        try:
            wifiDevices.feedScout()
        except:
            print("Couldn't feed Scout")

    def beerMe(self):
        wifiDevices.beerMe()

    def getAverageRMS(self):
        if self.debug == 1:
            return
        else:
            hT.getAverageRMS(self)

    def lightOn(self):
        def f():
            pr.set_color_delay(r=0, g=0, b=255, delay=.02)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()
        return thread

    def lightSuccess(self):
        def f():
            def g():
                pr.set_color_delay(r=0, g=255, b=0, delay=.02)
            thread = Thread(target=g)
            thread.daemon = True
            thread.start()
            self.turnLightOff = False
            time.sleep(2)
            self.turnLightOff = True
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()

    def lightFail(self):
        def f():
            pr.set_color(r=255, g=0, b=0)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()

    def lightOff(self):
        def f():
            pr.turn_off_color_delay(delay=.02)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()

    def lightListening(self):
        def f():
            pr.set_color_delay(r=255, g=132, b=0, delay=.02)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()

    def tts(self, text, file="/home/pi/Anton/Responses/delme",  play=1):
        APICalls.tts(self, text, file, play)

    def play(self, response, adddir=1):
        directory = "/home/pi/Anton/Responses/"
        if not self.isMuted:
            if adddir:
                APICalls.play(self, directory+response)
            else:
                APICalls.play(self, response)

    def playShow(self, show, season="", channel=""):
        self.roku.playShow(show=show, season=season, channel=channel)

    def setOven(self, temp):
        wifiDevices.setOven(temp)
        if temp == 0:
            self.play("OvenOff")
            return
        self.tts("Setting the oven to " + str(temp))

    def printSubprocessOutput(self):
        while self.isDead != 1:
            for x in self.processes:
                if x.poll() != None:
                    print("process removed")
                    self.processes.remove(x)
                    print(x.stdout.read().decode())
                print(x.stderr.read().decode())

    def setIsPlaying(self):
        if any(x in self.command.transcript for x in ["tv", "t.v.", "television", "hulu", "netflix"]):
            self.isPlaying = self.roku
        elif "music" in transcript:
            self.isPlaying = self.mpc
        elif "pandora" in transcript:
            self.isPlaying = self.pandora
        self.play("WhatPlay")
        self.isResponding = 1
        transcript = self.record()
        print(transcript)
        transcript = transcript.lower()
        if any(x in transcript for x in ["tv", "t.v.", "television", "hulu", "netflix"]):
            self.isPlaying = self.roku
        elif "music" in transcript:
            self.isPlaying = self.mpc
        elif "pandora" in transcript:
            self.isPlaying = self.pandora

    def changeMuteMode(self, mode=3):
        if mode == 3:
            self.bellsOff = not self.bellsOff
        else:
            self.bellsOff = mode

    def playDong(self):
        if not self.bellsOff:
            p = Popen(["play", self.filePaths["dong"]], stdout=PIPE, stderr=PIPE)
            self.processes.append(p)

    def sttCountdown(self):
        def f():
            self.endSTT = 0
            while self.endSTT < 9 and self.endSTT != -1:
                self.endSTT += 1
                time.sleep(1)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()
