import numpy as np



def default_model_params(time_to_control_veto=3):
    params = {}
    params['max_player_accel'] = 7.
    params['max_player_speed'] = 5.
    params['average_ball_speed'] = 15.
    params['reaction_time'] = 0.7
    params['tti_sigma'] = 0.45
    params['kappa_def'] = 1.
    params['lambda_att'] = 4.3
    params['lambda_def'] = 4.3 * params['kappa_def']
    params['lambda_gk'] = 3.0 * params['kappa_def']

    params['int_dt'] = 0.04
    params['max_int_time'] = 10
    params['model_converge_tol'] = 0.01

    params['time_to_control_att'] = time_to_control_veto * np.log(10) * ( np.sqrt(3) * params['tti_sigma'] / np.pi + 1 / params['lambda_att'] )
    params['time_to_control_def'] = time_to_control_veto * np.log(10) * ( np.sqrt(3) * params['tti_sigma'] / np.pi + 1 / params['lambda_def'] )

    return params


class Player(object):
    def __init__(self, pid, team, teamname, GKid, params):
        self.id = pid
        self.isGK = self.id == GKid
        self.teamname = teamname
        self.playername = "%s_%s_" % (teamname, self.id)
        self.vmax = params['max_player_speed']
        self.reaction_time = params['reaction_time']
        self.tti_sigma = params['tti_sigma']
        self.lambda_att = params['lambda_att']
        self.lambda_def = params['lambda_gk'] if self.isGK else params['lambda_def']
        self.get_position(team)
        self.get_velocity(team)
        self.PPCF = 0

    def get_position(self, team):
        self.position = np.array( [team[self.playername + 'x'], team[self.playername + 'y']] )
        self.inframe = not np.any( np.isnan(self.position) )


    def get_velocity(self, team):
        self.velocity = np.array( [team[self.playername + 'vx'], team[self.playername + 'vy']] )
        if np.any( np.isnan(self.velocity) ):
            self.velocity = np.array([0., 0.])

    def simple_time_to_intercept(self, r_final):
        self.PPCF = 0

        r_reaction = self.position + self.velocity * self.reaction_time

        self.time_to_intercept = self.reaction_time + np.linalg.norm(r_final - r_reaction) / self.vmax
        return self.time_to_intercept

    def probability_intercept_ball(self, T):
        return 1 / (1. + np.exp( -np.pi / np.sqrt(3.0) / self.tti_sigma * ( T - self.time_to_intercept) ) )



def initialise_players(team, teamname, params, GKid):
    player_ids = np.unique( [c.split('_')[1] for c in team.keys() if c[:4] == teamname ] )

    team_players = []
    for player in player_ids:
        p = Player(player, team, teamname, GKid, params)
        if p.inframe:
            team_players.append(p)

    return team_players


def check_offsides( attacking_players, defending_players, ball_position, GK_numbers, verbose=False, tol=0.2):
    defending_GK_id = GK_numbers[1] if attacking_players[0].teamname == "Home" else GK_numbers[0]

    assert defending_GK_id in [ p.id for p in defending_players ]

    defending_GK = [p for p in defending_players if p.id == defending_GK_id][0]
    
    defending_half = np.sign(defending_GK.position[0])
    
    deepest_defender_x = sorted( [p.position[0]*defending_half for p in defending_players], reverse=True)[1]

    tol *= defending_half
    ball_pos = ball_position[0] * defending_half

    offside_line = max(deepest_defender_x, ball_pos, 0.0) + tol

    if verbose:
        for p in attacking_players:
            if p.position[0] * defending_half > offside_line:
                print( "player %s in %s team is offside" % (p.id, p.playername) )

    attacking_players = [p for p in attacking_players if p.position[0] * defending_half <= offside_line]

    return attacking_players


def calculate_pitch_control_at_target(target_pos, attacking_players, defending_players, ball_start_pos, params):
    if ball_start_pos is None or any(np.isnan(ball_start_pos)):
        ball_travel_time = 0.0
    else:
        ball_travel_time = np.linalg.norm(target_pos - ball_start_pos) / params['average_ball_speed']

    ta_min_att = np.nanmin( [p.simple_time_to_intercept(target_pos) for p in attacking_players ] )
    ta_min_def = np.nanmin( [p.simple_time_to_intercept(target_pos) for p in defending_players ] )

    if ta_min_att - max(ball_travel_time, ta_min_def) >= params['time_to_control_att']:
        return 0., 1.
    elif ta_min_def - max(ball_travel_time, ta_min_def) >= params['time_to_control_def']:
        return 1., 0.
    else:
        attacking_players = [p for p in attacking_players if p.time_to_intercept - ta_min_att < params['time_to_control_att']]
        defending_players = [p for p in defending_players if p.time_to_intercept - ta_min_def < params['time_to_control_def']]

        dT_array = np.arange(ball_travel_time - params['int_dt'], ball_travel_time + params['max_int_time'], params['int_dt'])
        PPCFatt = np.zeros_like(dT_array)
        PPCFdef = np.zeros_like(dT_array)

        ptot = 0.0
        i = 1

        while 1-ptot>params['model_converge_tol'] and i<dT_array.size:
            T = dT_array[i]
            
            for player in attacking_players:
                # calculate ball control probablity for 'player' in time interval T+dt
                dPPCFdT = (1-PPCFatt[i-1]-PPCFdef[i-1])*player.probability_intercept_ball( T ) * player.lambda_att
                
                # make sure it's greater than zero
                assert dPPCFdT>=0, 'Invalid attacking player probability (calculate_pitch_control_at_target)'
                player.PPCF += dPPCFdT*params['int_dt'] # total contribution from individual player
                PPCFatt[i] += player.PPCF # add to sum over players in the attacking team (remembering array element is zero at the start of each integration iteration)
                
            for player in defending_players:
                # calculate ball control probablity for 'player' in time interval T+dt
                dPPCFdT = (1-PPCFatt[i-1]-PPCFdef[i-1])*player.probability_intercept_ball( T ) * player.lambda_def
                
                # make sure it's greater than zero
                assert dPPCFdT>=0, 'Invalid defending player probability (calculate_pitch_control_at_target)'
                
                player.PPCF += dPPCFdT*params['int_dt'] # total contribution from individual player
                PPCFdef[i] += player.PPCF # add to sum over players in the defending team
                
            ptot = PPCFdef[i]+PPCFatt[i] # total pitch control probability
            i += 1

        if i >= dT_array.size:
            print("Integration failed to converge: %1.3f" % (ptot))

        return PPCFatt[i - 1], PPCFdef[i - 1]


def generate_pitch_control_for_event(event_id, events, track_home, track_away, params, GK_numbers, field_dimen=(106., 68.0), n_grid_cells_x = 50, offsides=True):
    pass_frame = events.loc[event_id]['Start Frame']
    pass_team = events.loc[event_id].Team
    ball_start_pos = np.array([events.loc[event_id]['Start X'], events.loc[event_id]['Start Y']])

    if pass_team.lower() == 'home':
        attacking_players = initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[0])
        defending_players = initialise_players(track_away.loc[pass_frame], 'Away', params, GK_numbers[1])
    elif pass_team.lower() == 'away':
        defending_players = initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[0])
        attacking_players = initialise_players(track_away.loc[pass_frame], 'Away', params, GK_numbers[1])
    else:
        assert False, "Teams need to be either home or away"

    if offsides:
        attacking_players = check_offsides(attacking_players, defending_players, ball_start_pos, GK_numbers)

    n_grid_cells_y = int(n_grid_cells_x * field_dimen[1] / field_dimen[0] )
    dx = field_dimen[0] / n_grid_cells_x
    dy = field_dimen[1] / n_grid_cells_y
    xgrid = np.arange(n_grid_cells_x) * dx - field_dimen[0] / 2 + dx / 2
    ygrid = np.arange(n_grid_cells_y) * dy - field_dimen[1] / 2 + dy / 2

    PPCFa = np.zeros( shape=( len(ygrid), len(xgrid) ) )
    PPCFd = np.zeros( shape=( len(ygrid), len(xgrid) ) )

    for i in range( len(ygrid) ):
        for j in range( len(xgrid) ):
            target_pos = np.array( [xgrid[j], ygrid[i]] )
            PPCFa[i,j], PPCFd[i,j] = calculate_pitch_control_at_target(target_pos, attacking_players, defending_players, ball_start_pos, params)
            
    checksum = np.sum(PPCFa + PPCFd) / float(n_grid_cells_x * n_grid_cells_y)

    assert 1 - checksum < params['model_converge_tol'], "Checksum failed: %1.3f" % (1 - checksum)

    return PPCFa, xgrid, ygrid
