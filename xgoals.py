import numpy as np
import pandas as pd

from viz import pitch_viz as pviz
import json

with open('data/wy_scout/events/events_England.json') as f:
    data = json.load(f)
    
    
train = pd.DataFrame(data)