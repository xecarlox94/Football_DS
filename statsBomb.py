#import numpy as np
#import pandas as pd
#import os
import json

main_dir = "data/sports_bomb/data/"
events_dir = main_dir + "events/"
lineups_dir = main_dir + "lineups/"
matches_dir = main_dir + "matches/"
competitions_fileUrl = main_dir + "competitions.json"

def getCompetitions():
    with open(competitions_fileUrl) as f:
        competitions = json.load(f)
    return competitions

def getMatches(competition):
    matchesFile_url = matches_dir + str(competition['competition_id']) + "/" + str(competition['season_id']) + ".json"
    with open(matchesFile_url, "r", encoding="utf-8") as f:
        matches = json.load(f)
    return matches

def getMatchLineup(match):
    lineupFile_url = lineups_dir + str(match['match_id']) + ".json"
    with open(lineupFile_url, "r", encoding="utf-8") as f:
        lineup = json.load(f)
    return lineup

def getMatchEvents(match):
    eventsFile_url = events_dir + str(match['match_id']) + ".json"
    with open(eventsFile_url, "r", encoding="utf-8") as f:
        events = json.load(f)
    return events

competitions = getCompetitions()

matches = getMatches(competitions[26])

match = matches[27]

lineup = getMatchLineup(match)

events = getMatchEvents(match)



