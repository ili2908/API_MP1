import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKENS = {
    "Ilia Kova" : "SEKRET_TOKEN"
}

# you can get API keys for free here - https://api-ninjas.com/api/jokes
RSA_KEY = "ZAAY5D4YYNHZC7X3QEXF4R5UC"

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def getWeather(region: str, date: str):
    url_base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"    
    url = f"{url_base_url}/{region}/{date}?key={RSA_KEY}"
    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route("/content/api/v1/integration/getWeatherByDateAndLocation", methods=["POST"])
def joke_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKENS[json_data.get("requester_name")]:
        raise InvalidUsage("wrong API token", status_code=403)


    weather = getWeather(json_data.get("location"), json_data.get("date"))["days"][0];

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%d-%mT%H:%M:%SZ");

    result = {
        "requester_name": json_data.get("requester_name"),
        "location": json_data.get("location"),
        "date": json_data.get("date"),
        "timestamp": timestamp,
        "weather": {
            "temp_c": (weather["temp"]-32)*5/9,
            "wind_kph": weather["windspeed"],
            "pressure_mb":weather["pressure"],
            "humidity": weather["humidity"],
        }
    }


    return result