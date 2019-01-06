from time import sleep
import serial, os
import handleTrigger as HT
import getJoke as joke
import APICalls
import tts
import subprocess
try:
    s = serial.Serial(port="/dev/ttyUSB0", baudrate=9600)
except:
    print("No serial available")
directory = "/home/pi/Anton/Responses/"
todayWeatherArrays = [["todays", "weather"], ["today", "weather"], ["today's", "weather"], ["the weather in"]]
tomWeatherArrays = [["tomorrow", "weather"], ["tomorrows", "weather"], ["tomorrow's", "weather"]]

def playSound(file):
	os.system("mpg123 " + directory + file + ".mp3")

def parse(transcript):
    if "on the red" in transcript:
        s.write(b"1")
        playSound("RedLightOn")

    elif "off the red" in transcript:
        s.write(b"0")
        playSound("RedLightOff")

    elif "on the green" in transcript:
        s.write(b"2")
        playSound("GreenLightOn")

    elif "off the green" in transcript:
        s.write(b"3")
        playSound("GreenLightOff")

    elif "on both" in transcript or "on the lights" in transcript:
        s.write(b"2")
        s.write(b"1")
        playSound("BothLightsOn")

    elif "off both" in transcript or "off the lights" in transcript:
        s.write(b"0")
        s.write(b"3")
        playSound("BothLightsOff")

    elif "joke" in transcript:
        joke.play()

    elif "weather" in transcript:
        test = 0
        city = ""
        transcript2 = transcript.split()
        try:
            index = transcript2.index("in")
            city = transcript2[index+1]
        except ValueError:
            city = ""
        for x in todayWeatherArrays:
            if all(y in transcript for y in x):
                test = 1
                break
        if test == 1 and not any(x in transcript for x in ["tomorrow", "tomorrows", "tomorrow's"]):
            APICalls.getTodaysForecast(city)
        else:
            for x in tomWeatherArrays:
                if all(y in transcript for y in x):
                    test = 2
                    break
        if test == 2:
            APICalls.getTomForecast(city)
    elif "alarm" in transcript or "timer" in transcript:
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
            else:
                p = subprocess.Popen(["/home/pi/Anton/Resources/timer", str(nums[0]), letters[0], str(nums[1]), letters[1]])
        except Exception as e:
            print(e)
            playSound("BadRec")
        tts.text2speech("I've set your timer for" + playString)

    elif "play" in transcript:
        transcript = transcript.split()
        index = transcript.index("play")
        index2 = transcript.index("by")
        song = ""
        artist = ""
        for x in range(index+1, index2):
            song += transcript[x]
            song += " "
        for x in range(index2+1, len(transcript)):
            artist += transcript[x]
            artist += " "
        print(song)
        print(artist)
        os.system("mpc clear; mpc search title \"" + song + "\" artist \"" + artist + "\" | mpc add; mpc play")

    elif "pause" in transcript:
        os.system("mpc pause")

    elif "volume" in transcript:
        if "up" in transcript:
            os.system("amixer set Master 10%+")
        elif "down" in transcript:
            os.system("amixer set Master 10%-")
        else:
            #TODO: Add "Would you like the volume up or down?" response
            return


    elif "exit" in transcript:
        playSound("Goodbye")
        exit(0)

    else:
        print("I didn't quite get that. Please try again.")
        playSound("BadRec")
    
