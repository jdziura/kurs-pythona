# Analysis of public transport data in Warsaw
## Quickstart
Clone repository and create a file named .env containing api key to api.um.warszawa.pl with the following content:
```bash
API_KEY={your_api_key}
```
and run `python setup.py sdist`
Now you can install package with 
```bash
pip install ./path/to/package/directory
```
## Usage
You can run bus_project.collect and bus_project.analyze independently. The command
`python -m bus_project.collect` allows to download all the necessery data for analysis:
```
usage: python -m bus_project.collect [-h] [--base] [--live]

Analyze data of bus in Warsaw.

options:
  -h, --help  show this help message and exit
  --base      Download base data of buses and stops
  --live      Download live data of buses positions
```
Running `python -m bus_project.analyze` provides functionality to perform analysis and display its insights.
```
usage: python -m bus_project.analyze[-h] [--punctuality] [--speed] [--depots] [--data_dir DATA_DIR] [--speed_limit SPEED_LIMIT]
                  [--profile]
                  [{show}]

Analyze data of buses in Warsaw.

positional arguments:
  {show}                Action to perform, show or analyze. (default: analyze)

options:
  -h, --help            show this help message and exit
  --punctuality         Analyze punctuality of buses
  --speed               Analyze speed of buses
  --depots              Analyze buses in depots
  --data_dir DATA_DIR   Path to the data directory
  --speed_limit SPEED_LIMIT
                        Speed limit for speed analysis
  --profile             Profile code execution with line_profiler
```