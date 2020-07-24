

import numpy as np

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

        nx, ny = EPV.shape

        dx = field_dimen[0] / float(nx)
        dy = field_dimen[1] / float(ny)
