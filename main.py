import statsBomb_IO as sb
import numpy as np
import pandas as pd
from viz import pitch_viz as pitch

competition = sb.getCompetitions()[26]

match = sb.getMatches(competition)[27]

lineups = sb.getMatchLineups(match)

events = sb.getMatchEvents(match)

homeTeam = match['home_team']
awayTeam = match['away_team']

fig, ax, plt = pitch.createPitch(120, 80)

df = pd.json_normalize(events, sep = "_").assign(match_id = match['match_id']).set_index('id')

shots = df.loc[df['type_name'] == 'Shot']


for i, shot in shots.iterrows():
    x = shot['location'][0]
    y = shot['location'][1]
    
    goal = shot['shot_outcome_name'] == 'Goal'
    
    shotCircle = np.sqrt(shot['shot_statsbomb_xg'] * 5)
    
    shotCircle = plt.Circle((x, y), shotCircle, color="red")
    
    ax.add_patch(shotCircle)


plt.show()