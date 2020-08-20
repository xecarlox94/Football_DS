import statsBomb_IO as sio
import pandas as pd
import numpy as np

competition = sio.getCompetitions()[0] #0 #23

match = sio.getMatches(competition).iloc[0] #0 #7

team_ids = [match['home_team_home_team_id'],match['away_team_away_team_id']]

events = sio.getMatchEvents(match)


class Possession:
    def __init__(self, home_team_id, away_team_id):
        self.teams_ids = (home_team_id, away_team_id)
        self.poss_chains = []
        self.start = -1
        self.p_team = -1
        self.poss_init = False
        self.end = -1
        
    def is_team_in_possession(self, team_id):
        return self.p_team == team_id

    def get_opposition_team_id(self, team_id):
        if self.teams_ids[0] == team_id:
            return self.teams_ids[1]
        elif self.teams_ids[1] == team_id:
            return self.teams_ids[0]
        else:
            assert False, "Wrong team_id (%d)".format(team_id)
            
    def set_values(self, start=-1, p_team=-1, poss_init=False, end=-1):
        self.start = start
        self.p_team = p_team
        self.poss_init = poss_init
        self.end = end
        
    def get_last_poss_chain(self):
        return self.poss_chains[len(self.poss_chains) - 1]

    def has_chain_started(self):
        return self.start != -1 and self.p_team != -1

    def is_chain_complete(self):
        return self.has_chain_started() and self.end != -1

    def is_same_team_poss(self, p_team):
        return self.p_team == p_team

    def merge_with_previous_chain(self, end):
        l_poss = self.get_last_poss_chain()
        l_poss['end'] = end

    def end_chain(self, end, merge_pre=False):
        if self.has_chain_started():
            if self.start <= end:
                self.end = end
        elif merge_pre:
            self.merge_with_previous_chain(end)
        self.append_poss_chain()

    def start_chain_if_necessary(self, event_number, p_team, poss_init=False):
        if not self.has_chain_started():
            self.start_chain(event_number, p_team, poss_init)
        elif not self.is_same_team_poss(p_team):
            self.end_chain(event_number - 1)
            self.start_chain(event_number, p_team, poss_init)

    def start_chain(self, start, p_team, poss_init=False):
        if self.has_chain_started():
            if self.start > start:
                self.set_values()
                return
            self.end_chain(start - 1)
        elif poss_init and len(self.poss_chains) > 1:
            last_poss = self.get_last_poss_chain()
            if last_poss['end'] < start - 1:
                last_poss['end'] = start - 1
        self.set_values(start, p_team, poss_init)

    def append_poss_chain(self):
        if self.is_chain_complete():
            self.poss_chains.append(
                {"start": self.start, "end": self.end, "poss_team": self.p_team, "poss_init": self.poss_init}
            )
        self.set_values()

    def dataframe(self):
        return pd.DataFrame(self.poss_chains)


possession = Possession(team_ids[0], team_ids[1])

for i, e in events.iterrows():

    type_id = e['type_id']
    team_id = e['team_id']
        
    if type_id in [35, 18, 5]: 
        continue

    # SHOTS
    # add possession session to all shots from set pieces: IMPORTANT

    # other events:
    # dispossesed
    # duel
    
    """
    if type_id == 40: # injury stoppage
        possession.end_chain(i, merge_pre=True)
    """
    if type_id == 14: # dribble
        possession.start_chain_if_necessary(i, team_id)
        
    if type_id == 43: # carry
        possession.start_chain_if_necessary(i, team_id)
    
    if type_id == 9: # clearance
        possession.start_chain_if_necessary(i, team_id)
        possession.end_chain(i)
        
        
    if type_id == 16: # shots
        shot_type = e['shot_type_id']
        if shot_type in [61, 62, 88, 65]:
            possession.start_chain(i, team_id, poss_init=True)
        else:
            possession.start_chain_if_necessary(i, team_id)

    if type_id == 23: # goalkeeper
        gk_evt_type = int(e['goalkeeper_type_id'])
        gk_evt_outcome = e['goalkeeper_outcome_id']
        if np.isnan(gk_evt_outcome):
            continue
        else:
            gk_evt_outcome = int(gk_evt_outcome)
            
        if gk_evt_type == 25 and gk_evt_outcome != 50:
            possession.start_chain(i, team_id)
            
        if gk_evt_type == 27 and gk_evt_outcome != 50:
            if gk_evt_outcome == 48:
                possession.single_event_chain(i, team_id)
            else:
                possession.start_chain(i, team_id)
    
    if type_id == 10: # interception
        i_outcome_id = e['interception_outcome_id']
        if i_outcome_id not in [15, 16, 4]:
            possession.start_chain_if_necessary(i, team_id)
            possession.end_chain(i)
        else:
            possession.start_chain_if_necessary(i, team_id)
            
    if type_id == 17: # pressure
        p_team = possession.get_opposition_team_id(team_id)
        possession.start_chain_if_necessary(i, p_team)
        
    if type_id == 2: # ball recovery
        possession.start_chain_if_necessary(i, team_id)
    
    if type_id == 30: # pass
        p_type = e['pass_type_id']
        p_outcome = e['pass_outcome_id']
        if p_type in [61, 62, 63, 65, 67]: # set piece pass
            possession.start_chain(i, team_id, poss_init=True)
        if p_type in [64, 66]: # interception, recovery
            possession.start_chain_if_necessary(i, team_id)
        possession.start_chain_if_necessary(i, team_id)
        
    
    if type_id == 4:
        d_outcome = e['duel_outcome_id']
        d_type = int(e['duel_type_id'])
        
        if d_type == 10:
            p_team = possession.get_opposition_team_id(team_id)
            possession.start_chain_if_necessary(i, p_team)
            continue
        
        if not np.isnan(d_outcome):
            d_outcome = int(d_outcome)
            print(d_type, d_outcome)
        else:
            print(d_type)
        
        """
        if d_type == 10:
        print(i, e['duel_type_id'])
        """
        
        if d_outcome in [4, 15, 16]:
            possession.start_chain(i, team_id)
            
        if d_outcome in [1, 13, 14]:
            p_team = possession.get_opposition_team_id(team_id)
            possession.start_chain(i, p_team)
            
    
    """
    if type_id == 22:
        is_offensive = e['foul_committed_offensive']
        
        if not is_offensive:
            p_team = team_id
        else:
            p_team = possession.get_opposition_team_id(team_id)
            
        possession.start_chain_if_necessary(i, p_team)
        
    if type_id == 21:
        is_defensive = e['foul_won_defensive']
        
        if not is_defensive:
            p_team = possession.get_opposition_team_id(team_id)
        else:
            p_team = team_id
            
        possession.start_chain_if_necessary(i, p_team)
    """  
    

df_poss = possession.dataframe()

df_poss['length'] = pd.Series([df_poss.iloc[i]['end'] - df_poss.iloc[i]['start'] for i in range(len(df_poss) - 1)])

df_poss['diff'] = pd.Series([df_poss.iloc[i + 1]['start'] - df_poss.iloc[i]['end'] - 1 for i in range(len(df_poss) - 1)])

df_poss['single_event_chain'] = df_poss['start'] == df_poss['end']


def print_leaks(df_events, df_poss):
    chain_leaks = [ (c['end'] + 1, c['diff']) for i, c in df_poss.iterrows() if c['diff'] > 0]
    for c in chain_leaks:
        for i in range(int(c[1])):
            index = c[0] + i
            print(index, df_events.iloc[index]['type_name'])
            
print_leaks(events, df_poss)
