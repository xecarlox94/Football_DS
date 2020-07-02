import statsBomb_IO as sb
import numpy as np
import pandas as pd
from viz import pitch_viz as pitch

competition = sb.getCompetitions()[26]

match = sb.getMatches(competition)[27]

lineups = sb.getMatchLineups(match)

events = sb.getMatchEvents(match)

homeTeamName = match['home_team']['home_team_name']
awayTeamName = match['away_team']['away_team_name']

pitchSz = (120, 80)
fig, ax, plt = pitch.createPitch(pitchSz[0], pitchSz[1])

df = pd.json_normalize(events, sep = "_").assign(match_id = match['match_id']).set_index('id')

passes = df.loc[df['type_id'] == 30]

xavi_passes = []
for passe in passes.iterrows():
    if passe['player_id'] == 20131:
        print(234)


fig.set_size_inches(10,7)

plt.show()