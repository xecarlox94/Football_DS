import statsBomb_IO as sb
from viz import pitch_viz as pitch

competition = sb.getCompetitions()[26]

match = sb.getMatches(competition)[27]


lineups = sb.getMatchLineups(match)

events = sb.getMatchEvents(match)

eventTypes = {}
for e in events:
    typeEvent = e['type']['name']
    
    if typeEvent in eventTypes:
        eventTypes[typeEvent] = eventTypes[typeEvent] + 1
    else:
        eventTypes[typeEvent] = 1