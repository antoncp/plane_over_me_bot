import requests
import pandas as pd

from main import RAPID_API, MAP_KEY


class AirCraft:

    aircrafts = set()

    def __init__(
        self,
        reg,
        start,
        end,
    ):
        self.reg = reg
        self.start = start
        self.end = end
        AirCraft.aircrafts.add(self)

    def __str__(self):
        return self.id


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
    planes = (
        "https://maps.googleapis.com/maps/api/staticmap?&size=700x700"
        f"&maptype=satellite&markers=color:gray%7Clabel:0%7C{lat},{lon}&"
    )
    for i in range(min(5, list.shape[0])):
        plane = f"{list.iloc[i]['lat']},{list.iloc[i]['lon']}"
        planes += f"markers=color:blue%7Clabel:{i+1}%7C{plane}&"

    map = planes + f"key={MAP_KEY}"
    return map


def get_plane_selector(list):
    for i in range(min(5, list.shape[0])):
        model = list.iloc[i]["type"]
        reg = list.iloc[i]["reg"]
        dist = float(round(list.iloc[i]["dst"] * 1.852, 2))
        alt = int(round(list.iloc[i]["alt"] / 3.281, 0))
        spd = int(round(list.iloc[i]["spd"] * 1.852, 0))
        start = list.iloc[i]["from"]
        end = list.iloc[i]["to"]
        aircraft = AirCraft(reg, start, end)
        yield f"{i+1}) {model} / {alt} m / {spd} km/h", reg


def plane_details(reg):
    aircraft = next(
        (obj for obj in globals()['AirCraft'].aircrafts if obj.reg == reg),
        None,
    )
    return aircraft
