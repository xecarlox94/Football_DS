import metrica_IO as mio

# 106, 68
pitchSize = (106, 68)
events, tracking, teams = mio.readMatchData(2, pitchSize)

print(events['Type'].value_counts())

home = mio.calcVelocities(teams[0][:200])
away = mio.calcVelocities(teams[1][:200])

tracking = tracking[:200]
events = events[:200]

