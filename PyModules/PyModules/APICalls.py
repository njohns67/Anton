import tts
import datetime
import requests, json
from urllib.parse import quote

key = "849c0f6c67a3b0abbee0abf6bb50019c"

def getTodaysForecast(city="Menomonee Falls"):
    if city == "":
        city = "Menomonee Falls"
    base = "http://api.openweathermap.org/data/2.5/weather?"
    url = base + "appid=" + key + "&q=" + quote(city) + "&units=imperial"
    response = requests.get(url)
    if(response.status_code != 200):
        tts.text2speech("I couldn't find that city")
        return
    x = response.json()
    print(x)
    speak = city + " currently has " + x["weather"][0]["description"] + " with a high of " + str(int(x["main"]["temp_max"])) + " and a low of " + str(int(x["main"]["temp_min"]))
    tts.text2speech(speak)

def getTomForecast(city="Menomonee Falls"):
    if city == "":
        city = "Menomonee Falls"
    base = "http://api.openweathermap.org/data/2.5/forecast?"
    url = base + "appid=" + key + "&q=" + city + "&units=imperial"
    response = requests.get(url)
    if(response.status_code != 200):
        tts.text2speech("I couldn't find that city")
        return
    x = response.json()
    tempMax = 0
    tempMin = 200
    desc = x["list"][4]["weather"][0]["description"]
    rain = [-1, -1]
    for i in range(0, 8):
        if x["list"][i]["main"]["temp_max"] > tempMax:
            tempMax = x["list"][i]["main"]["temp_max"]
        if x["list"][i]["main"]["temp_min"] < tempMin:
            tempMin = x["list"][i]["main"]["temp_min"]
        if "rain" in x["list"][i]["weather"][0]["description"]:
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
    speak = city + " will have " + desc + " with a high of " + str(int(tempMax)) + " and a low of " + str(int(tempMin)) + " tomorrow"
    tts.text2speech(speak)
    if rain[0] != -3:
        tts.text2speech(speakRain)

def willItRain(city="Knoxville", day="today"):
    base = "http://api.openweathermap.org/data/2.5/forecast?"
    url = base + "appid=" + key + "&q=" + city + "&units=imperial"
    response = requests.get(url)
    x = response.json()
    tempMax = 0
    tempMin = 200
    desc = x["list"][4]["weather"][0]["description"]
    rain = [-1, -1]
    for i in range(0, 8):
        if x["list"][i]["main"]["temp_max"] > tempMax:
            tempMax = x["list"][i]["main"]["temp_max"]
        if x["list"][i]["main"]["temp_min"] < tempMin:
            tempMin = x["list"][i]["main"]["temp_min"]
        if "rain" in x["list"][i]["weather"][0]["description"]:
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
    speak = "The weather in " + city + " is " + desc + " with a high of " + str(int(tempMax)) + " and a low of " + str(int(tempMin))
    tts.text2speech(speak)
    if rain[0] != "-3am":
        tts.text2speech(speakRain)

def getWeatherDate(city="Menomonee Falls", day="today"):
    day = day.lower()
    daysDict = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}
    currentDay = datetime.datetime.today().weekday()
    keys = list(daysDict.keys())
    values = list(daysDict.values())
    targetDay = -1
    if day == "today":
        targetDay = keys[values.index(currentDay)]
    else:
        targetDay = daysDict[day]
    addDays = 0
    for x in range(0, 7):
        if currentDay == targetDay:
            break
        currentDay += 1
        if currentDay == 7:
            currentDay = 0
        addDays += 1
    print(str(addDays))
    if city == "":
        city = "Menomonee Falls"
    base = "http://api.openweathermap.org/data/2.5/forecast?"
    url = base + "appid=" + key + "&q=" + city + "&units=imperial"
    response = requests.get(url)
    if(response.status_code != 200):
        tts.text2speech("I couldn't find that city")
        return
    x = response.json()
    tempMax = 0
    tempMin = 200
    desc = x["list"][4]["weather"][0]["description"]
    rain = [-1, -1]
    for i in range(addDays, addDays + 8):
        if x["list"][i]["main"]["temp_max"] > tempMax:
            tempMax = x["list"][i]["main"]["temp_max"]
        if x["list"][i]["main"]["temp_min"] < tempMin:
            tempMin = x["list"][i]["main"]["temp_min"]
        if "rain" in x["list"][i]["weather"][0]["description"]:
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
    speak = city + " will have " + desc + " with a high of " + str(int(tempMax)) + " and a low of " + str(int(tempMin)) + " on " + day
    print(speak)
    tts.text2speech(speak)
    if rain[0] != "-3am":
        print(speakRain)
        tts.text2speech(speakRain)
    
getWeatherDate("", "sunday")
