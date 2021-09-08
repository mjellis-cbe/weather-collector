# -*- coding: utf-8 -*-
"""
This contains the generic caller responsible for calling the API and returning
the results
"""

import datetime as dt
import glob
import json
import logging
import math
import os
import pytz
import pandas as pd
import requests


__author__ = "Matt Ellis"
__copyright__ = "Matt Ellis"
__license__ = "mit"

_logger = logging.getLogger(__name__)


# pylint: disable=fixme
def _set_attr_if_exist(obj, kwargs):
    """Set attributes if they exist on object

    Args:
        obj (object): An object
        kwargs (dict): A dict of key-value pairs
    """
    for key, val in kwargs.items():
        if hasattr(obj, key):
            setattr(obj, key, val)


def create_file_name(fmt_code, date):
    """Create file name from formatting code

    Args:
        fmt_code (str): Formatting code
        date (dt.datetime): Date/time
    """
    parts = fmt_code.split("#")
    for index, part in enumerate(parts):
        if part[0:6] == "<date>":
            parts[index] = date.strftime(part[6:])
    return "".join(parts)


def format_data(data, units):
    """Format data

    Args:
        data (dict): key-value layout of data. Value is list
        units (units):

    """
    # TODO: this could be included in a data processor

    types = WeatherObjects.get_obj()
    r_data = {}
    for key, val in data.items():
        obj_type = key.split(".")[-1]

        pnt_t = types.types[obj_type]["Type"]
        if pnt_t not in units:
            msg = f"Object type {pnt_t} is not found"
            _logger.error(msg)
            raise KeyError(msg)

        unit = units[pnt_t]
        # TODO: Make this a bit more generic..
        if pnt_t.lower() == "datetime":
            if unit.lower() == "utc":
                val = [dt.datetime.utcfromtimestamp(d) for d in val]
        elif unit != "":
            key += "#" + unit
        if obj_type == "Date/Time":
            key = "Date/Time"
        r_data[key] = val
    return r_data


class Caller:
    """Generic caller class responsible for calling the API and returning
    the results.

    Args:
        kwargs (dict): keyword arguments

    Attributes:
        config (Union[str, dict]): either the config file path or the
            configuration data structure
    """

    def __init__(self, **kwargs):
        self.config = None
        _set_attr_if_exist(self, kwargs)
        if self.config is None:
            _logger.error("Must set the caller configuration")

    def call_api(self):
        """Call the API.

        Returns:
            dict: If successful, this will be populated with the data from the
            API; contains key: "CallTime" and "Response"
        """
        if isinstance(self.config, str):
            with open(self.config, "r") as config_file:
                config_data = json.load(config_file)
        else:
            config_data = self.config
        if "URL" not in config_data or config_data["URL"] == "":
            msg = f"Must have a valid URL in config: {self.config}"
            _logger.error(msg)
            raise KeyError(msg)

        now = dt.datetime.now().astimezone(pytz.utc)
        try:
            output = requests.get(config_data["URL"])
        except Exception as unknown_ex:
            output = None
            _logger.warning(unknown_ex)

        # pylint: disable=protected-access
        url = config_data["URL"]
        if hasattr(output, 'status_code') and output.status_code == 200:
            name = (
                "" if "Name" not in config_data else config_data["Name"] + " "
            )
            msg = f"Successfully called {name}API: {url}"
            _logger.info(msg)
            output = {"CallTime": now, "Response": output.json()}
        else:
            # TODO: Need to deal with failures
            msg = (
                f"Failed to call API {url}\n{output.status_code}: "
                + requests.status_codes._codes[output.status_code][0]
            )
            _logger.warning(msg)
            output = None
        return output

    def failure_handler(self):
        """Handle failures."""
        # TODO: Implement failure handler?
        raise NotImplementedError("This method is not implemented")


class Collector:
    """Collector

    Args:
        config (Union[str, dict]): either the config file path or the
            configuration data structure
    """

    def __init__(self, **kwargs):
        self.config = None
        _set_attr_if_exist(self, kwargs)
        if self.config is None:
            msg = "Must set the caller configuration"
            _logger.error(msg)
            raise ValueError(msg)

    def load_config(self):
        """Load configuration. Re-loading the config allows for hot-swamping
        it at runtime.
        """
        if isinstance(self.config, dict):
            return self.config
        with open(self.config, "r") as config_file:
            return json.load(config_file)

    def get_json_files_in_dir(self, config_dir):
        """Get all the JSON files in directory.

        Args:
            config_dir (str): Path to configuration directory

        Returns:
            list: JSON files in directory (not named unit.json)
        """
        if config_dir is None:
            msg = "Must set the collection configuration directory"
            _logger.error(msg)
            raise ValueError(msg)
        _logger.debug(
            "Searching %s for JSON files associated with %s",
            config_dir,
            self.load_config()["Name"],
        )
        return [
            file
            for file in glob.glob(config_dir + "/*.json")
            if os.path.basename(file) not in ["units.json", "config.json"]
        ]

    def collect(self, config_dir, data_dir):
        """Collects data and parse

        Args:
            config_dir (str): Configuration directory
            data_dir (str): Data directory
        """
        objs = WeatherObjects.get_obj()

        # Call the API
        response = Caller(config=self.config).call_api()
        if response is None:
            return

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        with open(os.path.join(config_dir, "units.json"), "r") as file:
            units = json.load(file)

        # TODO: makes call, formats data, and saves data (too much)
        # Currently combining since JSON is
        for data_config in self.get_json_files_in_dir(config_dir):
            with open(data_config, "r") as json_file:
                data_config = json.load(json_file)

            if "Append" not in data_config:
                data_config["Append"] = False

            # Get the data
            cur_data = {}
            for attr in data_config["Data"].keys():
                if attr == "!now":
                    cur_data["Collection Time"] = response["CallTime"]
                    continue

                cur_response = response["Response"]
                for key in attr.split("."):
                    cur_response = cur_response[key]

                cur_response = objs.parse_object_type(
                    cur_response.copy(), data_config["Data"][attr]
                )
                cur_data.update(format_data(cur_response, units))

            index = cur_data["Date/Time"]
            del cur_data["Date/Time"]
            file_name = os.path.join(
                data_dir,
                create_file_name(
                    data_config["Filename"], response["CallTime"]
                ),
            )
            self.save_data(
                pd.DataFrame(index=index, data=cur_data),
                file_name,
                data_config["Append"],
            )

    def save_data(self, data, path, append):
        """Save data

        Args:
            data (:obj:`pd.DataFrame`): Data
            path (str): Path of file to save
            append (bool): Append to existing file if exists
        """
        _logger.debug("Saving data to %s", path)
        api_name = self.load_config()["Name"]
        success_msg = f"Successfully saved data from {api_name}"
        if os.path.exists(path) and append:
            # Open file and append results
            with open(path, "a") as file:
                data.to_csv(file, header=False)
            _logger.info(success_msg)
            return

        if os.path.exists(path):
            # Remove file
            _logger.warning("File %s exists!; overwriting it", path)
            os.remove(path)

        data.to_csv(path)
        _logger.info(success_msg)


class WeatherObjects:
    """Definition of weather objects

    Args:
        path (str): String to the WeatherKeys.json file

    Attributes:
        types (dict): All defined objects
    """

    def __init__(self, path):
        with open(path, "r") as json_file:
            self.types = json.load(json_file)

    def parse_object_type(self, data, obj_type, key=None):
        """Parse object type

        Args:
            data (:obj:`list` of :obj:`dict`): Message returned by the API
            obj_type (str): Type of object
            key (str): Prefix key

        Returns:
            dict: key-value pair of key and list of values
        """
        if obj_type not in self.types:
            msg = f"The key {obj_type} is not defined in the Weather types"
            _logger.error(msg)
            raise KeyError(msg)

        data = data if isinstance(data, list) else [data]
        fmt_data = {}
        if len(data) == 0:
            return fmt_data

        cur_type = self.types[obj_type]
        if key is None:
            key = obj_type

        if "Points" in cur_type:
            if not any([isinstance(d, dict) for d in data]):
                fmt_data.update({key: data})
                return fmt_data

            for obj_t, pnt in cur_type["Points"].items():
                # Could be a string or a dict with Key, Optional and/or Type
                pnt = pnt.copy() if not isinstance(pnt, str) else {"Key": pnt}
                if "Optional" not in pnt:
                    pnt["Optional"] = False

                dat = [d.get(pnt["Key"], float("nan")) for d in data]
                if not pnt["Optional"] and any(
                    [d == float("nan") for d in dat]
                ):
                    msg = f"Type {obj_type} is missing data"
                    _logger.error(msg)
                    raise ValueError(msg)

                if pnt["Optional"] and all([math.isnan(d) for d in dat]):
                    continue

                new_key = key + "." + obj_t if key != "" else obj_t
                if "Type" not in pnt or (
                    len(dat) > 0 and not isinstance(dat[0], dict)
                ):
                    pnt["Type"] = obj_t

                cur_dat = self.parse_object_type(dat, pnt["Type"], key=new_key)
                fmt_data.update(cur_dat)
        else:
            fmt_data[key] = data

        return fmt_data

    @staticmethod
    def get_obj():
        """Get a Weather object"""
        cur_path = os.path.dirname(os.path.abspath(__file__))
        wk_path = os.path.join(cur_path, "WeatherTypes.json")
        return WeatherObjects(wk_path)
