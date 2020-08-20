import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import statsmodels.api as sm
import statsmodels.formula.api as smf

from viz import pitch_viz as pviz

import json

with open('data/wy_scout/events/events_England.json') as f:
    data = json.load(f)
    
    
train = pd.DataFrame(data)
shots = train[ train['subEventName'] == 'Shot']

shots_model = pd.DataFrame(columns=['Goal', 'X', 'Y'])

for i, shot in shots.iterrows():
    header = False
    goal = 0
    for tag in shot['tags']:
        if tag['id'] == 403:
            header = True

        if tag['id'] == 101:
            goal = 1

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
    
    
goals_all = shots_model[shots_model['Goal'] == 1]


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

shotcount_dist = np.histogram(shots_model['Angle']*180/np.pi, bins=40, range=[0, 180])
goalcount_dist = np.histogram(goals_all['Angle']*180/np.pi, bins=40, range=[0, 180])
prob_goal = np.divide(goalcount_dist[0], shotcount_dist[0])
angle = shotcount_dist[1]
midangle = (angle[:-1] + angle[1:])/2
fig, ax = plt.subplots(num=2)
ax.plot(midangle, prob_goal, linestyle='none', marker='.', markerSize=12, color='black')
ax.set_ylabel('Probability scoring')
ax.set_xlabel('Angle')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)


test_model = smf.glm(formula="Goal ~ Angle", data=shots_model, family=sm.families.Binomial()).fit()
#print(test_model.summary())

b = test_model.params

xGprob = 1 / (1 + np.exp(b[0] + b[1] * midangle * np.pi/ 180))
ax.plot(midangle, xGprob, linestyle='solid', color='black')


plt.show()

shotcount_dist = np.histogram(shots_model['Distance'], bins=40, range=[0, 55])
goalcount_dist = np.histogram(goals_all['Distance'], bins=40, range=[0, 55])
prob_goal = np.divide(goalcount_dist[0], shotcount_dist[0])
distance = shotcount_dist[1]
middistance = (distance[:-1] + distance[1:]) / 2
fig, ax = plt.subplots(num=3)
ax.plot(middistance, prob_goal, linestyle='none', marker='.', markerSize=12, color='black')
ax.set_xlabel('Distance')
ax.set_ylabel('Probability')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)


test_model = smf.glm(formula="Goal ~ Distance", data=shots_model, family=sm.families.Binomial()).fit()
print(test_model.summary())
b = test_model.params

xGprob = 1 / (1 + np.exp(b[0] + b[1] * middistance))
ax.plot(middistance, xGprob, linestyle='solid', color='black')

plt.show()


model_variables = ['Angle']
model = ''
for v in model_variables[:-1]:
    model = model + v + ' +'
model = model + model_variables[-1]


test_model = smf.glm(formula="Goal ~ Angle", data=shots_model, family=sm.families.Binomial()).fit()
print(test_model.summary())
b = test_model.params

def calculatexG(sh):
    bsum = b[0]
    for i, v in enumerate(model_variables):
        bsum = bsum + b[i + 1] * sh[v]
    xG = 1 / (1 + np.exp(bsum))
    return xG


xG = shots_model.apply(calculatexG, axis=1)
shots_model = shots_model.assign(xG=xG)


pgoald_2d = np.zeros((65, 65))

for x in range(65):
    for y in range(65):
        sh = dict()
        a = np.arctan(7.32 *x /(x**2 + abs(y-65/2)**2 - (7.32/2)**2))
        if a < 0:
            a = np.pi + a
        sh['Angle'] = a
        sh['Distance'] = np.sqrt(x**2 + abs(y-65/2)**2)
        pgoald_2d[x, y] = calculatexG(sh)

fig, ax, _ = pviz.createGoalMouthPitch()

pos = ax.imshow(pgoald_2d, extent=[-1, 65, 65, -1], aspect='auto', cmap=plt.cm.Reds, vmin=0, vmax=0.5)
fig.colorbar(pos, ax=ax)
ax.set_title('Probability of goal')
plt.xlim((0,66))
plt.ylim((-3, 35))
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
