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
fig, ax, plt, _ = pitch.createPitch(pitchSz[0], pitchSz[1])

df = pd.json_normalize(events, sep = "_").assign(match_id = match['match_id']).set_index('id')

passes = df.loc[df['type_id'] == 30]


for passe in passes.iterrows():
    if passe[1]['player_id'] == 5552:
        print()
        print(passe[1])
        x = passe[1]['location'][0]
        y = passe[1]['location'][1]
        dx = passe[1]['pass_end_location'][0]
        dy = passe[1]['pass_end_location'][1]
        print(x,y,dx,dy)
        ax.plot(x, y, 'ro')
        ax.annotate("", xy=(dx,dy), xytext=(x,y), alpha=0.6, arrowprops=dict(arrowstyle="->",color='r'))


fig.set_size_inches(10,7)

plt.show()