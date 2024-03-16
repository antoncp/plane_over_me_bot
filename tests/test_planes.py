from pandas.core.frame import DataFrame

import bot.planes as planes


def test_fetch_plane_list():
    lat = 52.359752
    lon = 4.894353
    plane_list = planes.get_plane_list(lat, lon)
    assert isinstance(plane_list, dict), "Failure to get plane list"
    sort_list = planes.sort_plane_list(plane_list, ground=False)
    assert isinstance(sort_list, DataFrame), "Failure to sort list of planes"
