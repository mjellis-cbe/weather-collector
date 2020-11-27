# -*- coding: utf-8 -*-
"""
Example runner for weather collector
"""

import argparse
import json
import os
import sys
import time
import logging

from weather_collector import __version__
from weather_collector.caller import Collector
from weather_collector.runner import SynchronousEvent

__author__ = "Matt Ellis"
__copyright__ = "Matt Ellis"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Weather collector runner")
    parser.add_argument(
        "--version",
        action="version",
        version="weather-collector {ver}".
                format(ver=__version__))
    parser.add_argument(
        '-c',
        '--config',
        dest="config",
        help="Configuration file",
        type=str,
        required=True)
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO)
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list

    Returns:
      SynchronousEvent: event runner
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting weather collector...")
    with open(args.config, 'r') as config_file:
        config = json.load(config_file)
    config_dir = os.path.dirname(args.config)
    collector = Collector(config=config)
    config = collector.load_config()

    def do_collect():
        _logger.debug('Running collector')
        collector.collect(config_dir=config_dir,
                          data_dir=config['Data Directory'])

    event = SynchronousEvent(config['Call Frequency']*60, do_collect)
    event.start()
    return event


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
