from google.cloud import speech_v1p1beta1 as speech
import speech_recognition as sr
import traceback
import subprocess, signal
import sys, os, time
import wave, pyaudio
import audioop
from threading import Thread
from pixel_ring import pixel_ring as pr
from gpiozero import LED


client = speech.SpeechClient()
filename = "temp.wav"

def getAverageRMS(self):
    time.sleep(5)
    p = pyaudio.PyAudio()
    stream = p.open(rate=self.recordingInfo["samplerate"], 
                    format=p.get_format_from_width(self.recordingInfo["width"]), 
                    channels=self.recordingInfo["channels"], input=True, start=False)
    stream.start_stream()
    rmsData = []
    averageRms = 0
    while self.isDead != 1:
        while self.isRecording != 1:
            if self.isPlaying:
                break
            data = stream.read(self.recordingInfo["chunk"])
            rms = audioop.rms(data, 4)
            rmsData.append(rms)
            if len(rmsData) > 100:
                averageRms = int(sum(rmsData)/len(rmsData))
                self.recordingInfo["minRMS"] = int(averageRms * 1.3)
            if len(rmsData) > 1000:
                rmsData = []
        if self.isRecording:
            print("Recording")
            print("rms min calculated at ", self.recordingInfo["minRMS"])
            time.sleep(10)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Exiting thread")

def record(self):
    proc = subprocess.Popen(["play", self.filePaths["dong"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    self.lightOn()
    self.processes.append(proc)
    p = pyaudio.PyAudio()
    stream = p.open(rate=self.recordingInfo["samplerate"], format=p.get_format_from_width(self.recordingInfo["width"]), 
                    channels=self.recordingInfo["channels"], input=True, start=False)
    stream.start_stream()
    frames = []
    min = sys.maxsize
    max = 0
    num = sys.maxsize
    isSet = 0
    maxi = int(self.recordingInfo["samplerate"]/self.recordingInfo["chunk"]*self.recordingInfo["length"])
    oneSecond = maxi/self.recordingInfo["length"]
    print("rmsMin is ", str(self.recordingInfo["minRMS"]))
    rmsData = []
    for i in range(0, int(self.recordingInfo["samplerate"]/self.recordingInfo["chunk"]*self.recordingInfo["length"])):
        data = stream.read(self.recordingInfo["chunk"])
        frames.append(data)
        rms = audioop.rms(data, 4)
        rmsData.append(rms)
        if rms < min:
            min = rms
        if rms > max: 
            max = rms
        if i > oneSecond * 2.5 and rms < self.recordingInfo["minRMS"] and isSet == 0:
            num = i + (oneSecond * (2/3))
            isSet = 1
        if i > num and rms < self.recordingInfo["minRMS"] and isSet == 1:
            break
        elif i > num and rms > self.recordingInfo["minRMS"] and isSet == 1:
            isSet = 0
    rmsAvg = sum(rmsData)/len(rmsData)
    print("\n\nMax is: ", max, "\nMin is ", min, "\nAverage is ", rmsAvg)
    stream.stop_stream()
    stream.close()
    p.terminate()
    w = wave.open(filename, "wb")
    w.setnchannels(self.recordingInfo["channels"])
    w.setsampwidth(p.get_sample_size(p.get_format_from_width(self.recordingInfo["width"])))
    w.setframerate(self.recordingInfo["samplerate"])
    w.writeframes(b''.join(frames))
    w.close()
    transcript = processAudio()
    if transcript == -1:
        self.lightFail()
        #self.play("/home/pi/Anton/Responses/GoodTalk")
        with open("log.txt", "a") as f:
            f.write("No transcript\n")
        self.isRecording = 0
        return -1
    return transcript

def processAudio():
    reg = sr.Recognizer()
    audio = sr.AudioFile(filename)
    with audio as source:
        audio = reg.record(source)
    try: 
        transcript = reg.recognize_google(audio)
        return transcript
    except Exception as e:
        print("No transcript")
        return -1

def processAudioGoogle():
    proc = subprocess.Popen(["play", self.filePaths["ding"]])
    self.processes.append(proc)
    with open(filename, "rb") as file:
        content = file.read()
    audio = speech.types.RecognitionAudio(content=content)
    config = speech.types.RecognitionConfig(encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=self.recordingInfo["samplerate"],
            language_code="en-US",
            audio_channel_count=4,
            enable_separate_recognition_per_channel=False)
    try:
        response = client.recognize(config, audio)
        transcript = response.results[0].alternatives[0].transcript
        return transcript
    except Exception as e:
        print(e)
        return 1

def main(self):
    try:
        return record(self)
    except Exception as e:
        self.isRecording = 0
        excType, excObj, excTb = sys.exc_info()
        fname = os.path.split(excTb.tb_frame.f_code.co_filename)[1]
        print(excType, fname, excTb.tb_lineno)
        traceback.print_exc()
        print(e)
        self.lightOff()
        for x in self.processes:
            x.send_signal(signal.SIGINT)
            x.wait()

