import statsBomb_IO as sio
import pandas as pd
import numpy as np


competition = sio.getCompetitions()[9]
match = sio.getMatches(competition)[0]

lineups = sio.getMatchLineups(match)
events = sio.getMatchEvents(match)

events = pd.json_normalize(events, sep="_").assign(match_id = match['match_id'])


chains = []
for i in range(1, events['possession'].max()):
    chains.append(events[events['possession'] == i])