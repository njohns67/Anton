import datetime as dt
from dateutil import parser
from word2number import w2n

daysArray =["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
numWords = {"mute": 0, "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, 
            "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12}
ordinalDict = {"first": 1 , "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
               "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11, "twelth": 12,
               "thirteenth": 13, "fourteenth": 14, "fifteenth": 15, "sixteenth": 16, "seventeenth": 17,
               "eighteenth": 18, "nineteenth": 19, "twentieth": 20, "twenty-first": 21, "twenty-second": 22,
               "twenty-third": 23, "twenty-fourth": 24, "twenty-fifth": 25, "twenty-sixth": 26, "twenty-seventh": 27,
               "twenty-eighth": 28, "twenty-ninth": 29, "thirtieth": 30, "thirty-first": 31}
monthsDict = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}


def getTargetDay(day="today"):
    '''Returns the number of days needed to add to the current day 
    to get to the target day. I.E. if today's Wednesday and the
    target day is Friday, it would return 2'''
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
    '''Gives the difference in seconds between the current time and a target time'''
    t = dt.datetime.now()
    if time.hour < t.hour and time.day == t.day:
        time += dt.timedelta(days=1)
    diff = time - t
    diff = diff.total_seconds()
    print(t)
    print(time)
    print(str(int(diff)))
    return diff

def speechToDate(transcript):
    '''Given any string, this function will extract a date and/or time
    from the string if there is one'''
    transcript = transcript.split()
    addHour = 0
    addMinute = 0
    addSecond = 0
    hour = dt.datetime.now().hour
    minute = dt.datetime.now().minute
    second = dt.datetime.now().second
    day = dt.datetime.now().day
    month = dt.datetime.now().month
    year = dt.datetime.now().year
    if "at" in transcript:
        atIndex = transcript.index("at")
        if ':' in transcript[atIndex+1]:
            cIndex = transcript[atIndex+1].index(':')
            hour = transcript[atIndex+1][:cIndex]
            minute = transcript[atIndex+1][cIndex+1:]
        elif len(transcript[atIndex+1]) == 3 and len(str(wordToNum(transcript[atIndex+1]))) != 3:
            hour = transcript[atIndex+1][0]
            minute = transcript[atIndex+1][1:]
        elif len(transcript[atIndex+1]) == 4 and len(str(wordToNum(transcript[atIndex+1]))) != 4:
            hour = transcript[atIndex+1][:2]
            minute = transcript[atIndex+1][2:]
        else:
            hour = transcript[atIndex+1]
            if wordToNum(transcript[atIndex+2]) != -1:
                minute = wordToNum(transcript[atIndex+2])
            else:
                minute = 0
        hour = wordToNum(hour)
        minute = wordToNum(minute)
        second = 0
        if "am" in transcript or "a.m." in transcript:
            if hour > 12:
                hour -= 12
        elif hour < 12:
            hour += 12
    elif "in" in transcript:
        for x in range(len(transcript)):
            if transcript[x] == "hour" or transcript[x] == "hours":
                addHour = transcript[x-1]
            elif transcript[x] == "minute" or transcript[x] == "minutes":
                addMinute = transcript[x-1]
            elif transcript[x] == "second" or transcript[x] == "seconds":
                addSecond = transcript[x-1]
        hour += wordToNum(addHour)
        minute += wordToNum(addMinute)
        second += wordToNum(addSecond)
    if "on" in transcript:
        ons = [i for i, hit in enumerate(transcript) if hit == "on"]
        for onIndex in ons:
            if transcript[onIndex+1] in monthsDict:
                month = monthsDict[transcript[onIndex+1]]
                day = transcript[onIndex+2]
                day = wordToNum(day)
            elif transcript[onIndex+1] == "the" and wordToNum(transcript[onIndex+2]) != -1:
                day = wordToNum(transcript[onIndex+2])
                month = monthsDict[transcript[onIndex+4]]
    if second > 60:
        minute += 1
        second -= 60
    if minute > 60:
        hour += 1
        minute -= 60
    if hour > 23:
        hour = 0
        day += 1
        if hour < dt.datetime.now().hour and day == dt.datetime.now().day:
                day += 1
    try:
        date = dt.datetime(day=day, month=month, year=year, hour=hour, minute=minute, second=second)
    except: 
        day = 1
        month += 1
        try: 
            date = dt.datetime(day=day, month=month, year=year, hour=hour, minute=minute, second=second)
        except:
            month = 1
            year += 1
            date = dt.datetime(day=day, month=month, year=year, hour=hour, minute=minute, second=second)
    if "tomorrow" in transcript:
        date += dt.timedelta(days=1)
        return date
    day = -1
    for word in transcript:
        if word in daysArray:
            day = word
    if day == -1:
        if dt.datetime.now() > date:
            return 0
        return date
    addDays = getTargetDay(day)
    date += dt.timedelta(days=addDays)
    if dt.datetime.now() > date:
        return 0
    return date

def wordToNum(word):
    '''Converts any given word to a number if at all possible'''
    try:
        return int(word)
    except:
        pass
    try:
        return numWords[word]
    except:
        pass
    try:
        return ordinalDict[word]
    except:
        pass
    try:
        return w2n.word_to_num(word)
    except:
        pass
    try:
        return w2n.word_to_num(word[:-2])
    except:
        return -1

def getDateTime(transcript):
    '''I'm not even sure if I use this but if converts ordinals to numbers (first = 1)'''
    transcript = transcript.split()
    for x in range(len(transcript)):
        try:
            transcript[x] = ordinalDict[transcript[x]]
        except:
            continue
    

