import numpy as np
import metrica_IO as mio
from viz import metrica_pitchControl as mpc

def load_EPV_grid(fname="EPV_grid.csv"):

    epv = np.loadtxt(fname, delimiter=',')
    return epv


def get_EPV_at_position(position, EPV, attack_direction, field_dimen=(106.,68.)):

    x, y = position

    if abs(x) > field_dimen[0] / 2. or abs(y) > field_dimen[1] / 2.:
        return 0.0

    else:
        if attack_direction == -1:
            EPV = np.fliplr(EPV)

        ny, nx = EPV.shape

        dx = field_dimen[0] / float(nx)
        dy = field_dimen[1] / float(ny)

        ix = (x + field_dimen[0] / 2. - .0001) / dx
        iy = (y + field_dimen[1] / 2. - .0001) / dy

        return EPV[int(iy), int(ix)]


def calculate_epv_added(event_id, events, track_home, track_away, GK_numbers, EPV, params):

    pass_start_pos = np.array([events.loc[event_id]['Start X'], events.loc[event_id]['Start Y']])
    pass_targt_pos = np.array([events.loc[event_id]['End X'], events.loc[event_id]['End Y']])

    pass_frame = events.loc[event_id]['Start Frame']
    pass_team = events.loc[event_id].Team

    home_attack_direction = mio.find_playing_position(track_home, 'Home')

    if pass_team == 'Home':
        attack_direction = home_attack_direction
        attacking_players = mpc.initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[0])
        defending_players = mpc.initialise_players(track_away.loc[pass_frame], 'Away', params, GK_numbers[1])
    elif pass_team == 'Away':
        attack_direction = home_attack_direction * -1
        defending_players = mpc.initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[0])
        attacking_players = mpc.initialise_players(track_away.loc[pass_frame], 'Away', params, GK_numbers[1])
        
    attacking_players = mpc.check_offsides(attacking_players, defending_players, pass_start_pos, GK_numbers)

    Patt_start, _ = mpc.calculate_pitch_control_at_target(pass_start_pos, attacking_players, defending_players, pass_start_pos, params)
    Patt_targt, _ = mpc.calculate_pitch_control_at_target(pass_targt_pos, attacking_players, defending_players, pass_start_pos, params)

    EPV_start = get_EPV_at_position(pass_start_pos, EPV, attack_direction=attack_direction)
    EPV_targt = get_EPV_at_position(pass_targt_pos, EPV, attack_direction=attack_direction)

    EEPV_targt = Patt_targt * EPV_targt
    EEPV_start = Patt_start * EPV_start

    EPPV_added = EEPV_targt - EEPV_start
    EPPV_remvd = EEPV_start - EEPV_targt

    return EPPV_added, EPPV_remvd


def find_max_value_added_target( event_id, events, track_home, track_away, GK_numbers, EPV, params):

    pass_start_pos = np.array([events.loc[event_id]['Start X'], events.loc[event_id]['Start Y']])
    pass_frame = events.loc[event_id]['Start Frame']
    pass_team = events.loc[event_id].Team

    home_attack_direction = mio.find_playing_position(track_home, 'Home')

    if pass_team == 'Home':
        attack_direction = home_attack_direction
        attacking_players = mpc.initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[0])
        defending_players = mpc.initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[1])
    elif pass_team == 'Away':
        attack_direction = home_attack_direction * -1
        defending_players = mpc.initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[0])
        attacking_players = mpc.initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[1])

    attacking_players = mpc.check_offsides(attacking_players, defending_players, pass_start_pos, GK_numbers)

    Patt_start, _ = mpc.calculate_pitch_control_at_target(pass_start_pos, attacking_players, defending_players, pass_start_pos, params)

    EPV_start = get_EPV_at_position(pass_start_pos, EPV, attack_direction=attack_direction)

    PPCF, xgrid, ygrid = mpc.generate_pitch_control_for_event(event_id, events, track_home, track_away, params, GK_numbers)

    if attack_direction == -1:
        EEPV = np.fliplr(EPV) * PPCF
    else:
        EEPV = EPV * PPCF

    maxEPV_idx = np.unravel_index(EEPV.argmax(), EEPV.shape)

    EEPV_start = Patt_start * EPV_start

    maxEPV_added = EEPV.max() - EEPV_start

    max_target_location = (xgrid[maxEPV_idx[1], ygrid[maxEPV_idx[0]]])

    return maxEPV_added, max_target_location
