# -*- coding: utf-8 -*-
"""
Tests Collector
"""

import datetime as dt
import glob
import os
import json
import shutil
import unittest
from weather_collector.caller import (
    Collector,
    create_file_name,
    WeatherObjects,
    format_data,
)

from tests.helpers import (
    get_example_weather_config,
    get_example_response,
    get_example_unit_config,
)

__author__ = "Matt Ellis"
__copyright__ = "Matt Ellis"
__license__ = "mit"


class TestCollector(unittest.TestCase):
    """Test collector"""

    @classmethod
    def setUpClass(cls):
        cls.config = get_example_weather_config()
        cls.response = get_example_response()

    def test_get_json(self):
        """Test getting all data files"""
        collector = Collector(config=self.config)
        files = collector.get_json_files_in_dir(os.path.dirname(self.config))
        self.assertEqual(len(files), 3)

    def test_file_name_formatting(self):
        """Test file name formatting"""

        now = dt.datetime(2020, 10, 12, 6, 12, 12)
        file_name = create_file_name("Hourly_#<date>%Y_%m_%d_%H_%M#.csv", now)
        self.assertEqual(file_name, 'Hourly_2020_10_12_06_12.csv')

        file_name = create_file_name("Current_#<date>%Y_%m_%d#.csv", now)
        self.assertEqual(file_name, 'Current_2020_10_12.csv')

    def test_formatting_data(self):
        """Test formatting data"""
        obj = WeatherObjects.get_obj()

        # Hourly
        obj_type = 'OpenWeather Weather Object'
        data = obj.parse_object_type(self.response['hourly'], obj_type)
        units = get_example_unit_config()
        with open(units, 'r') as file:
            units = json.load(file)
        data = format_data(data, units)

        num_expect_items = 48
        for key, val in obj.types[obj_type]['Points'].items():
            if key != 'Date/Time':
                typ = obj.types[key]['Type']
                unit = units[typ]
                unit = unit if unit != 'Datetime' else ""
                key = f'{obj_type}.{key}#{unit}'

            if (key not in data and 'Optional' in val and val['Optional']):
                continue

            self.assertTrue(key in data, msg=f'{key} not in formatted data')
            self.assertEqual(len(data[key]), num_expect_items)

    def test_collect(self):
        """Test data collection"""
        collector = Collector(config=self.config)
        config_dir = os.path.dirname(get_example_weather_config())
        my_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(my_dir, 'output')
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)

        collector.collect(config_dir=config_dir, data_dir=data_dir)

        # Check for files
        self.assertEqual(len(glob.glob(data_dir + '/Current_*.csv')), 1)
        self.assertEqual(len(glob.glob(data_dir + '/Hourly_*.csv')), 1)
        self.assertEqual(len(glob.glob(data_dir + '/Daily_*.csv')), 1)


if __name__ == '__main__':
    unittest.main()
