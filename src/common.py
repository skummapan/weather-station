from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import List


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


@dataclass
class WeatherValueFloat:
    value: float
    unit: str


@dataclass
class ForecastData:
    _values: List[float]
    unit: str

    def __iter__(self):
        yield from self._values

    def __len__(self):
        return len(self._values)


@dataclass
class ForecastDataEntry:
    date: date
    symbol: WeatherSymbol
    t: ForecastData  # Mean temperature
    ws: WeatherValueFloat  # Mean wind speed
    wd: WeatherValueFloat  # Mean wind direction
    gust: WeatherValueFloat  # Mean gust speed
