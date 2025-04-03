from flask import Flask, render_template, jsonify
import requests
import datetime
import pytz

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import threading
import time

app = Flask(__name__)

# ✅ Set time zone to IST (India Standard Time)
ist = pytz.timezone("Asia/Kolkata")

# ✅ Replace with your OpenWeatherMap API Key
API_KEY = "4e7654d8956cabb8c0022c86c407431b"  # Store API key separately

cities = {
    "Mumbai": (19.076, 72.8777),
    "Delhi": (28.7041, 77.1025),
    "Bangalore": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),

}

aqi_history = {}  # 🔹 Stores AQI history for each city



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/climate')
def climate():
    return render_template('climate.html')

@app.route('/humidity')
def humidity():
    return render_template('humidity.html')

@app.route('/aqi')
def aqi():
    return render_template('aqi.html')

@app.route('/city/<city>')
def get_city_climate(city):
    """Fetches real-time climate predictions for the selected city."""

    # ✅ OpenWeatherMap API request
    URL = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    
    response = requests.get(URL)
    data = response.json()

    if data.get("cod") != "200":
        return jsonify({"error": f"Failed to fetch data for {city}"}), 500



    # ✅ Get temperature predictions for the next 24 hours
    timestamps, temperatures = [], []
    for forecast in data["list"][:8]:  # 8 timestamps (~24 hours with 3-hour intervals)
        forecast_time = datetime.datetime.strptime(forecast["dt_txt"], "%Y-%m-%d %H:%M:%S")  
        time_12hr = forecast_time.strftime("%I:%M %p")  # ✅ Convert to 12-hour format (AM/PM)
        
        timestamps.append(time_12hr)  
        temperatures.append(forecast["main"]["temp"])  # Temperature in °C


    return render_template("city.html", city=city, timestamps=timestamps, temperatures=temperatures)

@app.route('/humidity/<city>')
def get_city_humidity(city):
    """Fetches real-time humidity predictions for the selected city."""
    API_KEY = "4e7654d8956cabb8c0022c86c407431b"  # Your API Key
    URL = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(URL)
    data = response.json()

    if data.get("cod") != "200":
        return jsonify({"error": f"Failed to fetch data for {city}"}), 500

    # ✅ Extract humidity data for next 24 hours (every 3 hours)
    timestamps, humidity_values = [], []
    for forecast in data["list"][:8]:  
        timestamps.append(datetime.datetime.strptime(forecast["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p"))
        humidity_values.append(forecast["main"]["humidity"])

    return render_template("humidity_graph.html", city=city, timestamps=timestamps, humidity_values=humidity_values)



# Fetch air quality data
# @app.route('/aqi/<city>')
# def get_aqi(city):
#     """Fetches real-time AQI for the selected city."""
    
#     if city not in cities:
#         return jsonify({"error": "City not found"}), 404

#     lat, lon = cities[city]
#     url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
#     response = requests.get(url)
#     data = response.json()

#     if "list" in data:
#         aqi = data["list"][0]["main"]["aqi"]
#         pm25 = data["list"][0]["components"]["pm2_5"]
#         pm10 = data["list"][0]["components"]["pm10"]
#     else:
#         return jsonify({"error": f"Failed to fetch AQI for {city}"}), 500

#     # Send AQI data to the template
#     return render_template("aqi_city.html", city=city, aqi=aqi, pm25=pm25, pm10=pm10)


#new one

@app.route('/aqi/<city>')
def get_aqi(city):
    """Fetches real-time AQI for the selected city."""
    
    if city not in cities:
        return jsonify({"error": "City not found"}), 404

    lat, lon = cities[city]
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "list" in data:
        aqi = data["list"][0]["main"]["aqi"]
        pm25 = data["list"][0]["components"]["pm2_5"]
        pm10 = data["list"][0]["components"]["pm10"]
    else:
        return jsonify({"error": f"Failed to fetch AQI for {city}"}), 500

    # Pass AQI data to the template for rendering
    return render_template("aqi_city.html", city=city, aqi=aqi, pm25=pm25, pm10=pm10)


if __name__ == "__main__":
    app.run(debug=True)

