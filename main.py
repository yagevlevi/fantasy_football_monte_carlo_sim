import pandas as pd
from utils import Season, Team, Player
import json
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import ast
from typing import Tuple

def load_season_settings():
    with open('settings.json') as json_file:
        settings = json.load(json_file)

    num_simulations = int(settings['num_simulations'])
    weeks_per_season = int(settings['weeks_per_season'])
    roster_path = settings['roster_path']
    num_playoff_teams = int(settings['num_playoff_teams'])

    return num_simulations, weeks_per_season, roster_path, num_playoff_teams

def create_player_code(player_name : str) -> str:
    player_name_list = player_name.split(' ', 1)
    first_name_code = player_name_list[0].replace('.', '').replace('-', '').replace("'", '').lower()
    last_name_code = player_name_list[1].replace('.', '').replace(' ', '').lower()

    with open('player_code_exceptions.json') as json_file:
        exceptions = json.load(json_file)

    if player_name in exceptions.keys():
        return first_name_code + '-' + last_name_code + '-' + exceptions[player_name]
    else:
        return first_name_code + '-' + last_name_code


def scrape_player_stats(player_name : str) -> Tuple[list, dict]:
    player_code = create_player_code(player_name)
    print('scraping data for {}'.format(player_name))
    url = 'https://www.fantasypros.com/nfl/games/{}.php?season=2023'.format(player_code)
    response = requests.get(url)
            
    if response.status_code != 200:
        print(response.status_code)
        raise Exception(f'Failed to retrieve data for {player_name}')

    soup = BeautifulSoup(response.text, 'html.parser')

    stats_table = soup.find('table', class_='table table-bordered')
    df = pd.read_html(str(stats_table))[0].droplevel(0, axis=1)
    df.drop(df.tail(1).index,inplace=True)
    df = df.drop(df[df['Points'] == 'BYE Week'].index)
    df = df.drop(df[df['Points'] == '-'].index)
    df['Points'] = pd.to_numeric(df['Points'])

    mean = df['Points'].mean()
    std = df['Points'].std()

    print('scraped data successfully for {}'.format(player_name))
    print()
        
    return list(df['Points']), {'mean': mean, 'std_dev': std}

def load_rosters_from_excel(file_path : str) -> dict:
    spreadsheet_id = file_path.split('/d/')[1].split('/edit')[0]
    excel_url = 'https://docs.google.com/spreadsheets/d/{}/export?format=xlsx'.format(spreadsheet_id)
    xls = pd.ExcelFile(excel_url)
    teams = {}
            
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name)
        players = []
        for i, row in df.iterrows():
            name = row['player_name']
            point_log, stats = scrape_player_stats(name)
            players.append(Player(name, stats, point_log))
        teams[sheet_name] = Team(sheet_name, players)
            
    return teams

def average_standings(all_standings):
    team_rankings = {}
    total_lists = len(all_standings)

    for season in all_standings:
        for i, team in enumerate(season):
            if team not in team_rankings:
                team_rankings[team] = [i]
            team_rankings[team].append(i)

    average_rankings = {}
    for team, rankings in team_rankings.items():
        average_rankings[team] = sum(rankings) / total_lists

    return average_rankings

def add_to_dict(bracket_dict : dict, bracket_to_add : str):
    if bracket_to_add in bracket_dict:
        bracket_dict[bracket_to_add] += 1
    else:
        bracket_dict[bracket_to_add] = 1

def print_top_brackets(top_three_brackets : list) -> None:
    bracket_num = 1
    for bracket in top_three_brackets:
        print('#' + str(bracket_num) + ' Bracket')
        bracket_list = ast.literal_eval(bracket)
        for i in range(len(bracket_list)):
            print(bracket_list[i][0] + ':', bracket_list[i][1])
        bracket_num += 1
        print()

def top_brackets_to_excel(top_three_brackets : list, file_path : str) -> None:
    brackets = [ast.literal_eval(bracket) for bracket in top_three_brackets]
    round_names = [x[0] for x in brackets[0]]
    df = pd.DataFrame(columns = ['bracket_number'] + round_names)
    idx = 0
    for i in range (len(brackets)):
        row = [i + 1]
        for j in range(len(brackets[i])):
            row.append(str(brackets[i][j][1]))
        df.loc[idx] = row
        idx += 1

    # spreadsheet_id = file_path.split('/d/')[1].split('/edit')[0]
    # excel_url = 'https://docs.google.com/spreadsheets/d/{}/export?format=xlsx'.format(spreadsheet_id)
    # with pd.ExcelWriter(excel_url, engine='openpyxl', mode='a') as writer:
    #     df.to_excel(writer, sheet_name='top_three_brackets', index=False)

    df.to_csv('top_brackets.csv')
    


def main():
    NUM_SIMULATIONS, WEEKS_PER_SEASON, ROSTER_PATH, NUM_PLAYOFF_TEAMS = load_season_settings()

    teams = load_rosters_from_excel(ROSTER_PATH)
    playoff_brackets = dict()

    for i in range(NUM_SIMULATIONS):
        season = Season(teams, WEEKS_PER_SEASON, NUM_PLAYOFF_TEAMS)
        curr_playoff_bracket = season.get_results()
        add_to_dict(playoff_brackets, str(curr_playoff_bracket))

    playoff_brackets = OrderedDict(sorted(playoff_brackets.items(), key=lambda team: team[1]))
    top_brackets = [bracket for bracket in list(playoff_brackets.keys())[:3]]
    print_top_brackets(top_brackets)

    print('number of different brackets simulated:', len(playoff_brackets))

    top_brackets_to_excel(top_brackets, ROSTER_PATH)

if __name__ == '__main__':
    main()

