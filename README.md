# weather-collector

Periodically collect the weather forecast and store it to a CSV file.

## Quick Reference

### Installation

- Requirements:
	- Python 3.8 (probably other Python 3 versions will work)
	- Python packages: `pandas` (`pyscaffold` for development)
- Setup process (inside a `virtualenv`):
```bash
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install pandas
$ python setup.py build
$ python seutp.py install
```
- If you want to install it globally, omit the first two commands

## Description

An extensible weather collector that will call various weather APIs to collect the weather forecast. The API return message is interpreted as a `JSON` string, which is converted to a `dict`.

### Defining Structure of Data Returned by an API

A few data files (i.e,. `.json` files) are used to define the data structure of a returned message. The data files are read each call implying that they be changed at run-time if, for example, the message structure changes.

#### Weather Object Types

`WeatherTypes.json` defines all known objects (i.e., shared object types across the different APIs and API specific object types). For example, the outdoor (dry-bulb) air temperature is defined as:
```python
{
	...
	"Temperature": {
		"Description": "Outdoor dry-bulb temperature",
		"Type": "Temperature"
	},
	...
}
```
where the key is the name of the object. The fields defining each object are:

- `Description`: A human readable description of the object.
- `Type`: The object type (types have associated units defined in an API's `units.json`, data validation (TODO) and filters (TODO))
- `Points`: Dictionary of points that make up the object. Each point key corresponds to the key in the returned `dict` that the data may be found. This field is optional. If this field is present, the object is assumed to be a collection of points.
	- Each point are defined by a key and string or JSON object.
	- The keys defines the object name (Temperature, Feels Like Temperature, etc.)
	- If the value is a string, then the value is a key for where to search in the response object
	- If the value is a JSON object (i.e., a `dict`), which may have keys, `Key`, `Type`, and `Optional`.
		- `Type`: Is the alternative object type. Will look for this before the object name.
		- `Key`: Reference to key in response object
		- `Optional`: Boolean to specify if the point is optional. If the point is optional and the response does not have any data for this point, then the parsed data structure will not have this point.
		- Example:
		```python
		{
			...
			"Temperature": {
				"Key": "temp"
				"Type": "Temperature Object",
			},
			...
			"UV Index": "uvi",
			...
		}
		```
		In this example, the key `temp` will be looked for in the response. If the data contained on `temp` is a group of data, it will take this data as a `Temperature Object`. Otherwise, it will assume that the data is a `Temperature` object. On the other hand, `UV Index` is found by key `uvi`. Both points are required in this example and an exception will be raised if data is not found on either of these points.

#### `config.json`

API-specific configuration. Fields:

- `URL`: API call URL
- `Name`: Name of API
- `Call Frequency`: Call frequency in minutes
- `Number of Retries`: Number of retries

#### `Units.json`

API-specific unit configuration:

- `Keys`: Category of quantity
- `Name`: Unit

#### Data File `*.json`

API-specific data files are generated for each data file (every `.json` that is not `config.json` and `units.json`). Fields:
- `Filename`: file name. The file name may include a date formatting code indicated by `#<date>date format code here#` file name may include a date formatting code indicated by `#<date>date format code here#`. For example, the filename: `Current_#<date>%Y_%m_%d#.csv` on 10/10/2020 will be read as `Current_2020_10_10.csv`. The date/times are are the time when the API is called.
- `Append`: Boolean flag; if true and the file exists, append the results to the end of it.
- `Data`: List of key-values. The key is the key to look in the returned `dict` and the value is the expected object type. Special keys:
	- `!now`: refers to the collection time (i.e., time that the API was called)

### Data Saved to a CSV File

The data is ultimately saved to a `csv` file. Specifically, from the returned data the is put into a `pandas` `DataFrame`. Ultimately, the data must be saved to:
```
<data_dir>/<APIName>/<Filename>
```

## Project TODOs

- Update how the data is saved (see section above)
- Create weather.gov API configuration
- Test weather.gov API
- How output directory should be configured?
	- Maybe, a configuration file in `~/.config`?
- If response takes longer that `x` time, stop waiting for a response. It is assumed that most APIs will return the time associated with each forecast, so this should not be an issue for determining what time the forecasts are associated with.
- Location of `WeatherTypes.json` in final config directory?
- Uninstall `weather_collector` from `virtualenv` (probably just create a fresh virtualenv
- Make sure that the call is on the clock (:00, :05, ...)
- Fix creep in call time time (i.e., it runs every 5 minutes after each task completes)
- Automated build
- Clean-up `setup.cfg`
