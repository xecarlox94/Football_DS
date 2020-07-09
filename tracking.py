import metrica_IO as mio
from viz import pitch_viz as pviz


def plot_events(events, figax=None, pitchSize=(106, 68), indicators=['Marker', 'Arrow'], color='r', marker_style='o', alpha=0.5, annotate=False):
    if figax is None:
        (figaxplt, pdimen) = pviz.createPitch(pitchSize[0], pitchSize[1])
        (fig, ax, plt) = figaxplt
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
    

def plot_frame(homeTeam, awayTeam, figax=None, teamColors=('r', 'b'), pitchSize=(106, 68), inc_plr_vel=False, PlayerMarkerSize=10, PlayerAlpha=0.7, annotate=False ):
    if figax is None:
        (figaxplt, pdimen) = pviz.createPitch(pitchSize[0], pitchSize[1])
        (fig, ax, plt) = figaxplt
    else:
        fig, ax = figax
        
    for team, color in zip( [homeTeam, awayTeam], teamColors):
        x_columns = [c for c in team.keys() if c[-2:].lower() == '_x' and c!='ball_x']
        y_columns = [c for c in team.keys() if c[-2:].lower() == '_y' and c!='ball_y']
        ax.plot( team[x_columns], team[y_columns], color + 'o', MarkerSize=PlayerMarkerSize, alpha=PlayerAlpha)
        if inc_plr_vel:
            vx_columns = ['{}_vx'.format(c[:-2]) for c in x_columns]
            vy_columns = ['{}_vy'.format(c[:-2]) for c in y_columns]
            ax.quiver( team[x_columns], team[y_columns], teams[vx_columns], teams[vy_columns], color=color, scale_units='inches', scale=10, width=0.0015, headlength=5, headwidth=3, alpha=PlayerAlpha)
        if annotate:
            [ ax.text(team[x]+0.5, team[y]+0.5, x.split('_'), fontsize=10, color=color) for x,y in zip(x_columns, y_columns) if not ( np.isnan(team[x]) or np.isnan(team[y]) )]
            
    ax.plot( homeTeam['ball_x'], homeTeam['ball_y'], 'ko', MarkerSize=6, LineWidth=0)
    
    return fig,ax



# 106, 68
pitchSize = (106, 68)
events, teams = mio.readMatchData(2, pitchSize)

home = teams[0]
away = teams[1]

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



(figaxplt, pdimen) = pviz.createPitch(pitchSize[0], pitchSize[1])
(fig, ax, plt) = figaxplt
fig.set_size_inches(15,10)

#ax.plot( events.loc[198]['Start X'], events.loc[198]['Start Y'], 'ro' )
#ax.annotate("", xy=events.loc[198][['End X','End Y']], xytext=events.loc[198][['Start X', 'Start Y']], alpha=0.6, arrowprops=dict(arrowstyle="->", color='r'))

#plot_events(events.loc[190:198], figax=(fig, ax), pitchSize=pdimen)

"""
ax.plot( home['Home_11_x'].iloc[:1500],home['Home_11_y'].iloc[:1500], 'r', MarkerSize=1 )
ax.plot( home['Home_1_x'].iloc[:1500],home['Home_1_y'].iloc[:1500], 'b', MarkerSize=1 )
ax.plot( away['Away_15_x'].iloc[:1500],away['Away_15_y'].iloc[:1500], 'g', MarkerSize=1 )
"""


(fig, ax) = plot_frame(home.loc[51],away.loc[51], figax=(fig, ax))

plt.show()