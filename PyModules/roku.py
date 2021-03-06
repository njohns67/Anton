from __future__ import division
import re
import sys
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue
import requests
import xml.etree.ElementTree as ET
import time
from threading import Thread
import subprocess
from word2number import w2n

class Roku:
    '''This class controls a roku. You must obtain the IP of your roku and pass it
    in the constructor for this class in Anton.py for any of this to work. Port 8060
    is default for roku device communication'''
    def __init__(self, anton="", ip="192.168.1.75", port="8060", volume=15):
        self.isOn = 0
        self.anton = anton
        self.volume = volume
        self.isMuted = 0
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
        try:
            response = requests.get(self.url+"query/apps").text
        except:
            print("Roku not available")
            return
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
        '''Types a string on the roku. Used for things like searches'''
        for c in string:
            requests.post(self.url+"keypress/Lit_"+c)

    def pressKey(self, key, num=1):
        for x in range(0, num):
            requests.post(self.url+"keypress/"+key)
            time.sleep(.2)

    def launchApp(self, name="", id=""):
        name = name.lower()
        def launch():
            if not self.isOn:
                self.power()
                time.sleep(5)
            if id != "":
                requests.post(self.url+"launch/"+id)
            else:
                requests.post(self.url+"launch/"+self.appIDs[name])
        thread = Thread(target=launch)
        thread.daemon = True
        thread.start()

    def power(self):
        requests.post(self.url+"keypress/power")
        self.isOn = not self.isOn
        self.anton.isPlaying = self.anton.roku

    def playShow(self, show, channel="hulu", season=""):
        '''This doesn't really work because for some reason roku's general search
        doesn't show netflix results so you're limited to hulu and amazon. Also 
        you can't choose a specific episode and it defaults to the latest season'''
        channel = channel.lower()
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
        '''In theory this continues playing the last show you were watching
        on hulu. In reality hulu changes their UI layout so much it's not functional'''
        if not self.isOn:
            self.power()
            time.sleep(15)
        self.launchApp("hulu")
        time.sleep(12)
        self.pressKey("right")
        self.pressKey("down")
        self.pressKey("select")

    def volumeUp(self, num=2):
        self.volume += num
        self.anton.isPlaying = self.anton.roku
        self.pressKey("VolumeUp", num)

    def volumeDown(self, num=2):
        self.volume -= num
        self.anton.isPlaying = self.anton.roku
        self.pressKey("VolumeDown", num)

    def setVolume(self, volume):
        '''This only really works if you exclusively use Anton to control the volume
        on your TV. If you use the remote then Anton doesn't know what the actual current
        volume is, just what it was before you used the remote'''
        volumeChange = volume-self.volume
        if volumeChange < 0:
            self.volumeDown(abs(volumeChange))
        else:
            self.volumeUp(abs(volumeChange))

    def mute(self):
        self.isMuted = 1
        self.anton.isPlaying = self.anton.roku
        self.pressKey("VolumeMute")

    def unMute(self):
        self.isMuted = 0
        self.mute()

    def rokuControl(self):
        '''Roku control mode allows you to speak commands like "up, down, select, back" 
        and for them to be executed like you were pressing the buttons on the remote. 
        The caveat is that you can't repeat the same command in succession. Instead of saying
        "down down right right select" you should say "down two right two select" or you'll
        get some weird results. This is because of how google's live STT API returns interim
        results. Fixing this would result in a major loss of the speed in which a button is "pressed".
        A speech_context list is passed to the google API to ensure that words are correctly recognized.
        Because single words are hard to convert to text (since they have no context), words like "left"
        would be confused with "let" without this list. I also included phrase conversion to stop things 
        like "up right" from being understood as "upright" and so forth'''
        anton = self.anton
        RATE = 48000
        CHUNK = 1024 
        commands = {"home": True, "play": True, "select": True, "left": True, "right": True, 
                    "down": True, "up": True, "back": True, "search": True, "backspace": True, "enter": True}
        class MicrophoneStream(object):
            def __init__(self, rate, chunk):
                self._rate = rate
                self._chunk = chunk
                self._buff = queue.Queue()
                self.closed = True

            def __enter__(self):
                anton.lightListening()
                self._audio_interface = pyaudio.PyAudio()
                self._audio_stream = self._audio_interface.open(
                    format=pyaudio.paInt16,
                    channels=1, rate=self._rate,
                    input=True, frames_per_buffer=self._chunk,
                    stream_callback=self._fill_buffer,
                )

                self.closed = False

                return self

            def __exit__(self, type, value, traceback):
                self._audio_stream.stop_stream()
                self._audio_stream.close()
                self.closed = True

            def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
                self._buff.put(in_data)
                return None, pyaudio.paContinue

            def generator(self):
                while not self.closed:
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


        def listen_print_loop(responses):
            num_chars_printed = 0
            prevKey = None
            for response in responses:
                if not response.results:
                        continue
                result = response.results[0]
                if not result.alternatives:
                    continue
                transcript = result.alternatives[0].transcript
                if "upright" in transcript:
                    transcript += " up right"
                if "downright" in transcript:
                    transcript += " down right"
                if "what" in transcript: 
                    transcript += " left"
                if "to" in transcript:
                    transcript += " two"
                transcript = transcript.lower().split()
                overwrite_chars = ' ' * (num_chars_printed - len(transcript))
                if not result.is_final:
                    for word in transcript:
                        if prevKey != None:
                            try: 
                                num = w2n.word_to_num(word)
                                self.pressKey(prevKey, num=num-1)
                                prevKey = None
                            except Exception as e:
                                print(e)
                                continue
                        if word in commands and commands[word]:
                            self.pressKey(word)
                            prevKey = word
                            commands[word] = False
                    sys.stdout.write(" ".join(transcript) + " ")
                    sys.stdout.flush()
                    num_chars_printed = len(transcript)
                else:
                    prevKey = None
                    for key in commands:
                        if key in transcript and commands[key]:
                            self.pressKey(key)
                        commands[key] = True
                    if "type" in transcript:
                        typeIndex = transcript.index("type")
                        stringToSend = " ".join((transcript[typeIndex+1:]))
                        self.sendString(stringToSend)
                    transcript2 = " ".join(transcript)
                    print("Final ", transcript2 + overwrite_chars)
                    if re.search(r'\b(exit|quit)\b', transcript2, re.I):
                        print('Exiting..')
                        self.anton.play("ExitRokuControlMode")
                        break
                    num_chars_printed = 0

        def start():
            language_code = 'en-US'  # a BCP-47 language tag
            client = speech.SpeechClient()
            config = types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code=language_code,
                speech_contexts=[{"phrases": [x for x in commands]}])
            streaming_config = types.StreamingRecognitionConfig(
                config=config,
                interim_results=True)
            self.anton.play("EnterRokuControlMode")
            proc = subprocess.Popen(["play", self.anton.filePaths["dong"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.anton.processes.append(proc)
            with MicrophoneStream(RATE, CHUNK) as stream:
                audio_generator = stream.generator()
                requests = (types.StreamingRecognizeRequest(audio_content=content)
                            for content in audio_generator)
                responses = client.streaming_recognize(streaming_config, requests)
                listen_print_loop(responses)
        try:
            start()
        except Exception as e:
            print(e)
            self.anton.play("ExitRokuControlMode")
    
    def skip(self):
        '''Purely used to continuity so all media classes have the same function names'''
        pass

    def previous(self):
        '''Purely used to continuity so all media classes have the same function names'''
        pass
