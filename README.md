# Fantasy Football Monte Carlo Sim

The following program runs a Monte Carlo simulation on a 12-team fantasy football league. Every iteration simulates one season, of a certain specified number of weeks. Each player's points scored each week is determined by a sample from a normal distribution which is generated for each player based on their performance last season. Their stats from last season are scraped from fantasypros.com at the beginning of each run of the program.

## Install requirements.txt

```
pip install -r /path/to/requirements.txt
```

## Run main.py

Once you set your desired variables in settings.json, run main.py:

```python
python main.py
```
