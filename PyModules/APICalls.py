from google.cloud import texttospeech as TTS
import os
import datetime
import requests, json
import string
from urllib.parse import quote
from subprocess import Popen, PIPE


def getKey():
    with open("/home/pi/Anton/Resources/Key.txt", "r") as file:
        key = file.readline().strip()
        return key

def getForecast(self, city="Menomonee Falls", day="today"):
    key = getKey()
    day = day.lower()
    if city == "":
        city = "Menomonee Falls"
    base = "http://api.openweathermap.org/data/2.5/forecast?"
    url = base + "appid=" + key + "&q=" + city + "&units=imperial"
    response = requests.get(url)
    if(response.status_code != 200):
        tts("I couldn't find that city")
        return
    x = response.json()
    speakArr = parseWeatherResponse(x, city, day)
    speak = speakArr[0]
    speakRain = speakArr[1]
    rainBool = speakArr[2]
    self.tts(speak)
    print(speak)
    if rainBool:
        print(speakRain)
        self.tts(speakRain)

def parseWeatherResponse(response, city, day):
    tempMax = 0
    tempMin = 200
    startTime = 0
    addDays = getTargetDay(day)
    desc = response["list"][4]["weather"][0]["description"]
    if "sky" in desc:
        desc += "s"
    time = response["list"][0]["dt_txt"].split()[1][:2]
    subHours = int(int(time)/3)
    if addDays == 0:
        startTime = 0
    else:
        startTime = (addDays * 8) - subHours
    rain = [-1, -1]
    for i in range(startTime, startTime + 8):
        if response["list"][i]["main"]["temp_max"] > tempMax:
            tempMax = response["list"][i]["main"]["temp_max"]
        if response["list"][i]["main"]["temp_min"] < tempMin:
            tempMin = response["list"][i]["main"]["temp_min"]
        if "rain" in response["list"][i]["weather"][0]["description"]:
            if rain[0] == -1:
                rain[0] = i
                rain[1] = i
            else:
                rain[1] = i
            if i < 4:
                rainMorning = 1
            elif i > 3 and i < 7:
                rainDay = 1
            elif i > 6:
                rainNight = 1
    rain[0] *= 3
    rain[1] *= 3

    if rain[0] > 12:
        rain[0] = str(rain[0] - 12) + "pm"
    elif rain[0] == 12:
        rain[0] = str(rain[0]) + "pm"
    else:
        rain[0] = str(rain[0]) + "am"

    if rain[0] == 0:
        rain[0] = "12am"

    if rain[1] > 12:
        rain[1] = str(rain[1] - 12) + "pm"
    elif rain[1] == 12:
        rain[1] = str(rain[1]) + "pm"
    else:
        rain[1] = str(rain[1]) + "am"
    if rain[1] == 0:
        rain[1] = "12am"
    
    speakRain = "It will rain between " + str(rain[0]) + " and " + str(rain[1])
    speak = (city + " will have " + desc + " with a high of " + str(int(tempMax)) 
             + " and a low of " + str(int(tempMin)))
    if day == "today":
        speak += " today"
    elif day == "tomorrow":
        speak += " tomorrow"
    else:
        speak += " on " + day
    rainBool = 0
    if rain[0] != "-3am":
        rainBool = 1
    else:
        rainBool = 0
    ret = [speak, speakRain, rainBool]
    return ret

#Returns the number of days to add to the current day to get to the target day
def getTargetDay(day="today"):
    daysArray =["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    currentDay = datetime.datetime.today().weekday()
    targetDay = -1
    if day == "today":
        targetDay = currentDay
    elif day == "tomorrow":
        targetDay = currentDay + 1
        if targetDay == 7:
            targetDay = 0
    else:
        targetDay = daysArray.index(day)
    addDays = 0
    for x in range(0, 7):
        if currentDay == targetDay:
            break
        currentDay += 1
        if currentDay == 7:
            currentDay = 0
        addDays += 1
    return addDays

def askQuestion(self, question):
        url = "http://api.wolframalpha.com/v2/result?"
        skyCommaArray = ["whos", "whose", "who's", "whats", "what's", "whens", "when's", "wheres", "where's", "whys", "why's", "hows", "how's"]
        payload = {"input": question, "appid": "XR36L6-RVJQRKE6LL"}
        answerAppend = ""
        splitQuestion = question.split()
        if len(splitQuestion) < 3:
            return
        if splitQuestion[1] == "is" or splitQuestion[1] == "are":
            answer = splitQuestion[2:]
            answer = " ".join(answer) + " " + splitQuestion[1]
        elif any(x == splitQuestion[0] for x in skyCommaArray):
            answer = splitQuestion[1:]
            answer = " ".join(answer) + " is "
        else:
            try:
                Index = splitQuestion.index("is")
            except:
                Index = splitQuestion.index("are")
            answerAppend = splitQuestion[Index+2:]
            answerAppend = " ".join(answerAppend)
            answer = splitQuestion[Index+1] + " " + splitQuestion[Index]
            if splitQuestion[Index] == "are":
                answerAppend = splitQuestion[Index-1] + " " + answerAppend


        response = requests.get(url,  payload)
        if response.status_code == 501:
            print("You'll have to google that yourself")
            return -1
        answer = answer +  " " + response.text + " " + answerAppend
        prevWord = "_"
        splitAnswer = answer.split()
        for word in splitAnswer:
            if word == prevWord:
                splitAnswer.remove(word)
            prevWord = word
        answer = " ".join(splitAnswer)
        print(answer)
        self.tts(answer)

def getJoke(self):
    printable = set(string.printable)
    r = requests.get("http://icanhazdadjoke.com", headers={"Accept": "text/plain"})
    joke = "".join(i for i in r.text if ord(i)<128)
    print(joke)
    self.tts(joke, "delme", 1)

def tts(self, TEXT, file="delme", PLAY=1):
    client = TTS.TextToSpeechClient()
    sinput = TTS.types.SynthesisInput(text=TEXT)
    voice = TTS.types.VoiceSelectionParams(language_code="en-US", 
        ssml_gender=TTS.enums.SsmlVoiceGender.MALE)
    config = TTS.types.AudioConfig(audio_encoding=TTS.enums.AudioEncoding.MP3)
    response = client.synthesize_speech(sinput, voice, config)
    with open(file + ".mp3", "wb") as out:
        out.write(response.audio_content)
    if PLAY == 1:
        self.play(file)

def play(self, file):
    p = Popen(["mpg123", file + ".mp3"], stdout=PIPE, stderr=PIPE)
    self.processes.append(p)
    p.wait()
