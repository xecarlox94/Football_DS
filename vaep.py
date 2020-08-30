from io import BytesIO
from pathlib import Path

import pandas as pd

from tqdm.notebook import tqdm

from sklearn.metrics import brier_score_loss, roc_auc_score
from xgboost import XGBClassifier

import socceraction.vaep.features as features
import socceraction.vaep.labels as labels

from socceraction.spadl.wyscout import convert_to_spadl
from socceraction.vaep.formula import value

import warnings
warnings.filterwarnings('ignore', category=pd.io.pytables.PerformanceWarning)

import os
curr_dir = os.getcwd()

data_dir = curr_dir + '/data/wy_scout/'

def read_json_file(filename):
    with open(filename, 'rb') as json_file:
        return BytesIO(json_file.read()).getvalue().decode('unicode_escape')
    
    
json_teams = read_json_file(data_dir + 'teams.json')
df_teams = pd.read_json(json_teams)
df_teams.to_hdf(data_dir + 'wyscout.h5', key='teams', mode='w')

json_players = read_json_file(data_dir + 'players.json')
df_players = pd.read_json(json_players)
df_players.to_hdf(data_dir + 'wyscout.h5', key='players', mode='a')


competitions = [
#     'England',
#     'France',
#     'Germany',
#     'Italy',
#     'Spain',
#    'European Championship',
    'World Cup'
]


dfs_matches = []
for competition in competitions:
    comp_name = competition.replace(' ', '_')
    file_matches = data_dir + f'matches_{comp_name}.json'
    json_matches = read_json_file(file_matches)
    df_matches = pd.read_json(json_matches)
    dfs_matches.append(df_matches)
df_matches = pd.concat(dfs_matches)
df_matches.to_hdf(data_dir + 'wyscout.h5', key='matches', mode='a')



for competition in competitions:
    comp_name = competition.replace(' ', '_')
    file_events = data_dir + f'events_{comp_name}.json'
    json_events = read_json_file(file_events)
    df_events = pd.read_json(json_events)
    df_events_matches = df_events.groupby('matchId', as_index=False)
    for match_id, df_events_match in df_events_matches:
        df_events_match.to_hdf(data_dir + 'wyscout.h5', key=f'events/match_{match_id}', mode='a')


convert_to_spadl(data_dir +'wyscout.h5', data_dir + 'spadl.h5')


df_games = pd.read_hdf(data_dir + 'spadl.h5', 'games')
df_actiontypes = pd.read_hdf(data_dir + 'spadl.h5', 'actiontypes')
df_bodyparts = pd.read_hdf(data_dir + 'spadl.h5', 'bodyparts')
df_results = pd.read_hdf(data_dir + 'spadl.h5', 'results')

nb_prev_actions = 3

functions_features = [
    features.actiontype_onehot,
    features.bodypart_onehot,
    features.result_onehot,
    features.goalscore,
    features.startlocation,
    features.endlocation,
    features.movement,
    features.space_delta,
    features.startpolar,
    features.endpolar,
    features.team,
    features.time_delta
]


for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    
    df_actions = pd.read_hdf(data_dir+ 'spadl.h5', f'actions/game_{game_id}')
    df_actions = (df_actions
                  .merge(df_actiontypes, how='left')
                  .merge(df_results, how='left')
                  .merge(df_bodyparts, how='left')
                  .reset_index(drop=False))
    
    dfs_gamestates = features.gamestates(df_actions, nb_prev_actions=nb_prev_actions)
    dfs_gamestates = features.play_left_to_right(dfs_gamestates, game['home_team_id'])
    
    df_features = pd.concat([function(dfs_gamestates) for function in functions_features], axis=1)
    df_features.to_hdf(data_dir + 'features.h5', f'game_{game_id}')


functions_labels = [
    labels.scores,
    labels.concedes
]

for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    
    df_actions = pd.read_hdf(data_dir+ 'spadl.h5', f'actions/game_{game_id}')
    df_actions = (df_actions
                  .merge(df_actiontypes, how='left')
                  .merge(df_results, how='left')
                  .merge(df_bodyparts, how='left')
                  .reset_index(drop=False)
                  )
    df_labels = pd.concat([function(df_actions) for function in functions_labels], axis=1)
    df_labels.to_hdf(data_dir+ 'labels.h5', f'game_{game_id}')


columns_features = features.feature_column_names(functions_features, nb_prev_actions=nb_prev_actions)


dfs_features = []
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    
    df_features = pd.read_hdf(data_dir+ 'features.h5', f'game_{game_id}')
    dfs_features.append(df_features[columns_features])
df_features = pd.concat(dfs_features).reset_index(drop=True)


columns_labels = [
    'scores',
    'concedes'
]


dfs_labels = []
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    
    df_labels = pd.read_hdf(data_dir+ 'labels.h5', key=f'game_{game_id}')
    dfs_labels.append(df_labels[columns_labels])
df_labels = pd.concat(dfs_labels).reset_index(drop=True)


models = {}
for column_label in columns_labels:
    model = XGBClassifier()
    model.fit(df_features, df_labels[column_label])
    models[column_label] = model


dfs_predictions = {}
for column_label in columns_labels:
    predictions = models[column_label].predict_proba(df_features)[:,1]
    dfs_predictions[column_label] = pd.Series(predictions)
df_predictions = pd.concat(dfs_predictions, axis=1)


dfs_game_ids = []
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    df_actions = pd.read_hdf(data_dir+ 'spadl.h5', key=f'actions/game_{game_id}')
    dfs_game_ids.append(df_actions['game_id'])
df_game_ids = pd.concat(dfs_game_ids, axis=0).astype('int').reset_index(drop=True)

df_predictions = pd.concat([df_predictions, df_game_ids], axis=1)


df_predictions_per_game = df_predictions.groupby('game_id')


for game_id, df_predictions in tqdm(df_predictions_per_game):
    df_predictions = df_predictions.reset_index(drop=True)
    df_predictions[columns_labels].to_hdf(data_dir+ 'predictions.h5', key=f'game_{game_id}')
    
    
    
df_players = pd.read_hdf(data_dir+ 'spadl.h5', 'players')
df_teams = pd.read_hdf(data_dir+ 'spadl.h5', 'teams')



dfs_values = []
for _, game in tqdm(df_games.iterrows(), total=len(df_games)):
    game_id = game['game_id']
    df_actions = pd.read_hdf(data_dir + 'spadl.h5', f'actions/game_{game_id}')
    df_actions = (df_actions
                  .merge(df_actiontypes, how='left')
                  .merge(df_results, how='left')
                  .merge(df_bodyparts, how='left')
                  .merge(df_players, how='left')
                  .merge(df_teams, how='left')
                  .reset_index(drop=True))
    
    
    df_predictions = pd.read_hdf(data_dir+ 'predictions.h5', f'game_{game_id}')
    df_values = value(df_actions, df_predictions['scores'], df_predictions['concedes'])
    
    df_all = pd.concat([df_actions, df_predictions, df_values], axis=1)
    dfs_values.append(df_all)
    
    
df_values = (pd.concat(dfs_values)
             .sort_values(['game_id', 'period_id', 'time_seconds'])
             .reset_index(drop=True))

df_values[
    ['short_name', 'scores', 'concedes', 'offensive_value', 'defensive_value', 'vaep_value']
].head(10)


df_ranking = (df_values[['player_id', 'team_name', 'short_name', 'vaep_value']]
              .groupby(['player_id', 'team_name', 'short_name'])
              .agg(vaep_count=('vaep_value', 'count'), vaep_sum=('vaep_value', 'sum'))
              .sort_values('vaep_sum', ascending=False)
              .reset_index())


df_player_games = pd.read_hdf(data_dir + 'spadl.h5', 'player_games')
df_player_games = df_player_games[df_player_games['game_id'].isin(df_games['game_id'])]


df_minutes_played = (df_player_games[['player_id', 'minutes_played']]
                     .groupby('player_id')
                     .sum()
                     .reset_index())


df_ranking_p90 = df_ranking.merge(df_minutes_played)
df_ranking_p90 = df_ranking_p90[df_ranking_p90['minutes_played'] > 90 * 10]
df_ranking_p90['vaep_ranking'] = df_ranking_p90['vaep_sum'] * 90 / df_ranking_p90['minutes_played']
df_ranking_p90 = df_ranking_p90.sort_values('vaep_ranking', ascending=False)