# -*- coding: utf-8 -*-
"""
Tests weather key object
"""
import unittest
from weather_collector.caller import WeatherObjects

from tests.helpers import (
    get_path_to_types,
    get_example_response,
)

__author__ = "Matt Ellis"
__copyright__ = "Matt Ellis"
__license__ = "mit"


class TestWeatherObject(unittest.TestCase):
    """Test weather object caller"""

    @classmethod
    def setUpClass(cls):
        cls.key_file = get_path_to_types()
        cls.response = get_example_response()
        cls.expected_sizes = {'daily': 8, 'hourly': 48, 'current': 1}
        cls.expected_sizes = {'daily': 8, 'hourly': 48, 'current': 1}

    def test_key_not_in_weather_object(self):
        """Test parsing response for type that is not defined"""
        obj = WeatherObjects(self.key_file)
        with self.assertRaises(KeyError):
            obj.parse_object_type(self.response, 'NotAKey')

    def test_parse_single_value(self):
        """Test parse single value in object"""
        obj = WeatherObjects(self.key_file)
        vals = [v['pressure'] for v in self.response['daily']]
        data = obj.parse_object_type(vals, 'Pressure')
        self.assertEqual(len(data['Pressure']), self.expected_sizes['daily'])

    def test_daily_temp_obj(self):
        """Test parsing daily temperature object"""
        expected_fields = ['Day Temperature',
                           'Minimum Temperature',
                           'Maximum Temperature',
                           'Night Temperature',
                           'Evening Temperature',
                           'Morning Temperature']
        obj = WeatherObjects(self.key_file)
        typ = 'OpenWeather Temperature Object'
        forecast_type = 'daily'
        in_dat = [d['temp'] for d in self.response[forecast_type]]
        data = obj.parse_object_type(in_dat, typ, key='')
        self.standard_verify(data, forecast_type, expected_fields)

    def test_parse_daily_weather(self):
        """Test parse daily weather"""
        expected_fields = ['Date/Time',
                           'Sunrise',
                           'Sunset',
                           'Temperature.Day Temperature',
                           'Temperature.Minimum Temperature',
                           'Temperature.Maximum Temperature',
                           'Temperature.Night Temperature',
                           'Temperature.Evening Temperature',
                           'Temperature.Morning Temperature',
                           'Feels Like Temperature.Day Temperature',
                           'Feels Like Temperature.Night Temperature',
                           'Feels Like Temperature.Evening Temperature',
                           'Feels Like Temperature.Morning Temperature',
                           'Pressure',
                           'Relative Humidity',
                           'Dew Point',
                           'Wind Speed',
                           'Wind Direction',
                           'Clouds',
                           'UV Index']
        obj = WeatherObjects(self.key_file)
        typ = 'OpenWeather Weather Object'
        forecast_type = 'daily'
        data = obj.parse_object_type(self.response[forecast_type], typ, key='')
        self.standard_verify(data, forecast_type, expected_fields)

    def test_parse_hourly_weather(self):
        """Test parse hourly weather"""
        expected_fields = ['Date/Time',
                           'Temperature',
                           'Feels Like Temperature',
                           'Pressure',
                           'Relative Humidity',
                           'Dew Point',
                           'Wind Speed',
                           'Wind Direction',
                           'Visibility',
                           'Clouds']
        obj = WeatherObjects(self.key_file)
        typ = 'OpenWeather Weather Object'
        forecast_type = 'hourly'
        data = obj.parse_object_type(self.response[forecast_type], typ, key='')
        self.standard_verify(data, forecast_type, expected_fields)

    def test_parse_current_weather(self):
        """Test parse current weather"""
        expected_fields = ['Date/Time',
                           'Sunrise',
                           'Sunset',
                           'Temperature',
                           'Feels Like Temperature',
                           'Pressure',
                           'Relative Humidity',
                           'Dew Point',
                           'Wind Speed',
                           'Wind Direction',
                           'Visibility',
                           'Clouds',
                           'UV Index']
        obj = WeatherObjects(self.key_file)
        typ = 'OpenWeather Weather Object'
        forecast_type = 'current'
        data = obj.parse_object_type(self.response[forecast_type], typ, key='')
        self.standard_verify(data, forecast_type, expected_fields)

    def standard_verify(self, data, forecast_type, expected_fields):
        """Standard verification function

        Args:
            data (dict): formatted return data
            forecast_type (str): Currently, hourly, daily
            expected_fields (:obj:`list` of :obj:`str`): Expected fields
        """
        size = self.expected_sizes[forecast_type]
        for fld in expected_fields:
            self.assertTrue(fld in data,
                            msg=f'Key {fld} not in formatted data')
            self.assertEqual(len(data[fld]), size,
                             msg=(f'Key {fld} has {len(data[fld])} points; '
                                  + f"expected {size}"))


if __name__ == '__main__':
    unittest.main()
