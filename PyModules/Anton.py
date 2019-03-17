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
    '''Main Anton class. 
    General form: 
    When a hotword is detected ("Hey Anton"), recording begins immediately. Google speech's live 
    speech-to-text API is used and is alloted a maximum of 10 seconds to record a transcript. 
    It will, however, detect when you end a sentence and not use the full 10 seconds. 
    
    This was initially done manually by me calculating the average RMS value
    of the sound levels in the room and storing this so when a hotword was detected, a person talking 
    would raise this value compared to the average so when the person stopped talking and the active 
    value approached the average, Anton would know a command had been spoken. Now, Google's live STT 
    API does this for me. 
    
    When a transcript has been recorded, a Command class instance is created
    and passed the transcript. More on that in command.py. If a word in the transcript is associated
    with a command, the command is executed after all the pertinent information is set. This is done
    sometimes by directly calling the command if no parsing is needed, but generally a wrapper function
    is called to do the heavy lifting and give Anton the information needed. If no keyword is found, 
    -1 is returned allowing for another 10 seconds of listening for a transcript before Anton goes
    back to listening for a keyword
    
    Anton contains instances of classes used to control various devices. Each media class contains function
    definitions for common functions, each with the same name. This allows for Anton's isPlaying variable
    to be a pointer to the active media's class and for all common functions to be called without having
    to figure out what media class is active. Basically if you tell Anton to "pause", all that is needed is
    Anton.isPlaying.pause() instead of having to determine if the TV is playing, or pandora, or spotify because
    each of those classes all have functions named "pause". By default the TV is active. However, in the instance
    that isPlaying does not reflect the actual active media (i.e. you use spotify so it points to an MPC class but
    then you turn the TV on manually but Anton thinks spotify is the active media), you can simply include the
    device you want to control in your command (pause the TV) and the variables will be adjusted and the command executed 
    appropriately'''
    def __init__(self, debug=0, verbose=0):
        self.power = LED(5)
        self.power.on()
        self.roku = Roku(self, "192.168.1.75")
        self.mpc = MPC(anton=self)
        self.pandora = Pandora(self)
        self.thermostat = Thermostat(self)
        pr.set_brightness(100)
        self.isRecording = 0
        self.isPlaying = self.roku  #Active media class variable
        self.continuePlaying = 0    #Determines whether or not media should be paused/resume playing on/after keyword trigger
        self.isDead = 0             #Obsolete. I think
        self.debug = debug          #Setting command flag -d or --debug enables debug mode which allows for input via text
        self.verbose = verbose      #Setting command flag -v or --verbose prints all thread's output
        self.processes = []         #List of processes spawned. Not really used. Just here for posterity's sake
        self.silentMode = 0            #Silent mode toggle. When on no bells or responses will be played
        self.quietMode = 0           #Mute mode. No bells will be played. TODO: Change to quiet mode
        self.isResponding = 0       #Obsolete. Used previously to pause determining average RMS
        self.endSTT = -1            #Timer variable for recording to timeout after 10 seconds
        self.transcriptTries = 0    #Counter for the number of unusuable transcripts recorded for a keyword before giving up. Max of 2
        self.transcript = ""        #Last transcript recorded
        self.turnLightOff = True    #Allows success light to stay on for 2 seconds instead of going away instantly
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
        '''Obsolete. Only kept until the refactor is fully tested'''
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
        '''Resets variables to a pre-recorded state and continues playing music
        if needed'''
        if self.continuePlaying and self.continuePlaying != self.roku:
            self.isPlaying.play()
        while not self.turnLightOff:
            pass
        self.lightOff()
        self.endSTT = -1
        self.transcriptTries = 0
        self.isRecording = 0

    def speechToText(anton):
        '''Copied straight from google's documentation and modified to allow for timeouts..
        When a transcript's "is_final" variable is True then a Command class 
        is created and the transcript is passed to it. If the checkCommand()
        returns -1 then the transcript did not contain a keyword and the function
        continues listening for another transcript. A max of 2 transcripts will
        be recorded before exiting. A maximum of 10 seconds is alloted for recording
        before the function will timeout'''
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
                '''Timeouts after 10 seconds of no transcript'''
                while not self.closed:
                    if self.anton.endSTT > 9:
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
        '''Obsolete'''
        if self.debug == 1:
            return
        else:
            hT.getAverageRMS(self)

    def lightOn(self):
        '''Blue light signaling hotword detected and recording'''
        def f():
            pr.set_color_delay(r=0, g=0, b=255, delay=.02)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()
        return thread

    def lightSuccess(self):
        '''Green light signaling the transcript matched a command'''
        def f():
            def g():
                pr.set_color(r=0, g=255, b=0)
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
        '''Red light signaling an unusuable transcript or none at all'''
        def f():
            pr.set_color(r=255, g=0, b=0)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()

    def lightOff(self):
        '''Turns off the light'''
        def f():
            pr.turn_off_color_delay(delay=.02)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()

    def lightListening(self):
        '''Orange light signalling roku control mode is active'''
        def f():
            pr.set_color_delay(r=255, g=132, b=0, delay=.02)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()

    def tts(self, text, file="/home/pi/Anton/Responses/delme",  play=1):
        if self.silentMode:
            play = 0
        APICalls.tts(text, file, play)

    def play(self, response, addDir=1):
        '''Plays a text-to-speech response. The default directory is only added if addDir is true'''
        directory = "/home/pi/Anton/Responses/"
        if not self.silentMode:
            if addDir:
                APICalls.play(directory+response)
            else:
                APICalls.play(response)

    def playShow(self, show, season="", channel=""):
        '''Not functional'''
        self.roku.playShow(show=show, season=season, channel=channel)

    def setOven(self, temp):
        wifiDevices.setOven(temp)
        if temp == 0:
            self.play("OvenOff")
            return
        self.tts("Setting the oven to " + str(temp))

    def printSubprocessOutput(self):
        '''Thread target for printing all output when -v is enabled'''
        while self.isDead != 1:
            for x in self.processes:
                if x.poll() != None:
                    print("process removed")
                    self.processes.remove(x)
                    print(x.stdout.read().decode())
                print(x.stderr.read().decode())

    def setIsPlaying(self):
        '''Sets the current active media'''
        if any(x in self.command.transcript for x in ["tv", "t.v.", "television", "hulu", "netflix"]):
            self.isPlaying = self.roku
        elif "music" in transcript:
            self.isPlaying = self.mpc
        elif "pandora" in transcript:
            self.isPlaying = self.pandora
        self.play("WhatPlay")
        self.isResponding = 1
        transcript = self.record()
        transcript = transcript.lower()
        if any(x in transcript for x in ["tv", "t.v.", "television", "hulu", "netflix"]):
            self.isPlaying = self.roku
        elif "music" in transcript:
            self.isPlaying = self.mpc
        elif "pandora" in transcript:
            self.isPlaying = self.pandora

    def toggleSilentMode(self):
        '''Toggles silent mode'''
        self.silentMode = not self.silentMode

    def toggleQuietMode(self):
        self.quietMode = not self.quietMode

    def playDong(self):
        if not self.quietMode:
            p = Popen(["play", self.filePaths["dong"]], stdout=PIPE, stderr=PIPE)
            self.processes.append(p)

    def sttCountdown(self):
        '''Timer thread for transcription timeout'''
        def f():
            self.endSTT = 0
            while self.endSTT < 11 and self.endSTT != -1:
                self.endSTT += 1
                time.sleep(1)
        thread = Thread(target=f)
        thread.daemon = True
        thread.start()
