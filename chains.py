import statsBomb_IO as sio
import pandas as pd
import numpy as np


competition = sio.getCompetitions()[26]

match = sio.getMatches(competition).iloc[17]

team_ids = [match['home_team_home_team_id'],match['away_team_away_team_id']]

events = sio.getMatchEvents(match)

poss_chains = []
p = dict()

limit = 2000


for i, e in events.iterrows():
    type_id = e['type_id']
    team_id = e['team_id']
        
    if type_id in [35, 18, 5]: 
        continue
    
    
    if type_id == 34:
        if 'p_team' not in p:
            p['p_team'] = team_id
        p['end'] = i - 1
        poss_chains.append(p)
        
    
    if type_id == 30: # pass
        p_type = e['pass_type_id']
        p_outcome = e['pass_outcome_id']
        
        if p_type in [61, 62, 63, 65, 67]: # set piece pass
            if 'str' in p:
                p['end'] = i - 1
                poss_chains.append(p)
            
            p = dict()
            p['p_team'] = team_id
            p['str'] = i
        
        if p['p_team'] != team_id:
            p['end'] = i - 1
            poss_chains.append(p)
            p = dict()
            p['p_team'] = team_id
            p['str'] = i
        
        if 'p_team' not in p:
            p['p_team'] = team_id
            p['str'] = i
            
        if p_outcome == 9: # chain stopped
            rel_events = events[events['id'].isin(e['related_events'])]
            #print(i, 'Chained stopped')
            
            
            #print('\n', e['period'], '->', e['timestamp'])
            
            for j, evt in rel_events.iterrows():
                if j < i:
                    continue
                
                evt_type = evt['type_id']
                evt_name = evt['type_name']
                
                
                if evt_type not in [17, 42, 22, 6]: 
                    print(str(evt_type) + ': ' + evt_name)
                
                #print(str(evt_type) + ': (' + str(i) + ') ' + evt_name)
                
                r_events= set()
                if evt_type in [17, 42]:
                    r_events.add(j)
            
            continue
            
    
    if type_id == 42:
        if team_id != p['p_team']:
            print('POSITION CHANGED ERROR')
        
    
    
    # shots
    
    #if i > limit: break
