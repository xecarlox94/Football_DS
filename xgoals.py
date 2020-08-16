import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import statsmodels.api as sm
import statsmodels.formula.api as smf

import json

with open('data/wy_scout/events/events_England.json') as f:
    data = json.load(f)
    
    
train = pd.DataFrame(data)
shots = train[ train['subEventName'] == 'Shot']

shots_model = pd.DataFrame(columns=['Goal', 'X', 'Y', 'C', 'Distance', 'Angle'])

for i, shot in shots.iterrows():
    header = False
    goal = False
    for tag in shot['tags']:
        if tag['id'] == 403:
            header = True

        if tag['id'] == 101:
            goal = True

    if header:
        continue

    shots_model.at[i, 'X'] = 100 - shot['positions'][0]['x']
    shots_model.at[i, 'Y'] = shot['positions'][0]['y']
    shots_model.at[i, 'C'] = abs(shot['positions'][0]['y'] - 50)

    x = shots_model.at[i, 'X'] * 105 / 100
    y = shots_model.at[i, 'C'] * 65 / 100

    shots_model.at[i, 'Distance'] = np.sqrt( x**2 + y ** 2)

    a = np.arctan( 7.32 * x / ( x**2 + y **2 - (7.32/2)**2))

    if a < 0:
        a = np.pi + a

    shots_model.at[i, 'Angle'] = a

    shots_model.at[i, 'Goal'] = goal


"""
H_shot = np.histogram2d(shots_model['X'], shots_model['Y'], bins=50, range=[[0, 100], [0, 100]])

shots_goals = shots_model[shots_model['Goal'] == True]
H_goal = np.histogram2d(shots_goals['X'], shots_goals['Y'], bins=50, range=[[0, 100], [0, 100]])


(fig, ax, _) = pviz.createGoalMouthPitch()
pos = ax.imshow(H_shot[0], extent=[-1, 66, 104, -1], aspect='auto', cmap=plt.cm.Reds)
fig.colorbar(pos, ax=ax)
ax.set_title('shots')
plt.xlim((-1, 66))
plt.ylim((-3, 50))
plt.tight_layout()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()


(fig, ax, _) = pviz.createGoalMouthPitch()
pos = ax.imshow(H_goal[0], extent=[-1, 66, 104, -1], aspect='auto', cmap=plt.cm.Reds)
fig.colorbar(pos, ax=ax)
ax.set_title('goals')
plt.xlim((-1, 66))
plt.ylim((-3, 50))
plt.tight_layout()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()


(fig, ax, _) = pviz.createGoalMouthPitch()
pos = ax.imshow( (H_goal[0] / H_shot[0]), extent=[-1, 66, 104, -1], aspect='auto', cmap=plt.cm.Reds)
fig.colorbar(pos, ax=ax)
ax.set_title('goals / shots probability')
plt.xlim((-1, 66))
plt.ylim((-3, 50))
plt.tight_layout()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
"""

"""
minutes_played = np.array([120, 452, 185, 708, 340, 561])
goals_scored = np.array([1, 6, 3, 7, 3, 5])

minutes_model = pd.DataFrame()
minutes_model = minutes_model.assign(minutes=minutes_played)
minutes_model = minutes_model.assign(goals=goals_scored)


fig, ax = plt.subplots(num=1)
ax.plot(minutes_played, goals_scored, linestyle='none', marker='.', markerSize=12, color='black')
ax.set_ylabel('Goals Scored')
ax.set_xlabel('Minutes Played')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xlim((0, 750))
plt.ylim((0, 8))


a=0

model_fit = smf.ols(formula='goals_scored ~ minutes_played - 1', data=minutes_model).fit()
print(model_fit.summary())
[b] = model_fit.params


x = np.arange(800, step=0.1)
y = a + b * x

ax.plot(x,y, color='black')

for i, mp in enumerate(minutes_played):
    ax.plot([mp, mp], [goals_scored[i], a+b*mp], color='red')

"""

"""
b=[3, -3]

x = np.arange(5, step=0.1)

y = 1 / (1 + np.exp(-b[0] -b[1]*x) )

fig, ax = plt.subplots(num=1)

plt.ylim((-0.05, 1.05))
plt.xlim((0, 5))

ax.set_ylabel('y')
ax.set_xlabel('x')

ax.plot(x, y, linestyle='solid', color='black')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.show()

"""

shots_200 = shots_model.iloc[:200]

fig, ax = plt.subplots(num=1)
ax.plot(shots_200['Angle']*180/np.pi, shots_200['Goal'], linestyle='none', marker='.', markerSize=12, color='black')
ax.set_ylabel('Goal scored')
ax.set_xlabel('Shot angle (degrees)')
plt.ylim((-0.05, 1.05))
ax.set_yticks([0, 1])
ax.set_yticklabels(['No', 'Yes'])
plt.show()

