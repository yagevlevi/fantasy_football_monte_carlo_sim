import pandas as pd
import numpy as np
import random
from collections import OrderedDict
from typing import Tuple
import statistics
import random

class Player:
    def __init__(self, name : str, stats : dict, points_log : list):
        self.name = name
        self.stats = stats
        self.points_log = points_log
    
    def simulate_performance(self) -> float:
        sample = np.random.normal(self.stats['mean'], self.stats['std_dev'])
        # self.points_log.append(sample)
        # self.stats['mean'] = statistics.mean(self.points_log)
        # self.stats['std_dev'] = statistics.stdev(self.points_log)
        return sample

class Team:
    def __init__(self, name : str, roster : list):
        self.name = name
        self.roster = roster

    def simulate_week(self) -> float:
        return sum(player.simulate_performance() for player in self.roster)

class Season:
    def __init__(self, teams : dict, num_weeks : int, num_playoff_teams : int):
        self.teams = teams
        self.schedule = self.create_schedule(num_weeks)
        self.standings = dict.fromkeys(list(self.teams.keys()))
        self.num_weeks = num_weeks
        assert self.num_weeks < 2 * len(teams)
        self.num_playoff_teams = num_playoff_teams
        assert self.num_playoff_teams in [2, 4, 8]
        self.playoff_bracket = []
    
    @staticmethod
    def get_team_points(team : Team) -> float:
        roster_points_scored = [x.simulate_performance() for x in team.roster]
        return sum(roster_points_scored)
    
    def create_schedule(self, num_weeks : int) -> list:
        team_names = list(self.teams.keys())
        schedule = []

        for round_num in range(len(team_names) - 1):
            round_matches = []
            for i in range(len(team_names) // 2):
                match = (team_names[i], team_names[len(team_names) - 1 - i])
                round_matches.append(match)

            schedule.append(round_matches)

            team_names.insert(1, team_names.pop())
        
        remaining_weeks = num_weeks % len(schedule)
        schedule += schedule[:remaining_weeks]
        random.shuffle(schedule)

        return schedule
        
    def play_matchup(self, team1 : Team, team2 : Team) -> list:
        team1_points = self.get_team_points(team1)
        team2_points = self.get_team_points(team2)

        if team1_points > team2_points:
            return [team1, team2]
        elif team2_points > team1_points:
            return [team2, team1]
        else:
            toss = random.randint(0, 1)
            if toss == 1:
                return [team1, team2]
            else:
                return [team2, team1]

    def add_win_to_standings(self, team_name : str) -> None:
        if self.standings[team_name] == None:
            self.standings[team_name] = [1, 0]
        else:
            self.standings[team_name][0] += 1

    def add_loss_to_standings(self, team_name : str) -> None:
        if self.standings[team_name] == None:
            self.standings[team_name] = [0, 1]
        else:
            self.standings[team_name][1] += 1

    def update_standings(self, winner : Team, loser : Team) -> None:
        self.add_win_to_standings(winner.name)
        self.add_loss_to_standings(loser.name)

    def create_playoff_round(self, playoff_teams, round_name):
        if len(playoff_teams) == 1:
            playoff_round = ['champion', playoff_teams]
            self.playoff_bracket.append(playoff_round)
        else:
            playoff_round = [round_name]
            matchups = []
            idx = 0
            offset = 1
            for i in range (len(playoff_teams) // 2):
                matchups.append([playoff_teams[idx], playoff_teams[idx-offset]])
                idx += 1
                offset += 2
            playoff_round.append(matchups)
            self.playoff_bracket.append(playoff_round)

    def simulate_schedule(self) -> None:
        for week in self.schedule:
            for matchup in week:
                team1 = self.teams[matchup[0]]
                team2 = self.teams[matchup[1]]
                winner, loser = self.play_matchup(team1, team2)
                self.update_standings(winner, loser)

        self.standings = OrderedDict(sorted(self.standings.items(), key=lambda team_record: team_record[1][0], reverse=True))
        standings_team_names = list(self.standings.keys())
        round_name = 'first_round'
        if len(standings_team_names[:self.num_playoff_teams]) == 4:
                round_name = 'semi_final'
        elif len(standings_team_names[:self.num_playoff_teams]) == 2:
                round_name = 'final'
        self.create_playoff_round(standings_team_names[:self.num_playoff_teams], round_name)

    def simulate_playoffs(self):
        if self.playoff_bracket == []:
            print("No playoff bracket")
            return
        for i in range(self.num_playoff_teams // 2):
            if self.playoff_bracket[i][0] == 'champion':
                return
            curr_round = self.playoff_bracket[i][1]
            winners = []
            for matchup in curr_round:
                team1 = self.teams[matchup[0]]
                team2 = self.teams[matchup[1]]
                winner, loser = self.play_matchup(team1, team2)
                winners.append(winner.name)
            if len(winners) == 4:
                round_name = 'semi_final'
            elif len(winners) == 2:
                round_name = 'final'
            self.create_playoff_round(winners, round_name)

    def get_results(self) -> list:
        self.simulate_schedule()
        self.simulate_playoffs()
        return self.playoff_bracket
