# -*- coding: utf-8 -*-
"""
Tests Collector
"""

import os
import json

__author__ = "Matt Ellis"
__copyright__ = "Matt Ellis"
__license__ = "mit"


MY_DIR = os.path.dirname(os.path.abspath(__file__))


def get_path_to_types():
    """Get the path to WeatherTypes.json

    Returns:
        str: absolute path to WeatherTypes.json
    """
    path = '../src/weather_collector/WeatherTypes.json'
    key_file = os.path.join(MY_DIR, path)
    return os.path.abspath(key_file)


def get_example_response():
    """Get the example response path

    Returns:
        dict: Path to example weather response
    """
    response = os.path.join(MY_DIR, 'data/example_weather.json')
    with open(response, 'r') as json_file:
        return json.load(json_file)


def get_example_weather_config():
    """Get a path to an example weather configuration file

    Returns:
        str: Path of the example config file
    """
    path = '../src/weather_collector/open_weather/config.json'
    return os.path.join(MY_DIR, path)


def get_example_unit_config():
    """Get an example unit configuration"""
    path = '../src/weather_collector/open_weather/units.json'
    return os.path.join(MY_DIR, path)
