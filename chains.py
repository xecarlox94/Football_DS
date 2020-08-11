import statsBomb_IO as sio
import pandas as pd
import numpy as np


competition = sio.getCompetitions()[25]

match = sio.getMatches(competition).iloc[24]

team_ids = [match['home_team_home_team_id'],match['away_team_away_team_id']]

events = sio.getMatchEvents(match)



poss_chains = []
p = dict()
skip = -1

for i, e in events.iterrows():
    if i <= skip:
        continue
    
    type_id = e['type_id']
    team_id = e['team_id']
        
    if type_id in [35, 18, 5]: 
        continue
    
    if type_id == 34: # half end
        #if 'p_team' not in p:
            #p['p_team'] = team_id
        
        if 'str' not in p:
            continue
        
        # assert if the start field does not exist
        p['end'] = i - 1
        poss_chains.append(p)
        p = dict()
    
    if type_id == 9:
        p['end'] = i - 1
        poss_chains.append(p)
        p = dict()
        p['str'] = i
        p['p_team'] = team_id
        p['end'] = i
        poss_chains.append(p)
        p = dict()
        

    if type_id == 23: # goalkeepereve
        gk_evt_type = int(e['goalkeeper_type_id'])
        #print(i, gk_evt_type, e['goalkeeper_type_name'])
        
        if gk_evt_type == 25:
            if 'str' in p:
                p['end'] = i - 1
                poss_chains.append(p)
                p = dict()
            p['str'] = i
            p['p_team'] = team_id
        
        if gk_evt_type == 30:
            if 'str' not in p:
                p['str'] = i
                
            if 'p_team' not in p:
                p['p_team'] = team_id
                
            p['end'] = i
            poss_chains.append(p)
            p = dict()
    
    if type_id == 10: # interception
        if 'str' in p:
            p['end'] = i - 1
            poss_chains.append(p)
            p = dict()
        p['str'] = i
        p['p_team'] = team_id
        
        # end chain if outcome is bad
        i_outcome_id = e['interception_outcome_id']
        if i_outcome_id not in [15, 16, 4]:
            p['end'] = i
            poss_chains.append(p)
            p = dict()
        
    if type_id == 2: # ball recovery
        if 'str' in p:
            p['end'] = i - 1
            poss_chains.append(p)
        p = dict()
        p['str'] = i
        p['p_team'] = team_id
        
    
    if type_id == 30: # pass
        p_type = e['pass_type_id']
        p_outcome = e['pass_outcome_id']
        
        if p_type in [64, 66]:
            #if 'str' in p: # raise error if chain was not closed
            if 'str' in p:
                p['end'] = i - 1
                poss_chains.append(p)
            
            p = dict()
            p['str'] = i
            p['p_team'] = team_id
        
        if p_type in [61, 62, 63, 65, 67]: # set piece pass
            
            if 'str' in p:
                p['end'] = i - 1
                poss_chains.append(p)
                
            p = dict()
            p['p_team'] = team_id
            p['str'] = i
        
        if 'p_team' in p:
            if p['p_team'] != team_id:
                #assert False, 'Possession Chain Leak, line ' + str(i)
                p['end'] = i - 1
                poss_chains.append(p)
                p = dict()
                p['p_team'] = team_id
                p['str'] = i
            
            if 'p_team' not in p:
                p['p_team'] = team_id
                p['str'] = i
            
        if p_outcome in [9, 74, 75, 76]: # chain stopped
            r_evts = e['related_events']
            
            if type(r_evts) != list:
                continue
            
            rel_events = events[events['id'].isin(r_evts)]
            
            for j, evt in rel_events.iterrows():
                if j < i:
                    continue
                
                evt_type = evt['type_id']
                evt_name = evt['type_name']
                
                if evt_type in [17, 42, 21, 6, 4]:
                    if skip < j:
                        skip = j
                
                else:
                    if evt_type == 23:
                        gk_evt_type = int(evt['goalkeeper_type_id'])
                        
                        if gk_evt_type in [30, 27, 31]:
                            if skip < j:
                                skip = j
            
            p['end'] = skip
            poss_chains.append(p)
            p = dict()
        
    
    
    
    # shots
    
    #if i > limit: break

poss_chains = pd.DataFrame(poss_chains)

poss_chains['diff'] = pd.Series([poss_chains.iloc[i + 1]['str'] - poss_chains.iloc[i]['end'] - 1 for i in range(len(poss_chains) - 1)])
