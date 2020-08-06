import statsBomb_IO as sio
import pandas as pd
import numpy as np

#competition 9 -> inter - bayern
competition = sio.getCompetitions()[26]


match = sio.getMatches(competition).iloc[17]


team_ids = [match['home_team_home_team_id'],match['away_team_away_team_id']]

events = sio.getMatchEvents(match)

limit = 200


poss_chains = []
p = dict()

for i, e in events.iterrows():
    type_id = e['type_id']
    team_id = e['team_id']
    
    if type_id in [35, 18, 5]: 
        continue 
    
    if type_id == 30: # pass
        p_type = e['pass_type_id']
        p_outcome = e['pass_outcome_id']
        
        if 'p_team' not in p:
            p['p_team'] = team_id
        elif p['p_team'] != team_id:
            p['end'] = i - 1
            poss_chains.append(p)
            p = dict()
            p['p_team'] = team_id
            p['str'] = i
        
        if np.isnan(p_type): # normal pass
            print('continuing chain')
        
        if p_type in [61, 62, 63, 65, 67]: # set piece pass
            print('-> start chain')
            p['p_team'] = team_id
            p['str'] = i
            
            # rel_events = events[events['id'] in pass_incomplete['related_events']]
            
        if p_outcome in [9, 74, 75, 76]: # chain stopped
        
    #elif type_id == 42: # ball receipt
        
    #elif type_id == 43: # ball carrying
    
    
    if i > limit: break