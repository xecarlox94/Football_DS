import numpy as np


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