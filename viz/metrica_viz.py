from viz import pitch_viz as pviz
import numpy as np
import matplotlib.animation as animation

def plot_events(events, figax=None, pitchSize=(106, 68), indicators=['Marker', 'Arrow'], color='r', marker_style='o',
                alpha=0.5, annotate=False):
    if figax is None:
        (figaxplt, pdimen) = pviz.createPitch(pitchSize[0], pitchSize[1])
        (fig, ax, plt) = figaxplt
    else:
        fig, ax = figax

    for i, row in events.iterrows():
        if 'Marker' in indicators:
            ax.plot(row['Start X'], row['Start Y'], alpha=alpha)

        if 'Arrow' in indicators:
            ax.annotate("", xy=row[['End X', 'End Y']], xytext=row[['Start X', 'Start Y']], alpha=alpha,
                        arrowprops=dict(alpha=alpha, width=0.5, headlength=4.0, color=color), annotation_clip=False)

        if annotate:
            textstring = row['Type'] + ': ' + row['From']
            ax.text(row['Start X'], row['Start Y'], textstring, fontsize=10, color=color)

    return fig, ax


def plot_frame(homeTeam, awayTeam, figax=None, teamColors=('r', 'b'), pitchSize=(106, 68), inc_plr_vel=False,
               PlayerMarkerSize=10, PlayerAlpha=0.7, annotate=False):
    if figax is None:
        (figaxplt, pdimen) = pviz.createPitch(pitchSize[0], pitchSize[1])
        (fig, ax, plt) = figaxplt
    else:
        fig, ax = figax

    for team, color in zip([homeTeam, awayTeam], teamColors):
        x_columns = [c for c in team.keys() if c[-2:].lower() == '_x' and c != 'ball_x']
        y_columns = [c for c in team.keys() if c[-2:].lower() == '_y' and c != 'ball_y']
        ax.plot(team[x_columns], team[y_columns], color + 'o', MarkerSize=PlayerMarkerSize, alpha=PlayerAlpha)
        if inc_plr_vel:
            vx_columns = ['{}_vx'.format(c[:-2]) for c in x_columns]
            vy_columns = ['{}_vy'.format(c[:-2]) for c in y_columns]
            ax.quiver(team[x_columns], team[y_columns], team[vx_columns], team[vy_columns], color=color,
                      scale_units='inches', scale=10, width=0.0015, headlength=5, headwidth=3, alpha=PlayerAlpha)
        if annotate:
            [ax.text(team[x] + 0.5, team[y] + 0.5, x.split('_'), fontsize=10, color=color) for x, y in
             zip(x_columns, y_columns) if not (np.isnan(team[x]) or np.isnan(team[y]))]

    ax.plot(homeTeam['ball_x'], homeTeam['ball_y'], 'ko', MarkerSize=6, LineWidth=0)

    return fig, ax


def save_match_clip(home, away, fpath, fname="clip_test", figax=None, frames_per_second=25, team_colors=('r', 'b'), field_dimen=(106.0, 68.0), include_player_velocities=False, PlayerMarkerSize=10, PlayerAlpha=0.7):
    assert np.all(home.index == away.index)

    index = home.index

    FFMpegWriter = animation.writers['ffmpeg']

    metadata = dict(title='Tracking Data', artist='Matplotlib', comment='Metrica tracking data clip')
    writer = FFMpegWriter(fps=frames_per_second, metadata=metadata)

    fname = fpath + '/' + fname + '.mp4'

    if figax is None:
        (figaxplt, pdimen) = pviz.createPitch(width=field_dimen[0], height=field_dimen[1])
        (fig, ax, plt) = figaxplt

    else:
        fig, ax = figax

    fig.set_tight_layout(True)

    print("Generating movie...", end='')

    with writer.saving(fig, fname, 100):
        for i in index:
            figobjs = []

            for team, color in zip( [home.loc[i], away.loc[i]], team_colors):
                x_columns = [c for c in team.keys() if c[-2:] == '_x' and c != 'ball_x']
                y_columns = [c for c in team.keys() if c[-2:] == '_y' and c != 'ball_y']

                objs, = ax.plot(team[x_columns], team[y_columns], color + 'o', MarkerSize=PlayerMarkerSize, alpha=PlayerAlpha)
                figobjs.append(objs)
                
                if include_player_velocities:
                    vx_columns = ['{}_vx'.format(c[-2:]) for c in x_columns]
                    vy_columns = ['{}_vy'.format(c[-2:]) for c in y_columns]

                    objs = ax.quiver(team[x_columns], team[y_columns], team[vx_columns], team[vy_columns], color=color, scale_units='inches', scale=10, width=0.0015, headlength=5, headwidth=3, alpha=PlayerAlpha)
                    figobjs.append(objs)

            objs, = ax.plot(team['ball_x'], team['ball_y'], 'ko', MarkerSize=6, alpha=1.0, LineWidth=0)
            figobjs.append(objs)

            frame_minute = int(team['Time [s]'] / 60)
            frame_second = ( team['Time [s]'] / 60. - frame_minute) * 60.
            timestring = "%d:%1.2f" % (frame_minute, frame_second)
            objs = ax.text(-2.5, field_dimen[1]/2.+1, timestring, fontsize=14)
            figobjs.append(objs)
            
            writer.grab_frame()
            
            for figobj in figobjs:
                figobj.remove()
    
    print("done")
    plt.clf()
    plt.close(fig)