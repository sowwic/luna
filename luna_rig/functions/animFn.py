import pymel.core as pm


def get_playback_range():
    time_range = (int(pm.playbackOptions(min=1, q=1)), int(pm.playbackOptions(max=1, q=1)))
    return time_range
