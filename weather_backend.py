# weather_backend.py
import requests
from datetime import datetime

API_KEY = "4a1e30a40f8eb0319044e48471779be9"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

def get_location():
    try:
        res = requests.get("http://ip-api.com/json/").json()
        return res['lat'], res['lon'], res['city'], res['country']
    except:
        return None, None, None, None

def get_current_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    res = requests.get(WEATHER_URL, params=params).json()

    if res.get("cod") != 200:
        return None

    return {
        "temp": res["main"]["temp"],
        "feels_like": res["main"]["feels_like"],
        "humidity": res["main"]["humidity"],
        "condition": res["weather"][0]["description"],
    }

def get_forecast(city, count=4):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    res = requests.get(FORECAST_URL, params=params).json()

    if res.get("cod") != "200":
        return []

    forecast = []
    for item in res["list"][:count]:
        time = datetime.fromtimestamp(item["dt"])
        forecast.append({
            "time": time.strftime("%I:%M %p"),
            "temp": item["main"]["temp"],
            "condition": item["weather"][0]["description"]
        })
    return forecast

