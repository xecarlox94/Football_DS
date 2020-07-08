import metrica_IO as mio
from viz import pitch_viz

# 106, 68
pitchSize = (106, 68)
events, tracking, teams = mio.readMatchData(2, pitchSize)


home = mio.calcVelocities(teams[0][:200])
away = mio.calcVelocities(teams[1][:200])

tracking = tracking[:200]
events = events[:200]


def plot_events(events, figax=None, pitchSize=(106, 68), indicators=['Marker', 'Arrow'], color='r', marker_style='o', alpha=0.5, annotate=False):
    if figax is None:
        fig, ax = pitch_viz.createPitch(pitchSize=pitchSize)
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


#def plot_frame(homeTeam)