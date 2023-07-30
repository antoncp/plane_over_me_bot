import pandas as pd
import requests
from bs4 import BeautifulSoup

from main import MAP_KEY, RAPID_API


class AirCraft:
    aircrafts = set()

    def __init__(self, reg, dist, start, end, alt, spd, order):
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
    users = dict()

    def __init__(self, id, lat=None, lon=None, last_map=None, caption=None):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.last_map = last_map
        self.caption = caption
        User.users[self.id] = self


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
        order = i + 1
        if list.iloc[i]["to"] != "nan":
            start = list.iloc[i]["from"]
            end = list.iloc[i]["to"]
        else:
            start = "Departure airport unknown"
            end = "Destination airport unknown"
        AirCraft(reg, dist, start, end, alt, spd, order)
        yield f"({i+1}) {dist} km / {model} / {alt} m / {spd} km/h", reg


def get_plane_photo(reg):
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
    return image, plane_model, date_img, place_img, author_img, url


def plane_details(reg):
    aircraft = next(
        (obj for obj in globals()["AirCraft"].aircrafts if obj.reg == reg),
        None,
    )
    return aircraft


def user_details(id):
    user = globals()["User"].users.get(id)
    return user
