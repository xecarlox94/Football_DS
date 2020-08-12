import statsBomb_IO as sio
import pandas as pd


competition = sio.getCompetitions()[25]

match = sio.getMatches(competition).iloc[24]

team_ids = [match['home_team_home_team_id'],match['away_team_away_team_id']]

events = sio.getMatchEvents(match)


class Possession:
    def __init__(self, home_team_id, away_team_id):
        self.teams_ids = (home_team_id, away_team_id)
        self.poss_chains = []
        self.p_team = -1
        self.start = -1
        self.end = -1
        self.poss_session = False

    def get_opposition_team_id(self, team_id):
        if self.teams_ids[0] == team_id:
            return self.teams_ids[1]
        elif self.teams_ids[1] == team_id:
            return self.teams_ids[0]
        else:
            assert False, "Wrong team_id (%d)".format(team_id)

    def has_chain_started(self):
        return self.start != -1 and self.p_team != -1

    def is_same_team_poss(self, p_team):
        return self.p_team == p_team

    def end_chain(self, end, p_team):
        if self.has_chain_started():
            #assert self.start <= end, "Invalid end (%d) because it is smaller than start (%d)".format(end, self.start)
            self.end = end
            self.append_poss_chain()
        else:
            pre_poss = self.poss_chains[len(self.poss_chains) - 1]
            new_start = pre_poss['start'] + 1
            self.start_chain(new_start, p_team)
            self.add_end(end, p_team)

    def start_chain_if_necessary(self, event_number, p_team, poss_session=False):
        if self.has_chain_started() and not self.is_same_team_poss(p_team):
            self.start_chain(event_number, p_team, poss_session)
        elif not self.has_chain_started():
            self.start_chain(event_number, p_team, poss_session)

    def start_chain(self, start, p_team, poss_session=False):
        if self.has_chain_started():
            #assert self.start < start, "New chain start (%d) is illegal (previous one %d)  ".format(start, self.start)
            self.end_chain(start - 1, self.p_team)
        self.start = start
        self.p_team = p_team
        self.poss_session = poss_session

    def append_single_event_chain(self, event_number, p_team, poss_session=False):
        if self.has_chain_started():
            self.end_chain(event_number - 1, self.p_team)
        self.start_chain(event_number, p_team, poss_session)
        self.end_chain(event_number, p_team)

    def append_poss_chain(self):
        #assert self.start > self.end, "Possession start (%d) is bigger than its end (%d)".format(self.start, self.end)
        self.poss_chains.append(
            {"start": self.start, "end": self.end, "poss_team": self.p_team, "poss_session": self.poss_session}
        )
        self.p_team = -1
        self.start = -1
        self.end = -1
        self.poss_session = False

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
    
    if type_id == 34: # half end
        if not possession.has_chain_started():
            continue
        possession.end_chain(i - 1, possession.p_team)
    
    if type_id == 9:
        possession.append_single_event_chain(i, team_id)

    if type_id == 23: # goalkeeper
        gk_evt_type = int(e['goalkeeper_type_id'])
        if gk_evt_type == 25:
            possession.start_chain(i, team_id)
        
        if gk_evt_type == 30:
            possession.append_single_event_chain(i, team_id)
    
    if type_id == 10: # interception
        i_outcome_id = e['interception_outcome_id']
        if i_outcome_id not in [15, 16, 4]:
            possession.append_single_event_chain(i, team_id)
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
            possession.start_chain(i, team_id, poss_session=True)
        
        possession.start_chain_if_necessary(i, team_id)
            
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

            possession.end_chain(skip, team_id)
            
    # SHOTS
    # add possession session to all shots from set pieces: IMPORTANT
    
    #if i > limit: break

df_poss = possession.dataframe()

df_poss['diff'] = pd.Series([df_poss.iloc[i + 1]['start'] - df_poss.iloc[i]['end'] - 1 for i in range(len(df_poss) - 1)])

df_poss['single_event_chain'] = df_poss['start'] == df_poss['end']

df_poss['mistake'] = df_poss['start'] > df_poss['end']

