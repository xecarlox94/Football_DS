import metrica_IO as mio
from viz import pitch_viz as pviz
import metrica_viz as mviz


# 106, 68
pitchSize = (106, 68)
events, teams = mio.readMatchData(2, pitchSize)

home = teams[0]
away = teams[1]

#home = mio.calcVelocities(teams[0][:200])
#away = mio.calcVelocities(teams[1][:200])

#events = events[:200]

















"""
home_events = events[events['Team'] == 'Home']
away_events = events[events['Team'] == 'Away']
home_events['Type'].value_counts()
away_events['Type'].value_counts()



shots = events[events['Type'] == 'SHOT']
home_shots = shots[shots['Team'] == 'Home']
away_shots = shots[shots['Team'] == 'Away']
home_shots['Subtype'].value_counts()
away_shots['Subtype'].value_counts()


home_shots['From'].value_counts()


home_goals = home_shots[home_shots['Subtype'].str.contains('-GOAL')].copy()
away_goals = away_shots[away_shots['Subtype'].str.contains('-GOAL')].copy()
home_goals['Minute'] = home_goals['Start Time [s]'] / 60
away_goals['Minute'] = home_goals['Start Time [s]'] / 60



(figaxplt, pdimen) = pviz.createPitch(pitchSize[0], pitchSize[1])
(fig, ax, plt) = figaxplt
fig.set_size_inches(15,10)

ax.plot( events.loc[198]['Start X'], events.loc[198]['Start Y'], 'ro' )
ax.annotate("", xy=events.loc[198][['End X','End Y']], xytext=events.loc[198][['Start X', 'Start Y']], alpha=0.6, arrowprops=dict(arrowstyle="->", color='r'))

(fig, ax) = mviz.plot_events(events.loc[190:198], figax=(fig, ax), pitchSize=pdimen)

ax.plot( home['Home_11_x'].iloc[:1500],home['Home_11_y'].iloc[:1500], 'r', MarkerSize=1 )
ax.plot( home['Home_1_x'].iloc[:1500],home['Home_1_y'].iloc[:1500], 'b', MarkerSize=1 )
ax.plot( away['Away_15_x'].iloc[:1500],away['Away_15_y'].iloc[:1500], 'g', MarkerSize=1 )


(fig, ax) = mviz.plot_frame(home.loc[51],away.loc[51], figax=(fig, ax))

(fig, ax) = mviz.plot_events( events.loc[198:198], annotate=True, figax=(fig,ax) )

frame = events.loc[198]['Start Frame']

(fig, ax) = mviz.plot_frame( home.loc[frame], away.loc[frame], figax=(fig,ax) )
"""
