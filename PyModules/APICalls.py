from weather import Weather, Unit
import tts

def getTodaysForecast(city):
    if city == "":
        city = "Knoxville"
    weather = Weather(unit=Unit.FAHRENHEIT)
    location = weather.lookup_by_location(city)
    forecasts = location.forecast
    print(forecasts[0].date)
    print(forecasts[0].text)
    print(forecasts[0].high)
    print(forecasts[0].low)
    speak = "the weather in " + city + " is " + forecasts[0].text + " with a high of " + forecasts[0].high + " and a low of " + forecasts[0].low
    tts.text2speech(speak)

def getTomForecast(city):
    if city == "":
        city = "Knoxville"
    weather = Weather(unit=Unit.FAHRENHEIT)
    location = weather.lookup_by_location(city)
    forecasts = location.forecast
    print(forecasts[1].date)
    print(forecasts[1].text)
    print(forecasts[1].high)
    print(forecasts[1].low)
    speak = "the weather in " + city + " tomorrow is " + forecasts[1].text + " with a high of " + forecasts[1].high + " and a low of " + forecasts[1].low
    tts.text2speech(speak)
