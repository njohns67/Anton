import datetime as dt

daysArray =["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
numWords = {"mute": 0, "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, 
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12}

#Returns the number of days to add to the current day to get to the target day
def getTargetDay(day="today"):
    currentDay = dt.datetime.today().weekday()
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

def subtractTimes(time):
    t = dt.datetime.now()
    if time.hour < t.hour and time.day == t.day:
        time += dt.timedelta(days=1)
    diff = time - t
    diff = diff.total_seconds()
    print(t)
    print(time)
    print(str(int(diff)))
    return diff

def speechToTime(transcript):
    transcript = transcript.split()
    hour = 0
    minute = 0
    second = 0
    if "at" in transcript:
        atIndex = transcript.index("at")
        if ':' in transcript[atIndex+1]:
            cIndex = transcript[atIndex+1].index(':')
            hour = transcript[atIndex+1][:cIndex]
            minute = transcript[atIndex+1][cIndex+1:]
        elif len(transcript[atIndex+1]) == 3:
            hour = transcript[atIndex+1][0]
            minute = transcript[atIndex+1][1:]
        elif len(transcript[atIndex+1]) == 4:
            hour = transcript[atIndex+1][:2]
            minute = transcript[atIndex+1][2:]
        else:
            hour = transcript[atIndex+1]
        hour = wordToNum(hour)
        minute = wordToNum(minute)
        second = wordToNum(second)
        if "am" in transcript or "a.m." in transcript:
            if hour > 12:
                hour -= 12
        elif hour < 12:
            hour += 12
        time = dt.time(hour=hour, minute=minute, second=second)
        time = dt.datetime.combine(dt.datetime.now(), time)
    elif "in" in transcript:
        for x in range(len(transcript)):
            if transcript[x] == "hour" or transcript[x] == "hours":
                hour = transcript[x-1]
            elif transcript[x] == "minute" or transcript[x] == "minutes":
                minute = transcript[x-1]
            elif transcript[x] == "second" or transcript[x] == "seconds":
                second = transcript[x-1]
        hour = wordToNum(hour)
        minute = wordToNum(minute)
        second = wordToNum(second)
        time = dt.datetime.now() + dt.timedelta(hours=hour, minutes=minute, seconds=second)
    if "tomorrow" in transcript:
        time += dt.timedelta(days=1)
        return time
    dayIndex = -1
    for day in daysArray:
        try:
            dayIndex = transcript.index(day)
        except:
            continue
    if dayIndex == -1:
        return time
    addDays = getTargetDay(daysArray[dayIndex])
    time += dt.timedelta(days=addDays)
    return time

def wordToNum(word):
    if isinstance(word, int):
        return word
    try:
        word = int(word)
        return word
    except:
        try:
            word = numWords[word]
            return word
        except:
            return -1
