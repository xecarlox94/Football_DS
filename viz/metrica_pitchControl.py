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