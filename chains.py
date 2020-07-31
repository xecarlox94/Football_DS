import statsBomb_IO as sio
import pandas as pd
import numpy as np

#competition 9 -> inter - bayern
competition = sio.getCompetitions()[25]


match = sio.getMatches(competition).iloc[6]


events = sio.getMatchEvents(match)


passes = events[events['type_id'] == 30]