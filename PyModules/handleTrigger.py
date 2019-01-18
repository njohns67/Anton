from google.cloud import speech_v1p1beta1 as speech
import subprocess, signal
import sys, os, time
import parseTranscript as pT
import wave, pyaudio
import audioop
import cfg

client = speech.SpeechClient()
length = 8
samplerate = 48000
channels = 4
width = 2
chunk = 1024
filename = "temp.wav"
dong = "/home/pi/Anton/Sounds/dong.wav"
ding = "/home/pi/Anton/Sounds/ding.wav"
testPlaying = 0
rmsMin = 10000000

def record():
    global testPlaying
    try:
        playing = subprocess.check_output("mpc | grep -o playing", shell=True)
        os.system("mpc pause")
        testPlaying = 1
    except subprocess.CalledProcessError:
        pass
    proc = subprocess.Popen(["play", dong])
    cfg.processes.append(proc)
    p = pyaudio.PyAudio()
    stream = p.open(rate=samplerate, format=p.get_format_from_width(width), 
                    channels=channels, input=True, start=False)
    stream.start_stream()
    frames = []
    min = 10000000
    max = 0
    num = sys.maxsize
    isSet = 0
    maxi = int(samplerate/chunk*length)
    print("Num is", str(num))
    print("Max i is ", str(maxi))
    oneSecond = maxi/length
    print("One second is ", str(oneSecond))
    for i in range(0, int(samplerate/chunk*length)):
        data = stream.read(chunk)
        frames.append(data)
        rms = audioop.rms(data, 4)
        print(rms)
        print("I is ", i)
        if rms < min:
            min = rms
        if rms > max: 
            max = rms
        if i > oneSecond * 2.5 and rms < rmsMin and isSet == 0:
            print("About to break at ", i)
            num = i + (oneSecond * (2/3))
            isSet = 1
        if i > num and rms < rmsMin and isSet == 1:
            print("Breaking at ", i)
            break
        elif i > num and rms > rmsMin and isSet == 1:
            isSet = 0

    print("\n\nMax is: ", max, "\nMin is ", min)
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
        pT.parse("Bad transcript")
        return
    print(transcript)
    pT.parse(transcript)
    if testPlaying == 1:
        os.system("mpc play")
        testPlaying = 0

def processAudio():
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
    except:
        return 1

def main():
    try:
        record()
    except Exception as e:
        print(e)
        for x in cfg.processes:
            x.send_signal(signal.SIGINT)
            x.wait()

