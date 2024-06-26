import requests
import json
import pytz
from datetime import datetime, date, timedelta
from enum import Enum
import itertools
from typing import TypedDict, Optional, Tuple


class WeatherSymbol(Enum):
    CLEAR_SKY = (1, "☀️")
    NEARLY_CLEAR_SKY = (2, "🌤️")
    VARIABLE_CLOUDINESS = (3, "⛅")
    HALFCLEAR_SKY = (4, "🌥️")
    CLOUDY_SKY = (5, "☁️")
    OVERCAST = (6, "🌧️")
    FOG = (7, "🌫️")
    LIGHT_RAIN_SHOWERS = (8, "🌦️")
    MODERATE_RAIN_SHOWERS = (9, "🌧️")
    HEAVY_RAIN_SHOWERS = (10, "🌧️🌧️")
    THUNDERSTORM = (11, "⛈️")
    LIGHT_SLEET_SHOWERS = (12, "🌨️")
    MODERATE_SLEET_SHOWERS = (13, "🌨️🌨️")
    HEAVY_SLEET_SHOWERS = (14, "🌨️🌨️🌨️")
    LIGHT_SNOW_SHOWERS = (15, "🌨️")
    MODERATE_SNOW_SHOWERS = (16, "🌨️🌨️")
    HEAVY_SNOW_SHOWERS = (17, "🌨️🌨️🌨️")
    LIGHT_RAIN = (18, "🌧️")
    MODERATE_RAIN = (19, "🌧️🌧️")
    HEAVY_RAIN = (20, "🌧️🌧️🌧️")
    THUNDER = (21, "⚡")
    LIGHT_SLEET = (22, "🌨️")
    MODERATE_SLEET = (23, "🌨️🌨️")
    HEAVY_SLEET = (24, "🌨️🌨️🌨️")
    LIGHT_SNOWFALL = (25, "❄️")
    MODERATE_SNOWFALL = (26, "❄️❄️")
    HEAVY_SNOWFALL = (27, "❄️❄️❄️")

    def __init__(self, code: int, icon: str):
        self.code = code
        self.icon = icon

    @classmethod
    def from_code(cls, code: int):
        for symbol in cls:
            if symbol.code == code:
                return symbol
        raise ValueError(f"No matching weather symbol for code: {code}")


class PCAT(Enum):
    """Precipitation Category (pcat)

    The precipitation category parameter value is an integer with a value range of 0 to 6.
    The values represent the following:
    """

    NO_PRECIPITATION = 0
    SNOW = 1
    SNOW_AND_RAIN = 2
    RAIN = 3
    DRIZZLE = 4
    FREEZING_RAIN = 5
    FREEZING_DRIZZLE = 6


class WeatherValueFloat(TypedDict):
    value: Optional[float]
    unit: str


class WeatherValueInt(TypedDict):
    value: Optional[int]
    unit: str


class WeatherValuePCAT(TypedDict):
    value: Optional[PCAT]
    unit: str


class WeatherValueWeatherSymbol(TypedDict):
    value: Optional[WeatherSymbol]
    unit: str


class WeatherDataEntry(TypedDict):
    msl: WeatherValueFloat  # Air pressure
    t: WeatherValueFloat  # Air temperature
    vis: WeatherValueFloat  # Horizontal visibility
    wd: WeatherValueInt  # Wind direction
    ws: WeatherValueFloat  # Wind speed
    r: WeatherValueInt  # Relative humidity
    tstm: WeatherValueInt  # Thunder probability
    tcc_mean: WeatherValueInt  # Mean value of total cloud cover
    lcc_mean: WeatherValueInt  # Lean value of low level cloud cover
    mcc_mean: WeatherValueInt  # Mean value of medium level cloud cover
    hcc_mean: WeatherValueInt  # Mean value of high level cloud cover
    gust: WeatherValueFloat  # Wind gust speed
    pmin: WeatherValueFloat  # Minimum precipitation intensity
    pmax: WeatherValueFloat  # Maximum precipitation intensity
    spp: WeatherValueInt  # Percent of precipitation in frozen form
    pcat: WeatherValuePCAT  # Precipitation category
    pmean: WeatherValueFloat  # Mean precipitation intensity
    pmedian: WeatherValueFloat  # Median precipitation intensity
    Wsymb2: WeatherValueWeatherSymbol  # Weather symbol


def date_str_to_datetime(date_str: str) -> datetime:
    datetime_object = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return datetime_object.replace(tzinfo=pytz.UTC)


def SMHI_timeSeries_object_to_WeatherDataEntry(
    obj: str,
) -> Tuple[datetime, WeatherDataEntry]:
    valid_time = date_str_to_datetime(obj["validTime"])
    data_dict = {
        item["name"]: {"value": item["values"][0], "unit": item["unit"]}
        for item in obj["parameters"]
    }
    return valid_time, WeatherDataEntry(
        {
            "msl": {
                "value": data_dict.get("msl")["value"],
                "unit": data_dict.get("msl")["unit"],
            },
            "t": {
                "value": data_dict.get("t")["value"],
                "unit": data_dict.get("t")["unit"],
            },
            "vis": {
                "value": data_dict.get("vis")["value"],
                "unit": data_dict.get("vis")["unit"],
            },
            "wd": {
                "value": data_dict.get("wd")["value"],
                "unit": data_dict.get("wd")["unit"],
            },
            "ws": {
                "value": data_dict.get("ws")["value"],
                "unit": data_dict.get("ws")["unit"],
            },
            "r": {
                "value": data_dict.get("r")["value"],
                "unit": data_dict.get("r")["unit"],
            },
            "tstm": {
                "value": data_dict.get("tstm")["value"],
                "unit": data_dict.get("tstm")["unit"],
            },
            "tcc_mean": {
                "value": data_dict.get("tcc_mean")["value"],
                "unit": data_dict.get("tcc_mean")["unit"],
            },
            "lcc_mean": {
                "value": data_dict.get("lcc_mean")["value"],
                "unit": data_dict.get("lcc_mean")["unit"],
            },
            "mcc_mean": {
                "value": data_dict.get("mcc_mean")["value"],
                "unit": data_dict.get("mcc_mean")["unit"],
            },
            "hcc_mean": {
                "value": data_dict.get("hcc_mean")["value"],
                "unit": data_dict.get("hcc_mean")["unit"],
            },
            "gust": {
                "value": data_dict.get("gust")["value"],
                "unit": data_dict.get("gust")["unit"],
            },
            "pmin": {
                "value": data_dict.get("pmin")["value"],
                "unit": data_dict.get("pmin")["unit"],
            },
            "pmax": {
                "value": data_dict.get("pmax")["value"],
                "unit": data_dict.get("pmax")["unit"],
            },
            "spp": {
                "value": data_dict.get("spp")["value"],
                "unit": data_dict.get("spp")["unit"],
            },
            "pcat": {
                "value": PCAT(data_dict.get("pcat")["value"]),
                "unit": data_dict.get("pcat")["unit"],
            },
            "pmean": {
                "value": data_dict.get("pmean")["value"],
                "unit": data_dict.get("pmean")["unit"],
            },
            "pmedian": {
                "value": data_dict.get("pmedian")["value"],
                "unit": data_dict.get("pmedian")["unit"],
            },
            "Wsymb2": {
                "value": WeatherSymbol.from_code(data_dict.get("Wsymb2")["value"]),
                "unit": data_dict.get("Wsymb2")["unit"],
            },
        }
    )


class SMHIHelper:
    def __init__(self, lon: float, lat: float) -> None:
        self.lon = lon
        self.lat = lat
        self.hourly_forecasts = {}

    def get_url(self) -> str:
        return f"https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{self.lon}/lat/{self.lat}/data.json"

    def fetch(self) -> None:
        weather = json.loads(requests.get(self.get_url()).text)
        for time_series in weather["timeSeries"]:
            time, forecast = SMHI_timeSeries_object_to_WeatherDataEntry(time_series)
            self.hourly_forecasts[time] = forecast

    def get_timestamps(self):
        return sorted(self.hourly_forecasts.keys())

    def get_dates(self):
        return {
            key: list(group)
            for key, group in itertools.groupby(
                self.get_timestamps(), key=lambda x: x.date()
            )
        }

    def get_current_weather(self) -> Tuple[datetime, WeatherDataEntry]:
        time = min(self.get_timestamps())
        return time, self.hourly_forecasts[time]

    def get_hourly_forecasts_for_date(
        self, date: date
    ) -> dict[datetime:WeatherDataEntry]:
        return {
            date_time: self.hourly_forecasts[date_time]
            for date_time in self.get_dates()[date]
        }


def get_weather():
    weather = SMHIHelper(15.580572, 58.381857)
    weather.fetch()
    today = date.today()
    tomorrow = today + timedelta(days=1)
    test = weather.get_hourly_forecasts_for_date(tomorrow)
    print(weather.get_current_weather())


if __name__ == "__main__":
    get_weather()
