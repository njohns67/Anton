from time import sleep
import serial, os, signal
import handleTrigger as HT
import APICalls
import tts
import subprocess
import wifiDevices
import cfg

directory = "/home/pi/Anton/Responses/"
ding = "/home/pi/Anton/Sounds/ding.wav"

todayWeatherArrays = [["todays", "weather"], ["today", "weather"], ["today's", "weather"], ["the weather in"]]
tomWeatherArrays = [["tomorrow", "weather"], ["tomorrows", "weather"], ["tomorrow's", "weather"]]
commandArray = ["light", "joke", "weather", "alarm", "play", "next", 
                "pause", "volume", "skip", "feed", "beer", "exit", "scout"]
weatherDayArray = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "today", "tomorrow"]
questionArray = ["who", "whose", "who's", "whos", 
                 "what", "what's", "whats", 
                 "when", "when's", "whens", 
                 "where", "where's", "wheres", 
                 "why", "why's", "whys",
                 "how", "how's", "hows"]

def playSound(file):
	os.system("mpg123 " + directory + file + ".mp3")

def playDingDelay():
        p = subprocess.Popen(["play", ding])
        cfg.processes.append(p)

def playDing():
    os.system("play " + ding)

def parse(transcript):
    transcript = transcript.lower()
    print(transcript)
    if not any(x in transcript for x in commandArray):
        return -1
    if "light" in transcript and "on" in transcript:
        playDing()
        wifiDevices.lightOn()

    elif "joke" in transcript:
        playDingDelay()
        APICalls.getJoke()

    elif "weather" in transcript:
        playDingDelay()
        city = ""
        transcript2 = transcript.split()
        day = ""
        try:
            index = transcript2.index("in")
            city = transcript2[index+1]
        except ValueError:
            city = ""
        both = set(weatherDayArray).intersection(transcript2)
        if len(both) == 0:
            day = "today"
        else:
            index = [weatherDayArray.index(x) for x in both]
            day = weatherDayArray[index[len(index)-1]]
        APICalls.getForecast(city, day)

    elif "alarm" in transcript or "timer" in transcript:
        playDingDelay()
        if not any(x in transcript for x in ["minutes", "seconds", "hours", "minute", "hour"]):
            playSound("BadTimer")
            return
        a, playString = transcript.split("for")
        transcript2 = transcript.split()
        nums = []
        indices = []
        letters = []
        i = 0
        for x in transcript2:
            i += 1
            try:
               nums.append(int(x))
               indices.append(i)
            except ValueError:
                continue
        if len(nums) == 0:
            playSound("BadRec")
            return
        for x in indices:
            letters.append(transcript2[x][0])
        if "and a half" in transcript or "1/2" in transcript:
            nums.append(30)
            if letters[0] == 'm':
                letters.append('s')
            else:
                letters.append('m')
        try:
            if len(nums) == 1:
                p = subprocess.Popen(["/home/pi/Anton/Resources/timer", str(nums[0]), letters[0]])
                cfg.processes.append(p)
            else:
                p = subprocess.Popen(["/home/pi/Anton/Resources/timer", str(nums[0]), letters[0], str(nums[1]), letters[1]])
                cfg.processes.append(p)
        except Exception as e:
            print(e)
            playSound("BadRec")
        tts.text2speech("I've set your timer for" + playString)

    elif "play" in transcript or "pray" in transcript:
        HT.isPlaying = 1
        playDing()
        transcript2 = transcript
        transcript = transcript.split()
        if (len(transcript) < 4 and "continue" in transcript) or "play the music" == transcript2 or "continue playing" in transcript2 or "play" == transcript2:
            print("resuming")
            return 3
        index = transcript.index("play")
        index2 = 0
        try:
            index2 = transcript.index("by")
        except ValueError:
            song = ""
            if "next" in transcript or "after this" in transcript2:
                for x in range(index+1, len(transcript)-1):
                    song += transcript[x]
                    song += " "
                os.system("mpc search title \"" + song + "\" | head -n 1 | mpc add")
                tts.text2speech("Added " + song + " to the queue")
                return 3
            else:
                for x in range(index+1, len(transcript)):
                    song += transcript[x]
                    song += " "
                os.system("mpc clear; mpc search title \"" + song + "\" | head -n 1 | mpc add")
                tts.text2speech("Playing " + song)
                return 3
        song = ""
        artist = ""
        if "next" in transcript or "after this" in transcript2:
            for x in range(index+1, index2):
                song += transcript[x]
                song += " "
            for x in range(index2+1, len(transcript)-1):
                artist += transcript[x]
                artist += " "
            print(song)
            print(artist)
            os.system("mpc search title \"" + song + "\" artist \"" + artist + "\" | head -n 1 | mpc add")
            tts.text2speech("Added " + song + " by " + artist + " to the queue")
            return 3
        else:
            for x in range(index+1, index2):
                song += transcript[x]
                song += " "
            for x in range(index2+1, len(transcript)):
                artist += transcript[x]
                artist += " "
            print(song)
            print(artist)
            os.system("mpc clear; mpc search title \"" + song + "\" artist \"" + artist + "\" | head -n 1 | mpc add")
            tts.text2speech("Playing " + song + " by " + artist)
            return 3

    elif "pause" in transcript or ("stop" in transcript and "music" in transcript):
        playDing()
        HT.isPlaying = 0
        print("Pausing music")
        return 2

    elif "volume" in transcript:
        playDing()
        if "up" in transcript:
            os.system("amixer set Master 10%+")
        elif "down" in transcript:
            os.system("amixer set Master 10%-")
        else:
            #TODO: Add "Would you like the volume up or down?" response
            return

    elif "skip" in transcript:
        playDing()
        os.system("mpc next")

    elif "feed" in transcript or "scout" in transcript:
        playDing()
        playSound("FeedingScout")
        wifiDevices.feedScout()

    elif "beer" in transcript:
        playDing()
        wifiDevices.beerMe()

    elif any(x in transcript for x in questionArray):
        APICalls.askQuestion(transcript)

    elif "exit" in transcript:
        playDing()
        playSound("Goodbye")
        for x in cfg.processes:
            x.send_signal(signal.SIGINT)
            x.wait()
        os.system("stty sane")
        exit(0)

    else:
        print("I didn't quite get that. Please try again.")
        return -1
    
