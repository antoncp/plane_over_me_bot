import requests
import pandas as pd

from main import RAPID_API, MAP_KEY


def get_plane_list(lat, lon):
    url = (
        "https://adsbx-flight-sim-traffic.p.rapidapi.com/"
        f"api/aircraft/json/lat/{lat}/lon/{lon}/dist/25/"
    )
    headers = {
        "X-RapidAPI-Key": RAPID_API,
        "X-RapidAPI-Host": "adsbx-flight-sim-traffic.p.rapidapi.com",
    }
    return requests.request("GET", url, headers=headers).json()


def sort_plane_list(plane_list):
    list = pd.DataFrame(plane_list["ac"])
    list = list[
        (list["alt"] != "")
        & (list["spd"] != "")
        & (list["reg"] != "")
        & (list["dst"] != "")
    ]
    list = list.astype(
        {
            "dst": float,
            "spd": float,
            "alt": int,
            "from": str,
            "to": str,
            "lon": float,
            "lat": float,
        }
    )
    list = list[
        (list["dst"] < 20)
        & (list["alt"] > 200)
        & ~((list["alt"] > 1000) & (list["spd"] < 60))
    ]
    return list.sort_values(by="dst")


def plane_map(lat, lon, list):
    plane_1 = f"{list.iloc[0]['lat']},{list.iloc[0]['lon']}"
    plane_2 = f"{list.iloc[1]['lat']},{list.iloc[1]['lon']}"
    plane_3 = f"{list.iloc[2]['lat']},{list.iloc[2]['lon']}"
    map = (
        "https://maps.googleapis.com/maps/api/staticmap?&size=700x700"
        f"&maptype=satellite&markers=color:gray%7Clabel:0%7C{lat},{lon}&"
        f"markers=color:red%7Clabel:1%7C{plane_1}&markers=color:blue%7"
        f"Clabel:2%7C{plane_2}&markers=color:yellow%7Clabel:"
        f"3%7C{plane_3}&key={MAP_KEY}"
    )
    return map
