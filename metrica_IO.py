import pandas as pd
import csv as csv
import scipy.signal as signal
import numpy as np

DATA_DIR = "data/metrica_sports/data"

def readMatchData(game_id, pitchDimensions):
    track_home = trackingData(game_id,"Home")
    track_away = trackingData(game_id,"Away")
    
    track_home = convert_to_pSize(track_home, pitchDimensions)
    track_away = convert_to_pSize(track_away, pitchDimensions)

    events = eventData(game_id)
    events = convert_to_pSize(events, pitchDimensions)

    return events, (track_home,track_home)


def eventData(game_id):
    eventFile = 'Sample_Game_%d/Sample_Game_%d_RawEventsData.csv' % (game_id, game_id)
    events = pd.read_csv('{}/{}'.format(DATA_DIR, eventFile))
    return events


def mergeTrackingData(home, away):
    
    home = home.drop(columns=['ball_x', 'ball_y'])
    away = away.drop(columns=['Period', 'Time [s]'])
    
    home = home.merge(away, left_index=True, right_index=True)
    
    return home


def trackingData(game_id, team):
    trackFile = 'Sample_Game_%d/Sample_Game_%d_RawTrackingData_%s_Team.csv' % (game_id,game_id,team)
    file = open('{}/{}'.format(DATA_DIR, trackFile), 'r')

    fileReader = csv.reader(file)
    teamnamefull = next(fileReader)[3].lower()

    print("Reading team: %s" % teamnamefull)

    jerseys = [x for x in next(fileReader) if x != '']
    columns = next(fileReader)

    for i,j in enumerate(jerseys):
        columns[i * 2 + 3] = "{}_{}_x".format(team, j)
        columns[i * 2 + 4] = "{}_{}_y".format(team, j)
        
    columns[-2] = "ball_x"
    columns[-1] = "ball_y"

    tracking = pd.read_csv('{}/{}'.format(DATA_DIR, trackFile), names=columns, index_col="Frame", skiprows=3)
    tracking = rmvTrackSpeeds(tracking)
    
    return tracking


def convert_to_pSize(data, pitchDimensions):
    x_columns = [ c for c in data.columns if c[-1].lower() == 'x']
    y_columns = [ c for c in data.columns if c[-1].lower() == 'y']

    data[x_columns] = data[x_columns] * pitchDimensions[0]
    data[y_columns] = data[y_columns] * pitchDimensions[1]

    return data


def rmvTrackSpeeds(track_team):
    columns = [c for c in track_team.columns if c.split('_')[-1] in ['vx','vy','ax','ay','speed','acceleration']]
    
    return track_team.drop(columns=columns)
    

def calcVelocities(track_team, smothing=True, filter_='Savitsky-Golay', window=7, polyorder=1, maxspeed=12):
    
    return track_team
