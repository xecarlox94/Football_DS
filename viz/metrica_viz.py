from viz import pitch_viz as pviz
import numpy as np
import matplotlib.animation as animation
import metrica_IO as mio

def plot_events(events, figax=None, pitchSize=(106, 68), indicators=['Marker', 'Arrow'], color='r', marker_style='o', alpha=0.5, annotate=False):
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


def plot_frame(homeTeam, awayTeam, figax=None, teamColors=('r', 'b'), pitchSize=(106, 68), include_player_velocities=False, PlayerMarkerSize=10, PlayerAlpha=0.7, annotate=False):
    if figax is None:
        (figaxplt, pdimen) = pviz.createPitch(pitchSize[0], pitchSize[1])
        (fig, ax, plt) = figaxplt
    else:
        fig, ax = figax

    for team, color in zip([homeTeam, awayTeam], teamColors):
        x_columns = [c for c in team.keys() if c[-2:].lower() == '_x' and c != 'ball_x']
        y_columns = [c for c in team.keys() if c[-2:].lower() == '_y' and c != 'ball_y']
        ax.plot(team[x_columns], team[y_columns], color + 'o', MarkerSize=PlayerMarkerSize, alpha=PlayerAlpha)
        if include_player_velocities:
            vx_columns = ['{}_vx'.format(c[:-2]) for c in x_columns]
            vy_columns = ['{}_vy'.format(c[:-2]) for c in y_columns]
            ax.quiver(team[x_columns], team[y_columns], team[vx_columns], team[vy_columns], color=color,
                      scale_units='inches', scale=10, width=0.0015, headlength=5, headwidth=3, alpha=PlayerAlpha)
        if annotate:
            [ax.text(team[x] + 0.5, team[y] + 0.5, x.split('_')[1], fontsize=10, color=color) for x, y in zip(x_columns, y_columns) if not (np.isnan(team[x]) or np.isnan(team[y]))]
            
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
    
    print("Generating video...", end='')
    

    with writer.saving(fig, fname, 100):
        for i in index:
            figobjs = []

            for team, color in zip( [home.loc[i], away.loc[i]], team_colors):
                x_columns = [c for c in team.keys() if c[-2:] == '_x' and c != 'ball_x']
                y_columns = [c for c in team.keys() if c[-2:] == '_y' and c != 'ball_y']

                objs, = ax.plot(team[x_columns], team[y_columns], color + 'o', MarkerSize=PlayerMarkerSize, alpha=PlayerAlpha)
                figobjs.append(objs)
                
                if include_player_velocities:
                    vx_columns = [ '{}_vx'.format(c[:-2]) for c in x_columns]
                    vy_columns = [ '{}_vy'.format(c[:-2]) for c in y_columns]
                    
                    objs = ax.quiver(team[x_columns], team[y_columns], team[vx_columns], team[vy_columns], color=color, scale_units='inches', scale=10, width=0.0015, headlength=5, headwidth=3, alpha=PlayerAlpha)
                    
                    
                    figobjs.append(objs)

            objs, = ax.plot(team['ball_x'], team['ball_y'], 'ko', MarkerSize=6, alpha=1.0, LineWidth=0)
            figobjs.append(objs)

            frame_minute = int(team['Time [s]'] / 60)
            frame_second = ( team['Time [s]'] / 60. - frame_minute) * 60.
            timestring = "%d:%1.2f    frame: %d" % (frame_minute, frame_second, i)
            objs = ax.text(-2.5, field_dimen[1]/2.+1, timestring, fontsize=14)
            figobjs.append(objs)
            
            writer.grab_frame()
            
            for figobj in figobjs:
                figobj.remove()
                
    print("done")
    plt.clf()
    plt.close(fig)


def plot_event_pitch_control(eventid, events, track_home, track_away, PPFC, alpha=0.7, include_player_velocities=True, annotate=False, field_dimen=(106.0,68)):
    pass_frame = events.loc[eventid]['Start Frame']
    pass_team = events.loc[eventid].Team

    ((fig,ax,_), _) = pviz.createPitch(field_dimen[0], field_dimen[1])

    plot_frame(track_home.loc[pass_frame], track_away.loc[pass_frame], figax=(fig, ax), PlayerAlpha=alpha, include_player_velocities=include_player_velocities, annotate=annotate)
    plot_events(events.loc[eventid:eventid], figax=(fig,ax), pitchSize=field_dimen, annotate=False, color='k', alpha=1, indicators = ['Marker','Arrow'])

    if pass_team == 'Home':
        cmap = 'bwr'
    else:
        cmap = 'bwr_r'
        
    ax.imshow(np.flipud(PPFC), extent=(-field_dimen[0]/2., field_dimen[0]/2., -field_dimen[1]/2., field_dimen[1]/2.),interpolation='spline36', vmin=0, vmax=1.0, cmap=cmap, alpha=0.5)

    return fig, ax


def plot_EPV_for_event(event_id, events, track_home, track_away, PPCF, EPV, alpha=0.7, include_player_velocities=True, annotate=False, autoscale=.1, contours=False, field_dimen = (106.0,68)):

    pass_frame = events.loc[event_id]['Start Frame']
    pass_team = events.loc[event_id].Team

    ((fig, ax, _), _) = pviz.createPitch(field_dimen[0], field_dimen[1])
    
    plot_frame(track_home.loc[pass_frame], track_away.loc[pass_frame], figax=(fig, ax), PlayerAlpha=alpha, include_player_velocities=include_player_velocities, annotate=annotate)
    plot_events(events.loc[event_id:event_id], figax=(fig, ax), color='k', alpha=1)

    if pass_team == 'Home':
        cmap = 'Reds'
        lcolor = 'r'
        EPV = np.fliplr(EPV) if mio.find_playing_position(track_home, 'Home') == -1 else EPV
    else:
        cmap = 'Blues'
        lcolor = 'b'
        EPV = np.fliplr(EPV) if mio.find_playing_position(track_away, 'Away') == -1 else EPV

    EPVxPPCF = EPV * PPCF

    if autoscale is True:
        vmax = np.max(EPVxPPCF) * 2
    elif autoscale >= 0 and autoscale <= 1:
        vmax = autoscale
    else:
        assert False, "'autoscale' must be either {True or between 0 and 1}"

    ax.imshow(np.flipud(EPVxPPCF), extent=(-field_dimen[0]/2., field_dimen[0]/2., -field_dimen[1]/2., field_dimen[1]/2.), interpolation='spline36', vmin=0.0, vmax=vmax, cmap=cmap, alpha=0.7)
    
    if contours:
        ax.contour(EPVxPPCF, extent=(-field_dimen[0]/2., field_dimen[0]/2., -field_dimen[1]/2., field_dimen[1]/2.), levels=np.array([0.75])*np.max(EPVxPPCF), colors=lcolor, alpha=1.0)

    return fig, ax

def plot_EPV(EPV, field_dimen=(106.0,68), attack_direction=1):

    if attack_direction == -1:
        EPV = np.fliplr(EPV)

    ny, nx = EPV.shape

    ((fig, ax, _), _) = pviz.createPitch(field_dimen[0], field_dimen[1])

    ax.imshow(EPV, extent=(-field_dimen[0]/2., field_dimen[0]/2., -field_dimen[1]/2., field_dimen[1]/2.), vmin=0.0, vmax=0.6, cmap='Blues', alpha=0.6)

    return fig, ax