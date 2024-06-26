from dataclasses import dataclass
from typing import Dict, Generator, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas.core.frame import DataFrame

from config import RedisDataSharing, logger, settings

from .db import read_user, save_coordinates, save_user
from .utils import timing_log

RAPID_API = settings.RAPID_API
MAP_KEY = settings.MAP_KEY


class AirCraft:
    """The class for the aircraft's properties like altitude, velocity,
    registration number etc.
    """

    aircrafts = set()
    airphotos = dict()

    def __init__(self, id, reg, dist, start, end, alt, spd, order):
        self.id = id
        self.reg = reg
        self.dist = dist
        self.start = start
        self.end = end
        self.alt = alt
        self.spd = spd
        self.order = order
        AirCraft.aircrafts.add(self)

    def __str__(self):
        return self.id


class User:
    """The class used to store user information such as location or previously
    viewed maps.
    """

    users = dict()

    def __init__(self, id, lat=None, lon=None, saved=False):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.saved = saved
        self.last_map = {}
        self.caption = {}
        User.users[self.id] = self

    def save_to_db(self):
        record_user = read_user(self.id)
        if not record_user:
            self.saved = True
            user_to_db = dict(self.__dict__)
            del user_to_db["last_map"]
            del user_to_db["caption"]
            del user_to_db["saved"]
            save_user(user_to_db)

    def update_coordinates(self, lat, lon):
        if self.lat != lat or self.lon != lon:
            self.lat = lat
            self.lon = lon
            save_coordinates(self.id, lat, lon)


@dataclass
class AirPhoto:
    """The class to store images associated with AirCraft objects."""

    image: str
    plane_model: str
    date_img: str
    place_img: str
    author_img: str
    url: str

    def __post_init__(self):
        RedisDataSharing.last_plane_image = self.image
        RedisDataSharing.plane_model = self.plane_model
        RedisDataSharing.last_plane_url = self.url
        RedisDataSharing.last_plane_photo_author = self.author_img


@timing_log()
def get_plane_list(lat: int, lon: int) -> Dict:
    url = (
        "https://adsbx-flight-sim-traffic.p.rapidapi.com/"
        f"api/aircraft/json/lat/{lat}/lon/{lon}/dist/25/"
    )
    headers = {
        "X-RapidAPI-Key": RAPID_API,
        "X-RapidAPI-Host": "adsbx-flight-sim-traffic.p.rapidapi.com",
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.warning("Timeout on request to RapidAPI")
        return None
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request to RapidAPI failed: {e}")
        return None


def sort_plane_list(plane_list: Dict, ground: bool) -> DataFrame:
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
        },
        errors="ignore",
    )
    if not ground:
        list = list[(list["spd"] > 80) & (list["alt"] > 200)]
    list = list.sort_values(by="dst")
    return list


def plane_map(lat: int, lon: int, list: DataFrame) -> str:
    planes = (
        "https://maps.googleapis.com/maps/api/staticmap?&size=700x700"
        f"&maptype=satellite&markers=color:gray%7Clabel:0%7C{lat},{lon}&"
    )
    for i in range(min(5, list.shape[0])):
        plane = f"{list.iloc[i]['lat']},{list.iloc[i]['lon']}"
        planes += f"markers=color:blue%7Clabel:{i+1}%7C{plane}&"

    map = planes + f"key={MAP_KEY}"
    RedisDataSharing.last_map = map
    return map


def get_plane_selector(
    list: DataFrame, prefix: str
) -> Generator[str, None, None]:
    for i in range(min(5, list.shape[0])):
        model = list.iloc[i]["type"]
        reg = list.iloc[i]["reg"]
        dist = float(round(list.iloc[i]["dst"] * 1.852, 2))
        alt = int(round(list.iloc[i]["alt"] / 3.281, 0))
        spd = int(round(list.iloc[i]["spd"] * 1.852, 0))
        order = i + 1
        if list.iloc[i]["to"] != "nan":
            start = list.iloc[i]["from"]
            end = list.iloc[i]["to"]
        else:
            start = "Departure airport unknown"
            end = "Destination airport unknown"
        id = f"{prefix}&{reg}"
        AirCraft(id, reg, dist, start, end, alt, spd, order)
        yield f"({i+1}) {dist} km / {model} / {alt} m / {spd} km/h", id


@timing_log(extra_log=True)
def get_plane_photo(reg: str) -> tuple:
    saved_plane = plane_photo_details(reg)
    if saved_plane:
        return saved_plane
    url = f"https://www.jetphotos.com/registration/{reg}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    image = f"https:{soup.find_all('img')[3]['src']}"
    plane_model = soup.select(
        "#results > div:nth-child(1) > div.result__section.result"
        "__section--info-wrapper > section.desktop-only.desktop-only"
        "--block > ul > li:nth-child(3) > span > a"
    )[0].text
    date_img = soup.select(
        "#results > div:nth-child(1) > div.result__section.result__"
        "section--info-wrapper > section.desktop-only.desktop-only--"
        "block > ul > li:nth-child(5) > span > a"
    )[0].text
    place_img = soup.select(
        "#results > div:nth-child(1) > div.result__section.result__"
        "section--info2-wrapper > ul:nth-child(1) > li > span > a"
    )[0].text
    author_img = soup.select(
        "#results > div:nth-child(1) > div.result__section.result__"
        "section--info2-wrapper > ul:nth-child(2) > li > span.result__"
        "infoListText.result__infoListText--photographer > a"
    )[0].text
    extra_log = {"Requested URL": url, "Author": author_img}
    plane = AirPhoto(image, plane_model, date_img, place_img, author_img, url)
    AirCraft.airphotos[reg] = plane
    return plane, extra_log


def plane_details(id: str) -> Optional[AirCraft]:
    aircraft = next(
        (obj for obj in globals()["AirCraft"].aircrafts if obj.id == id),
        None,
    )
    return aircraft


def plane_photo_details(reg: str) -> Optional[AirPhoto]:
    plane = AirCraft.airphotos.get(reg)
    return plane


def user_details(id: int) -> Optional[User]:
    user = User.users.get(id)
    if not user:
        user = read_user(id)
        if user:
            user = User(
                user.get("id"), user.get("lat"), user.get("lon"), saved=True
            )
    return user
