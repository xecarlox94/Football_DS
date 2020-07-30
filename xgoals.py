import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from viz import pitch_viz as pviz
import json

with open('data/wy_scout/events/events_England.json') as f:
    data = json.load(f)
    
    
train = pd.DataFrame(data)
shots = train[ train['subEventName'] == 'Shot']

shots_model = pd.DataFrame(columns=['X', 'Y', 'C', 'Distance', 'Angle', 'Goal'])

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
    y = shots_model.at[i, 'Y'] * 65 / 100

    shots_model.at[i, 'Distance'] = np.sqrt( x**2 + y ** 2)

    a = np.arctan( 7.32 * x / ( x**2 + y **2 - (7.32/2)**2))

    if a < 0:
        a = np.pi + a

    shots_model.at[i, 'Angle'] = a

    shots_model.at[i, 'Goal'] = goal



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



