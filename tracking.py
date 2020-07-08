import metrica_IO as mio

# 106, 68
pitchSize = (106, 68)
events, tracking = mio.readMatchData(2, pitchSize)

tracking = tracking[:100]
events = events[:100]
