# Fantasy Football Monte Carlo Sim

The following program runs a Monte Carlo simulation on a 12-team fantasy football league. Every iteration simulates one season, of a certain specified number of weeks. Each season's schedule is created at random, with each team guaranteed to play eachother once. Each player's points scored per week is determined by a sample from a normal distribution which is generated for each player based on their performance last season. Their stats from last season are scraped from fantasypros.com at the beginning of each run of the program.

## Install requirements.txt

```
pip install -r /path/to/requirements.txt
```

## Set settings.json

Some things to note about settings.json:
- for best results, you want many simulation iterations (10k+)
- ensure ```weeks_per_season``` is less than 24
- the ```roster_path``` is the public export link to a Google Sheet, should not be changed unless new Google Sheet url is in the same format as the original and player names are correct
- ```num_playoff_teams``` should only take the values of [2, 4, 8] because the program's current capabilities does not support a first week bye

## Run main.py

Once you set your desired variables in settings.json, run main.py:

```python
python main.py
```
