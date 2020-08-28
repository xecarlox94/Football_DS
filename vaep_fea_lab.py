from tqdm.notebook import tqdm
import numpy as np
import pandas as pd
import matplotsoccer

import warnings
warnings.filterwarnings('ignore', category=pd.io.pytables.PerformanceWarning)

    
def nice_time(row):
    minute = int((row['period_id']>=2) * 45 + (row['period_id']>=3) * 15 + 
                 (row['period_id']==4) * 15 + row['time_seconds'] // 60)
    second = int(row['time_seconds'] % 60)
    return f'{minute}m{second}s'

def action_name(row):
    return f"{row['action_id']}: {row['nice_time']} - {row['short_name']} {row['type_name']}"

def plot_actions(df_actions_to_plot):
    matplotsoccer.actions(
        location=df_actions_to_plot[['start_x', 'start_y', 'end_x', 'end_y']],
        action_type=df_actions_to_plot['type_name'],
        team=df_actions_to_plot['team_name'],
        result=df_actions_to_plot['result_name'] == 'success',
        label=df_actions_to_plot[['nice_time', 'type_name', 'short_name', 'short_team_name']],
        zoom=False,
        figsize=8
    )
    
def plot_actions_from_action_name(df_actions, action_name):
    action_id = int(action_name.split(':')[0])
    df_actions_to_plot = df_actions[action_id-3:action_id+3]
    plot_actions(df_actions_to_plot)

def add_action_type_dummies(df_actions):
    return df_actions.merge(pd.get_dummies(df_actions['type_name']), how='left', left_index=True, right_index=True)


data_dir = 'data/wy_scout/'
PITCH_LENGTH = 105
PITCH_WIDTH = 68
GOAL_X = PITCH_LENGTH
GOAL_Y = PITCH_WIDTH / 2

df_teams = pd.read_hdf(data_dir + 'spadl.h5', key='teams')
df_players = pd.read_hdf(data_dir + 'spadl.h5', key='players')
df_games = pd.read_hdf(data_dir + 'spadl.h5', key='games')

team_name_mapping = df_teams.set_index('team_id')['team_name'].to_dict()
df_games['home_team_name'] = df_games['home_team_id'].map(team_name_mapping)
df_games['away_team_name'] = df_games['away_team_id'].map(team_name_mapping)

game_id = df_games[(df_games['home_team_name'] == 'Belgium') & (df_games['away_team_name'] == 'Japan')].iloc[0]['game_id']

with pd.HDFStore(data_dir + 'spadl.h5') as spadlstore:
    df_actions = spadlstore[f'actions/game_{game_id}']
    df_actions = (
        df_actions.merge(spadlstore['actiontypes'], how='left')
        .merge(spadlstore['results'], how='left')
        .merge(spadlstore['bodyparts'], how='left')
        .merge(spadlstore['players'], how='left')
        .merge(spadlstore['teams'], how='left')
        .reset_index()
        .rename(columns={'index': 'action_id'})
    )

df_actions['nice_time'] = df_actions.apply(nice_time, axis=1)

df_actions['action_name'] = df_actions.apply(action_name, axis=1)


action_id = 145

for side in ['start', 'end']:
    key_x = f'{side}_x'
    df_actions[f'{key_x}_norm'] = df_actions[key_x] / PITCH_LENGTH
    
    key_y = f'{side}_y'
    df_actions[f'{key_y}_norm'] = df_actions[key_y] / PITCH_WIDTH


for side in ['start', 'end']:
    diff_x = GOAL_X - df_actions[f'{side}_x']
    diff_y = abs(GOAL_Y - df_actions[f'{side}_y'])
    df_actions[f'{side}_distance_to_goal'] = np.sqrt(diff_x ** 2 + diff_y ** 2)
    df_actions[f'{side}_angle_to_goal'] = np.divide(diff_x, diff_y, out=np.zeros_like(diff_x), where=(diff_y != 0))


for side in ['start', 'end']:
    df_actions['start_is penalty_box'] = ((df_actions[f'{side}_x'] > PITCH_LENGTH - 16.5) &
                                          (df_actions[f'{side}_y'] > 13.85) &
                                          (df_actions[f'{side}_y'] > PITCH_LENGTH - 13.5))


def add_distance_features(df_actions):
    df_actions['diff_x'] = df_actions['end_x'] - df_actions['start_x']
    df_actions['diff_y'] = df_actions['end_y'] - df_actions['start_y']
    
    df_actions['distance_covered'] = np.sqrt(
        (df_actions['end_x'] - df_actions['start_x']) ** 2 +
        (df_actions['end_y'] - df_actions['start_y']) ** 2 
    )


def add_time_played(df_actions):
    df_actions['time_played'] = ( df_actions['time_seconds'] +
                                 (df_actions['period_id'] >= 2) * (45 * 60) +
                                 (df_actions['period_id'] >= 3) * (15 * 60) +
                                 (df_actions['period_id'] == 4) * (15 * 60)
                                 )
    
add_distance_features(df_actions)
add_time_played(df_actions)


delays = 3
features_to_delay = ['game_id', 'period_id', 'time_seconds', 'team_id',
       'player_id', 'start_x', 'start_y', 'end_x', 'end_y', 'bodypart_id',
       'type_id', 'result_id', 'type_name', 'result_name', 'bodypart_name',
       'time_played']

def create_delayed_features(df_actions, features_to_delay, delays):
    df_delay = [df_actions[features_to_delay].shift(step).add_suffix(f'_{step}') for step in range(0, delays)]
    return pd.concat(df_delay, axis=1)

df_features = create_delayed_features(df_actions, features_to_delay, delays)


location_cols = [ f'{side}_{xy}_{delay}' for delay in reversed(range(0, delays)) for xy in ['x', 'y']for side in ['start', 'end']]
df_features[action_id:action_id+1][location_cols]


cols = [f'{col}_{delay}' for delay in reversed(range(0, delays)) for col in ['period_id', 'time_seconds', 'type_name', 'result_name', 'bodypart_name']]
df_features[action_id:action_id+1][cols]


def add_same_team(df_features, delays):
    for step in range(1, delays):
        df_features[f'team_{step}'] = df_features['team_id_0'] == df_features[f'team_id_{step}']
        
add_same_team(df_features, delays)


def invert_coordinates(df_features, delays):
    for step in range(1, delays):
        for side in ['start', 'end']:
            df_features.loc[~(df_features[f'team'])]