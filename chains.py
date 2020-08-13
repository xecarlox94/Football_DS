import statsBomb_IO as sio
import pandas as pd
import numpy as np

competition = sio.getCompetitions()[25]

match = sio.getMatches(competition).iloc[24]

team_ids = [match['home_team_home_team_id'],match['away_team_away_team_id']]

events = sio.getMatchEvents(match)


class Possession:
    def __init__(self, home_team_id, away_team_id):
        self.teams_ids = (home_team_id, away_team_id)
        self.poss_chains = []
        self.set_values()

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


    def has_chain_started(self):
        return self.start != -1 and self.p_team != -1

    def is_chain_complete(self):
        return self.has_chain_started() and self.end != -1

    def is_same_team_poss(self, p_team):
        return self.p_team == p_team

    def end_chain(self, end):
        if self.has_chain_started() and self.start <= end:
            self.end = end
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
            last_poss = self.poss_chains[len(self.poss_chains) - 1]
            if last_poss['end'] < start - 1:
                last_poss['end'] = start - 1
        self.set_values(start, p_team, poss_init)

    def single_event_chain(self, event_number, p_team, poss_session=False):
        self.start_chain(event_number, p_team, poss_session)
        self.end_chain(event_number)

    def append_poss_chain(self):
        if self.is_chain_complete():
            self.poss_chains.append(
                {"start": self.start, "end": self.end, "poss_team": self.p_team, "poss_init": self.poss_init}
            )
        self.set_values()

    def dataframe(self):
        return pd.DataFrame(self.poss_chains)


possession = Possession(team_ids[0], team_ids[1])
skip = -1

for i, e in events.iterrows():
    if i <= skip:
        continue

    type_id = e['type_id']
    team_id = e['team_id']
        
    if type_id in [35, 18, 5]: 
        continue

    # SHOTS
    # add possession session to all shots from set pieces: IMPORTANT

    # other events:
    # dispossesed
    # duel
    
    # pressure means the team does not have the ball
    
    if type_id == 34: # half end
        if not possession.has_chain_started():
            continue
        possession.end_chain(i - 1)
    
    if type_id == 9:
        possession.single_event_chain(i, team_id)

    if type_id == 23: # goalkeeper
        gk_evt_type = int(e['goalkeeper_type_id'])
        if gk_evt_type == 25:
            possession.start_chain(i, team_id)
        
        if gk_evt_type == 30:
            possession.single_event_chain(i, team_id)
    
    if type_id == 10: # interception
        i_outcome_id = e['interception_outcome_id']
        if i_outcome_id not in [15, 16, 4]:
            possession.single_event_chain(i, team_id)
        else:
            possession.start_chain(i, team_id)

        
    if type_id == 2: # ball recovery
        possession.start_chain(i, team_id)
    
    if type_id == 30: # pass
        p_type = e['pass_type_id']
        p_outcome = e['pass_outcome_id']
        
        if p_type in [64, 66]:
            possession.start_chain(i, team_id)
        
        if p_type in [61, 62, 63, 65, 67]: # set piece pass
            possession.start_chain(i, team_id, poss_init=True)
        
        possession.start_chain_if_necessary(i, team_id)
        

df_poss = possession.dataframe()

df_poss['diff'] = pd.Series([df_poss.iloc[i + 1]['start'] - df_poss.iloc[i]['end'] - 1 for i in range(len(df_poss) - 1)])

df_poss['single_event_chain'] = df_poss['start'] == df_poss['end']

