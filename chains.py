import statsBomb_IO as sio
import pandas as pd
import numpy as np

#competition 9 -> inter - bayern
competition = sio.getCompetitions()[26]


match = sio.getMatches(competition).iloc[17]


team_ids = [match['home_team_home_team_id'],match['away_team_away_team_id']]

events = sio.getMatchEvents(match)

limit = 120


poss_chains = []
curr_team_poss = 0
curr_chain_poss = []

for i, e in events.iterrows():
    type_id = e['type_id']
    
    if type_id in [35, 18]: 
        continue 
    
    if type_id == 30:
        pass_type = e['pass_type_id']
        
        if np.isnan(pass_type):
            print('continuing chain')
        
        if pass_type in [61, 62, 63, 65, 67]:
            print('-> start chain')
        
    elif type_id == 42:
        print('ball receipt')
        
    elif type_id == 43:
        print('carry')
    
    
    if i > limit: break