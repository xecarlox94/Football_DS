import metrica_IO as mio
from viz import pitch_viz as pviz, metrica_viz as mviz, metrica_pitchControl as mpc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = '/Users/jf94u/Desktop/Projects/football_dataScience/data'
# 106, 68
pitchSize = (106, 68)
events, (home, away) = mio.readMatchData(2, pitchSize)






"""
#lecture 3
shots = events[events['Type'] == 'SHOT']
goals = shots[shots['Subtype'].str.contains('-GOAL')].copy()



mviz.plot_events(events.loc[820:823], color='k', annotate=True)


params = mpc.default_model_params()

GK_numbers = [mio.findGoalkeeper(home), mio.findGoalkeeper(away)]


PPFC, xgrid, ygrid = mpc.generate_pitch_control_for_event(820, events, home, away, params, GK_numbers)
mviz.plot_event_pitch_control(820, events, home, away, PPFC)

PPFC, xgrid, ygrid = mpc.generate_pitch_control_for_event(821, events, home, away, params, GK_numbers)
mviz.plot_event_pitch_control(821, events, home, away, PPFC)

PPFC, xgrid, ygrid = mpc.generate_pitch_control_for_event(822, events, home, away, params, GK_numbers)
mviz.plot_event_pitch_control(822, events, home, away, PPFC)


home_passes = events[ (events['Type'].isin(['PASS'])) & (events['Team'] == 'Home') ]

pass_success_probability = []

for i, row in home_passes.iterrows():

    pass_start_pos = np.array([row['Start X'], row['Start Y']])
    pass_target_pos= np.array([row['End X'], row['End Y']])
    pass_frame = row['Start Frame']

    att_plrs = mpc.initialise_players(home.loc[pass_frame], 'Home', params, GK_numbers[0])
    def_plrs = mpc.initialise_players(away.loc[pass_frame], 'Away', params, GK_numbers[1])
    Patt,Pdef = mpc.calculate_pitch_control_at_target(pass_target_pos, att_plrs, def_plrs, pass_start_pos, params)
    
    pass_success_probability.append( (i, Patt) )
    

fig, ax = plt.subplots()
ax.hist([p[1] for p in pass_success_probability], np.arange(0,1.1,0.1))
ax.set_xlabel('Pass success probability')
ax.set_ylabel('Frequency')


pass_success_probability = sorted( pass_success_probability, key= lambda x: x[1] )

risky_passes = events.loc[ [p[0] for p in pass_success_probability if p[1] < 0.5] ]

mviz.plot_events(risky_passes, color='k', annotate=True)


for p in pass_success_probability[:20]:
    outcome = events.loc[ p[0] + 1 ].Type
    print( p[1], outcome)

"""


"""
#lecture 2
home_players = np.unique( [ c.split('_')[1] for c in home.columns if c[:4].lower() == 'home' ] )
home_summary = pd.DataFrame(index=home_players)

minutes = []
for player in home_players:
    column = 'Home_' + player + '_x'
    player_minutes = ( home[column].last_valid_index() - home[column].first_valid_index() ) / 25 / 60
    minutes.append(player_minutes)
home_summary['Minutes Played'] = minutes
home_summary.sort_values(['Minutes Played'], ascending=False, inplace=True)


distance = []
for player in home_summary.index:
    column = 'Home_' + player + '_speed'
    player_distance = home[column].sum() / 25. / 1000
    distance.append(player_distance)
home_summary['Distance [km]'] = distance


plt.subplots()
ax = home_summary['Distance [km]'].plot.bar(rot=8)
ax.set_xlabel('Player')
ax.set_ylabel('Distance ')

mviz.plot_frame(home.loc[51],away.loc[51], annotate=True, inc_plr_vel=True)


walking =[]
jogging =[]
running = []
sprinting = []

for player in home_summary.index:
    column = 'Home_' + player + '_speed'
    plr_distance = home.loc[ home[column] < 2, column ].sum() / 25. / 1000
    walking.append(plr_distance)
    plr_distance = home.loc[ (home[column] >= 2) & (home[column] < 4), column ].sum() / 25. / 1000
    jogging.append(plr_distance)
    plr_distance = home.loc[ (home[column] >= 4) & (home[column] < 7), column ].sum() / 25. / 1000
    running.append(plr_distance)
    plr_distance = home.loc[ home[column] >= 7, column].sum() / 25. / 1000
    sprinting.append(plr_distance)
    
home_summary['Walking [km]'] = walking
home_summary['Jogging [km]'] = jogging
home_summary['Running [km]'] = running
home_summary['Sprinting [km]'] = sprinting


plt.subplots()
ax = home_summary[['Walking [km]','Jogging [km]','Running [km]','Sprinting [km]']].plot.bar(colormap='coolwarm')
ax.set_xlabel('Player')
ax.set_ylabel('Distance covered [km]')



nsprints = []
sprint_threeshold = 7
sprint_window = 1 * 25
for player in home_summary.index:
    column = 'Home_' + player + '_speed'
    player_sprints = np.diff(1 * (np.convolve(1 * (home[column] >= sprint_threeshold), np.ones(sprint_window), mode='same') >= sprint_window) )
    nsprints.append( np.sum(player_sprints == 1) )
home_summary['# sprints'] = nsprints


player = '10'
column = 'Home_' + player + '_speed'
column_x = 'Home_' + player + '_x'
column_y = 'Home_' + player + '_y'
p_sprints = np.diff(1 * (np.convolve(1 * (home[column] >= sprint_threeshold), np.ones(sprint_window), mode='same') >= sprint_window) )
p_sprints_start = np.where(p_sprints == 1)[0] - int(sprint_window/2)
p_sprints_end = np.where(p_sprints == -1)[0] + int(sprint_window/2)

(figaxplt, pdimen) = pviz.createPitch(pitchSize[0], pitchSize[1])
(fig, ax, plt) = figaxplt

for s,e in zip(p_sprints_start, p_sprints_end):
    ax.plot(home[column_x].iloc[s], home[column_y].iloc[s], 'ro')
    ax.plot(home[column_x].iloc[s:e+1], home[column_y].iloc[s:e+1], 'r')
"""


"""
lecture 2


mviz.save_match_clip(home[20000:20000+2000],away[20000:20000+2000], DATA_DIR, include_player_velocities=True, fname="play2", PlayerMarkerSize=5)


(figaxplt, pdimen) = pviz.createPitch(pitchSize[0], pitchSize[1])
(fig, ax, plt) = figaxplt

fig.set_size_inches(15,10)


(fig, ax) = mviz.plot_frame(home.loc[10000],away.loc[10000], figax=(fig, ax), annotate=True, inc_plr_vel=True)

plt.show()


"""




"""
#lecture 1

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