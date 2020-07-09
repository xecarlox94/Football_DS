import metrica_IO as mio
from viz import pitch_viz as pviz

# 106, 68
pitchSize = (106, 68)
events, teams = mio.readMatchData(2, pitchSize)

home = teams[0][:200]
away = teams[1][:200]

#home = mio.calcVelocities(teams[0][:200])
#away = mio.calcVelocities(teams[1][:200])

#events = events[:200]


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


figaxplt = pviz.createPitch(pitchSize[0], pitchSize[1])

(fig, ax, plt, ps) = figaxplt


"""
def plot_events(events, figax=None, pitchSize=(106, 68), indicators=['Marker', 'Arrow'], color='r', marker_style='o', alpha=0.5, annotate=False):
    if figax is None:
        figax, plt, pdimen = pitch_viz.createPitch(pitchSize[0], pitchSize[1])
    else:
        fig, ax = figax
        
    for i, row in events.iterrows():
        if 'Marker' in indicators:
            ax.plot( row['Start X'], row['Start Y'], alpha=alpha)
        
        if 'Arrow' in indicators:
            ax.annotate("", xy=row[['End X','End Y']], xytext=row[['Start X', 'Start Y']], alpha=alpha, arrowprops=dict(alpha=alpha, width=0.5, headlength=4.0, color=color), annotation_clip=False)
            
        if annotate:
            textstring = row['Type'] + ': ' + row['From']
            ax.text( row['Start X'], row['Start Y'], textstring, fontsize=10, color=color)
    
    return fig, ax
"""


#def plot_frame(homeTeam)