from google.cloud import speech_v1p1beta1 as speech
import speech_recognition as sr
import traceback
import subprocess, signal
import sys, os, time
import parseTranscript as pT
import wave, pyaudio
import audioop
import cfg
from threading import Thread
from pixel_ring import pixel_ring as pr
from gpiozero import LED
import tts

power = LED(5)
power.on()
pr.set_brightness(100)
isDead = 0
isRecording = 0
testPlaying = 0
isPlaying = 0

client = speech.SpeechClient()
length = 8
samplerate = 48000
channels = 1
width = 2
chunk = 1024
filename = "temp.wav"
dong = "/home/pi/Anton/Sounds/dong.wav"
ding = "/home/pi/Anton/Sounds/ding.wav"
rmsMin = 50000000

def lightOn():
    pr.set_color_delay(r=0, g=0, b=255, delay=.02)

def lightSuccess():
    pr.set_color(r=0, g=255, b=0)

def lightFail():
    pr.set_color(r=255, g=0, b=0)
    time.sleep(1)
    lightOff()

def lightOff():
    pr.turn_off_color_delay(delay=.02)

def getAverageRMS():
    time.sleep(5)
    global isDead
    p = pyaudio.PyAudio()
    stream = p.open(rate=samplerate, format=p.get_format_from_width(width), 
                    channels=channels, input=True, start=False)
    stream.start_stream()
    rmsData = []
    averageRms = 0
    while isDead != 1:
        global isRecording
        global isPlaying
        while isRecording != 1:
            if isPlaying:
                break
            global rmsMin
            data = stream.read(chunk)
            rms = audioop.rms(data, 4)
            rmsData.append(rms)
            if len(rmsData) > 100:
                averageRms = int(sum(rmsData)/len(rmsData))
                rmsMin = int(averageRms * 1.3)
            if len(rmsData) > 1000:
                rmsData = []
        if isRecording:
            print("Recording")
            print("rms min calculated at ", rmsMin)
            time.sleep(10)
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("Exiting thread")

def record():
    global testPlaying
    global isRecording
    isRecording = 1
    print(str(testPlaying))
    if testPlaying:
        os.system("mpc pause")
        print("Pausing music")
    proc = subprocess.Popen(["play", dong])
    cfg.processes.append(proc)
    thread = Thread(target=lightOn)
    thread.start()
    p = pyaudio.PyAudio()
    stream = p.open(rate=samplerate, format=p.get_format_from_width(width), 
                    channels=channels, input=True, start=False)
    stream.start_stream()
    frames = []
    min = sys.maxsize
    max = 0
    num = sys.maxsize
    isSet = 0
    maxi = int(samplerate/chunk*length)
    oneSecond = maxi/length
    print("rmsMin is ", str(rmsMin))
    rmsData = []
    for i in range(0, int(samplerate/chunk*length)):
        data = stream.read(chunk)
        frames.append(data)
        rms = audioop.rms(data, 4)
        rmsData.append(rms)
        if rms < min:
            min = rms
        if rms > max: 
            max = rms
        if i > oneSecond * 2.5 and rms < rmsMin and isSet == 0:
            num = i + (oneSecond * (2/3))
            isSet = 1
        if i > num and rms < rmsMin and isSet == 1:
            break
        elif i > num and rms > rmsMin and isSet == 1:
            isSet = 0
    rmsAvg = sum(rmsData)/len(rmsData)
    print("\n\nMax is: ", max, "\nMin is ", min, "\nAverage is ", rmsAvg)
    stream.stop_stream()
    stream.close()
    p.terminate()
    w = wave.open(filename, "wb")
    w.setnchannels(channels)
    w.setsampwidth(p.get_sample_size(p.get_format_from_width(width)))
    w.setframerate(samplerate)
    w.writeframes(b''.join(frames))
    w.close()
    transcript = processAudio()
    if transcript == 1:
        tts.play("/home/pi/Anton/Responses/GoodTalk")
        thread = Thread(target=lightOff)
        thread.start()
        isRecording = 0
        if testPlaying == 1:
            os.system("mpc play")
            print("Playing")
        return
    thread = Thread(target=lightSuccess)
    thread.start()
    test = pT.parse(transcript)
    if test == -1:
        thread = Thread(target=lightFail())
        thread.start()
    elif test == 2:         #Music should stay paused
        testPlaying = 0
    elif test == 3:         #Music needs to be played
        testPlaying = 1
    thread = Thread(target=lightOff)
    thread.start()
    print(testPlaying)
    if testPlaying == 1:
        os.system("mpc play")
        print("Playing")
    isRecording = 0

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
        return 1

def processAudioGoogle():
    global testPlaying
    proc = subprocess.Popen(["play", ding])
    cfg.processes.append(proc)
    with open(filename, "rb") as file:
        content = file.read()
    audio = speech.types.RecognitionAudio(content=content)
    config = speech.types.RecognitionConfig(encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=samplerate,
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

def main():
    try:
        record()
        time.sleep(1)
    except Exception as e:
        excType, excObj, excTb = sys.exc_info()
        fname = os.path.split(excTb.tb_frame.f_code.co_filename)[1]
        print(excType, fname, excTb.tb_lineno)
        traceback.print_exc()
        print(e)
        lightOff()
        for x in cfg.processes:
            x.send_signal(signal.SIGINT)
            x.wait()

