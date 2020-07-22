import numpy as np



class Player(object):
    def __init__(self, pid, team, teamname, params, GKid):
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

    def probability_intercept_the_ball(self, T):
        return 1 / (1. + np.exp( -np.pi / np.sqrt(3.0) / self.tti_sigma * ( T - self.time_to_intercept) ) )



def initialise_players(team, teamname, params, GKid):
    player_ids = np.unique( [c.split('_')[1] for c in team.keys() if c[:4] == teamname ] )

    team_players = []
    for player in player_ids:
        p = Player(player, team, teamname, params, GKid)
        if p.inframe:
            team_players.append(p)

    return team_players


def default_model_params(time_to_control_veto=3):
    params = {}
    params['max_player_accel'] = 7.
    params['max_player_speed'] = 5.
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
    params['time_to_control_att'] = time_to_control_veto * np.log(10) * ( np.sqrt(3) * params['tti_sigma'] / np.pi + 1 / params['lambda_def'] )

    return params


def check_offsides( attacking_players, defending_players, ball_position, GK_numbers, verbose=False, tol=0.2):
    defending_GK_id = GK_numbers[1] if attacking_players[0].teamname == "Home" else GK_numbers[0]

    assert defending_GK_id in [ p.id for p in defending_players ]

    defending_GK = [p for p in defending_players if p.id == defending_GK_id][0]
    
    defending_half = np.sign(defending_GK.position[0])
    
    deepest_defender_x = sorted( [p.position[0]*defending_half for p in defending_players if not p.id == defending_GK.id], reverse=True)

    tol *= defending_half
    ball_pos = ball_position * defending_half

    offside_line = max(deepest_defender_x, ball_pos, 0.0) + tol

    if verbose:
        for p in attacking_players:
            if p.position[0] * defending_half > offside_line:
                print( "player %s in %s team is offside" % (p.id, p.playername) )

    attacking_players = [p for p in attacking_players if p.position[0] * defending_half <= offside_line]

    return attacking_players


def calculate_pitch_control_at_target(target_position, attacking_players, defending_players, ball_start_position, params):
    pass

def generate_pitch_control_for_event(event_id, events, track_home, track_away, params, GK_numbers, field_dimen=(106., 68.0), n_grid_cells_x = 50, offsides=True):
    pass_frame = events.loc[event_id]['Start Frame']
    pass_team = events.loc[event_id].Team
    ball_start_pos = np.array([events.loc[event_id]['Start X'], events.loc[event_id]['Start Y']])

    if pass_team.lower() == 'home':
        attacking_players = initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[0])
        defending_players = initialise_players(track_away.loc[pass_frame], 'Away', params, GK_numbers[1])
    elif pass_team.lower() == 'away':
        defending_players = initialise_players(track_away.loc[pass_frame], 'Away', params, GK_numbers[1])
        attacking_players = initialise_players(track_home.loc[pass_frame], 'Home', params, GK_numbers[0])
    else:
        assert False, "Teams need to be either home or away"

    if offsides:
        attacking_players = check_offsides(attacking_players, defending_players, ball_start_pos, GK_numbers)

    n_grid_cells_y = int(n_grid_cells_x * field_dimen[1] / field_dimen[0] )
    dx = field_dimen[0] / n_grid_cells_x
    dy = field_dimen[1] / n_grid_cells_y
    xgrid = np.arange(n_grid_cells_x) * dx - field_dimen[0] / 2 + dx / 2
    ygrid = np.arange(n_grid_cells_y) * dy - field_dimen[1] / 2 + dy / 2

    for i in range( len(ygrid) ):
        for j in range( len(xgrid) ):
            target_pos = np.array( [xgrid[j], ygrid[i]] )
            PPCFa[i,j], PPCFd[i,j] = calculate_pitch_control_at_target(target_pos, attacking_players, defending_players, ball_start_pos, params)
            
    checksum = np.sum(PPCFa + PPCFd) / float(n_grid_cells_x * n_grid_cells_y)

    assert 1 - checksum < params['model_converge_tol'], "Checksum failed: %1.3f" % (1 - checksum)

    return PPCFa, xgrid, ygrid

