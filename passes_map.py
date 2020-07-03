import statsBomb_IO as sb
import pandas as pd
from viz import pitch_viz as pitch

competition = sb.getCompetitions()[26]

match = sb.getMatches(competition)[27]

lineups = sb.getMatchLineups(match)

events = sb.getMatchEvents(match)

homeTeamName = match['home_team']['home_team_name']
awayTeamName = match['away_team']['away_team_name']

pitchSz = (130, 90)
fig, ax, plt = pitch.createPitch(pitchSz[0], pitchSz[1])

df = pd.json_normalize(events, sep = "_").assign(match_id = match['match_id']).set_index('id')

passes = df.loc[df['type_id'] == 30]

xavi_passes = []
for passe in passes.iterrows():
    if passe[1]['player_id'] == 5216:
        x = passe[1]['location'][0]
        y = passe[1]['location'][1]
        passCircle = plt.Circle((x, y),1,color="blue")
        passCircle.set_alpha(0.2)
        ax.add_patch(passCircle)
        dx = passe[1]['pass_end_location'][0]
        dy = passe[1]['pass_end_location'][1]
        passArrow = plt.Arrow(x,y,dx,dy,width=1.5, color="blue")
        ax.add_patch(passArrow)


fig.set_size_inches(10,7)

plt.show()