import pandas as pd
import csv as csv
import scipy.signal as signal
import numpy as np

DATA_DIR = "data/metrica_sports/data"

def readMatchData(game_id):
    track_home = trackingData(game_id,"Home")
    track_away = trackingData(game_id,"Away")

    tracking = mergeTrackingData(track_home, track_away)

    events = eventData(game_id)

    return events, tracking


def eventData(game_id):
    eventFile = 'Sample_Game_%d/Sample_Game_%d_RawEventsData.csv' % (game_id, game_id)
    events = pd.read_csv('{}/{}'.format(DATA_DIR, eventFile))
    return events


def mergeTrackingData(home, away):
    home.drop(columns=['ball_x', 'ball_y'])

    home.merge(away, left_index=True, right_index=True)
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

    tracking = pd.read_csv('{}/{}'.format(DATA_DIR, trackFile), names=columns, index_col="Frame", dtype='unicode')
    return tracking


#def calcVelocities