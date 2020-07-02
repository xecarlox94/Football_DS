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

shots = df.loc[df['type_name'] == 'Shot']


for i, shot in shots.iterrows():
    x = shot['location'][0]
    y = shot['location'][1]
    
    goal = shot['shot_outcome_name'] == 'Goal'
    
    
    circleSize = np.sqrt(shot['shot_statsbomb_xg'] * 5)
    
    if (shot['team_name'] == homeTeamName):
        if (goal):
            shotCircle = plt.Circle((x, y), circleSize, color="red")
            plt.text((x + 1), y - 1, shot['player_name'])
        else:
            shotCircle = plt.Circle((x, y), circleSize, color="red")
            shotCircle.set_alpha(.2)
    else:
        if (goal):
            shotCircle = plt.Circle((pitchSz[0] - x, y), circleSize, color="blue")
            plt.text((pitchSz[0] - x + 1), y - 1, shot['player_name'])
        else:
            shotCircle = plt.Circle((pitchSz[0] - x, y), circleSize, color="blue")
            shotCircle.set_alpha(.2)
    
    ax.add_patch(shotCircle)

fig.set_size_inches(10,7)

plt.show()