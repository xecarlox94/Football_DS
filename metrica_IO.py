import pandas as pd
import csv as csv
import scipy.signal as signal
import numpy as np

DATA_DIR = "data/metrica_sports/data"


def readMatchData(game_id, pitchDimensions):
    track_home = trackingData(game_id, "Home")
    track_away = trackingData(game_id, "Away")

    track_home = convert_to_pSize(track_home, pitchDimensions)
    track_away = convert_to_pSize(track_away, pitchDimensions)

    events = eventData(game_id)
    events = convert_to_pSize(events, pitchDimensions)
    
    home, away, events = to_single_playing_direction(track_home, track_away,events)
    
    home = calcVel(home, smothing=True, filter_='moving_average')
    away = calcVel(away, smothing=True, filter_='moving_average')

    return events, (home, away)


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
    trackFile = 'Sample_Game_%d/Sample_Game_%d_RawTrackingData_%s_Team.csv' % (game_id, game_id, team)
    file = open('{}/{}'.format(DATA_DIR, trackFile), 'r')

    fileReader = csv.reader(file)
    teamnamefull = next(fileReader)[3].lower()

    print("Reading team: %s" % teamnamefull)

    jerseys = [x for x in next(fileReader) if x != '']
    columns = next(fileReader)

    for i, j in enumerate(jerseys):
        columns[i * 2 + 3] = "{}_{}_x".format(team, j)
        columns[i * 2 + 4] = "{}_{}_y".format(team, j)

    columns[-2] = "ball_x"
    columns[-1] = "ball_y"

    tracking = pd.read_csv('{}/{}'.format(DATA_DIR, trackFile), names=columns, index_col="Frame", skiprows=3)

    return tracking


def convert_to_pSize(data, pitchDimensions):
    x_columns = [c for c in data.columns if c[-1].lower() == 'x']
    y_columns = [c for c in data.columns if c[-1].lower() == 'y']

    data[x_columns] = (data[x_columns] - 0.5) * pitchDimensions[0]
    data[y_columns] = (-1) * (data[y_columns] - 0.5) * pitchDimensions[1]

    return data


def calcVel(track_team, smothing=True, filter_='Savitsky-Golay', window=7, polyorder=1, maxspeed=12):
    rmvTrackSpeeds(track_team)

    player_ids = np.unique([c[:-2] for c in track_team.columns if c[:4] in ['Home', 'Away']])

    dt = track_team['Time [s]'].diff()

    second_half_id = track_team.Period.idxmax(2)

    raw_speed = 0

    for player in player_ids:
        vx = track_team[player + "_x"].diff() / dt
        vy = track_team[player + "_y"].diff() / dt

        if maxspeed > 0:
            raw_speed = np.sqrt( vx**2 + vy**2 )
            vx[raw_speed > maxspeed] = np.nan
            vy[raw_speed > maxspeed] = np.nan

        if smothing:
            if filter_ == 'Savitsky-Golay':
                vx.dropna(inplace=True)
                vy.dropna(inplace=True)
                
                vx.loc[:second_half_id] = signal.savgol_filter(vx.loc[:second_half_id], window_length=window, polyorder=polyorder, mode='mirror')
                vy.loc[:second_half_id] = signal.savgol_filter(vy.loc[:second_half_id], window_length=window, polyorder=polyorder, mode='mirror')

                vx.loc[second_half_id:] = signal.savgol_filter(vx.loc[second_half_id:], window_length=window, polyorder=polyorder, mode='mirror')
                vy.loc[second_half_id:] = signal.savgol_filter(vy.loc[second_half_id:], window_length=window, polyorder=polyorder, mode='mirror')

            elif filter_ == 'moving_average':
                ma_window = np.ones(window) / window
                vx.loc[:second_half_id] = np.convolve(vx.loc[:second_half_id], ma_window, mode='same')
                vy.loc[:second_half_id] = np.convolve(vy.loc[:second_half_id], ma_window, mode='same')

                vx.loc[second_half_id:] = np.convolve(vx.loc[second_half_id:], ma_window, mode='same')
                vy.loc[second_half_id:] = np.convolve(vy.loc[second_half_id:], ma_window, mode='same')

            else:
                return

        track_team[player + '_vx'] = vx
        track_team[player + '_vy'] = vy
        track_team[player + '_speed'] = raw_speed

    return track_team

def to_single_playing_direction(home, away, events):
    for data in [home, away, events]:
        second_half_idx = data.Period.idxmax(2)
        columns = [c for c in data if c[-1].lower() in ['x', 'y']]
        data.loc[second_half_idx:,columns] *= -1

    return home, away, events

def rmvTrackSpeeds(track_team):
    columns = [c for c in track_team.columns if c.split('_')[-1] in ['vx', 'vy', 'ax', 'ay', 'speed', 'acceleration']]

    return track_team.drop(columns=columns)
