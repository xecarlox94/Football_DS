import statsBomb_IO as sio

competitions = sio.getCompetitions()


matches = []

for c in competitions:
    ms = sio.getMatches(c)
    for m in ms:
        matches.append(m)