# weather.py

import argparse
import json
import sys
from turtle import st
import style
from configparser import ConfigParser
from urllib import error, parse, request


# This is the base URL that will be used in all API calls.
BASE_WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

# Weather Condition Codes
# https://openweathermap.org/weather-conditions#Weather-Condition-Codes-2
THUNDERSTORM = range(200, 300)
DRIZZLE = range(300, 400)
RAIN = range(500, 600)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)


def _get_api_key():
    """
    The underscore here dictates that the function should be non-public.
    ######### Function Details ###########
    Fetch the API key from your configuration file.

    Expects a configuration file named "secrets.ini" with structure:

    [openweather]
   api_key=<API KEY VALUE>
    """

    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


def read_user_cli_args():
    """Handles the CLI user interactions.

    returns:
          argparse.Namespace: Populated namespace object
  """
    parser = argparse.ArgumentParser(
        description="gets weather and temperature information for a city")
    parser.add_argument(
        "city", nargs="+", type=str, help="enter the city name"
    )

    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="display the temperature in imperial units"
    )

    return parser.parse_args()


def build_weather_query(city_input, imperial=False):
    """Builds the URL for an API request to OpenWeather's weather API.

    Args:
        city_input (List[str]): Name of a city as collected by argparse
        imperial (bool): Whether or not to use imperial units for temperature

    Returns:
        str: URL formatted for a call to OpenWeather's city name endpoint
    """

    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&appid={api_key}"
    )
    return url


def get_weather_data(query_url):
    """Makes an API request to a URL and returns the data as a Python object.

    Args:
        query_url (str): URL formatted for OpenWeather's city name endpoint

    Returns:
        dict: Weather information for a specific city

    """
    try:
        response = request.urlopen(query_url)
    except error.HTTPError as http_error:
        if http_error.code == 401:  # 401 - Unauthorized
            sys.exit("Access denied.  Check your API key.")
        elif http_error.code == 404:  # 404 - Not found
            sys.exit("Can't find weather data for this city.")
        else:
            sys.exit(f"Something went wrong... ({http_error.code})")

    data = response.read()

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Couldn't read the server response.")


def display_weather_info(weather_data, imperial=False):
    """Prints formatted weather information about a city.  

        Args:
            Weather_data(dict): API response from OpenWeather by city name
            imperial (bool): whether or not to use imperial units for the temperature

        More information at https://openweather.org/current#name
    """
    city = weather_data["name"]
    weather_id = weather_data["weather"][0]["id"]
    weather_description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]
    country = weather_data["sys"]["country"]

    style.change_colour(style.REVERSE)
    print(f"{city:^{style.PADDING}}", end="")
    style.change_colour(style.RESET)

    # colour codes for different weather conditions

    if weather_id in THUNDERSTORM:
        style.change_colour(style.RED)
    elif weather_id in DRIZZLE:
        style.change_colour(style.CYAN)
    elif weather_id in RAIN:
        style.change_colour(style.BLUE)
    elif weather_id in SNOW:
        style.change_colour(style.WHITE)
    elif weather_id in ATMOSPHERE:
        style.change_colour(style.BLUE)
    elif weather_id in CLEAR:
        style.change_colour(style.YELLOW)
    elif weather_id in CLOUDY:
        style.change_colour(style.WHITE)
    else:  # In case the API adds new weather codes
        style.change_colour(style.RESET)

    print(
        f"\t{weather_description.capitalize():^{style.PADDING}}", end=" "
    )
    style.change_colour(style.RESET)

    print(f"({temperature}°{'F' if imperial else 'C'})")


if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city, user_args.imperial)
    weather_data = get_weather_data(query_url)

    display_weather_info(weather_data, user_args.imperial)
