import speech_recognition as sr
import subprocess
import sys, os, time
import sounddevice as sd
import soundfile as sf
import parseTranscript as pT
import wave, pyaudio

length = 3.5
samplerate = 48000
channels = 1
filename = "temp.wav"
dong = "/home/pi/Anton/Sounds/dong.wav"
ding = "/home/pi/Anton/Sounds/ding.wav"
attempts = 0

testPlaying = 0

def record():
    global testPlaying
    try:
        playing = subprocess.check_output("mpc | grep -o playing", shell=True)
        os.system("mpc pause")
        testPlaying = 1
    except subprocess.CalledProcessError:
        pass
    subprocess.Popen(["play", dong])
    recording = sd.rec(int(length * samplerate), samplerate=samplerate, channels=channels)
    sd.wait()
    sf.write(filename, recording, samplerate)
    transcript = processAudio()
    if transcript == 1:
        pT.parse("Bad transcript")
        return
    pT.parse(transcript)
    if testPlaying == 1:
        os.system("mpc play")
        testPlaying = 0

def processAudio():
    global testPlaying
    subprocess.Popen(["play", ding])
    reg = sr.Recognizer()
    audio = sr.AudioFile(filename)
    with audio as source:
        audio = reg.record(source)
    try:
        transcript = reg.recognize_google(audio)
    except:
        print("Sorry, I didn't quite get that. Please try again.")
        return 1
    print(transcript)
    return transcript

def main():
    record()

if __name__ == "__main__":
    main()
