import itertools
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Dict, List, Tuple

import pytz
import requests
from common import (
    PCAT,
    ForecastData,
    ForecastDataEntry,
    WeatherSymbol,
    WeatherValueFloat,
)


@dataclass
class WeatherDataEntry:
    msl: WeatherValueFloat  # Air pressure
    t: WeatherValueFloat  # Air temperature
    vis: WeatherValueFloat  # Horizontal visibility
    wd: WeatherValueFloat  # Wind direction
    ws: WeatherValueFloat  # Wind speed
    r: WeatherValueFloat  # Relative humidity
    tstm: WeatherValueFloat  # Thunder probability
    tcc_mean: WeatherValueFloat  # Mean value of total cloud cover
    lcc_mean: WeatherValueFloat  # Lean value of low level cloud cover
    mcc_mean: WeatherValueFloat  # Mean value of medium level cloud cover
    hcc_mean: WeatherValueFloat  # Mean value of high level cloud cover
    gust: WeatherValueFloat  # Wind gust speed
    pmin: WeatherValueFloat  # Minimum precipitation intensity
    pmax: WeatherValueFloat  # Maximum precipitation intensity
    spp: WeatherValueFloat  # Percent of precipitation in frozen form
    pcat: PCAT  # Precipitation category
    pmean: WeatherValueFloat  # Mean precipitation intensity
    pmedian: WeatherValueFloat  # Median precipitation intensity
    wsymb2: WeatherSymbol  # Weather symbol


class SMHIHelper:
    def __init__(self, lon: float, lat: float, tz: timezone = pytz.UTC) -> None:
        self.lon = lon
        self.lat = lat
        self.hourly_forecasts = {}
        self.tz = tz

    def date_str_to_datetime(self, date_str: str) -> datetime:
        datetime_object = pytz.utc.localize(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ"))
        datetime_as_utc = datetime_object.astimezone(self.tz)
        return datetime_as_utc

    def SMHI_timeSeries_object_to_WeatherDataEntry(
        self,
        obj: str,
    ) -> Tuple[datetime, WeatherDataEntry]:
        valid_time = self.date_str_to_datetime(obj["validTime"])
        data_dict = {
            item["name"]: {"value": item["values"][0], "unit": item["unit"]}
            for item in obj["parameters"]
        }
        return valid_time, WeatherDataEntry(
            msl=WeatherValueFloat(
                value=data_dict.get("msl")["value"],
                unit=data_dict.get("msl")["unit"],
            ),
            t=WeatherValueFloat(
                value=data_dict.get("t")["value"],
                unit=data_dict.get("t")["unit"],
            ),
            vis=WeatherValueFloat(
                value=data_dict.get("vis")["value"],
                unit=data_dict.get("vis")["unit"],
            ),
            wd=WeatherValueFloat(
                value=data_dict.get("wd")["value"],
                unit=data_dict.get("wd")["unit"],
            ),
            ws=WeatherValueFloat(
                value=data_dict.get("ws")["value"],
                unit=data_dict.get("ws")["unit"],
            ),
            r=WeatherValueFloat(
                value=data_dict.get("r")["value"],
                unit=data_dict.get("r")["unit"],
            ),
            tstm=WeatherValueFloat(
                value=data_dict.get("tstm")["value"],
                unit=data_dict.get("tstm")["unit"],
            ),
            tcc_mean=WeatherValueFloat(
                value=data_dict.get("tcc_mean")["value"],
                unit=data_dict.get("tcc_mean")["unit"],
            ),
            lcc_mean=WeatherValueFloat(
                value=data_dict.get("lcc_mean")["value"],
                unit=data_dict.get("lcc_mean")["unit"],
            ),
            mcc_mean=WeatherValueFloat(
                value=data_dict.get("mcc_mean")["value"],
                unit=data_dict.get("mcc_mean")["unit"],
            ),
            hcc_mean=WeatherValueFloat(
                value=data_dict.get("hcc_mean")["value"],
                unit=data_dict.get("hcc_mean")["unit"],
            ),
            gust=WeatherValueFloat(
                value=data_dict.get("gust")["value"],
                unit=data_dict.get("gust")["unit"],
            ),
            pmin=WeatherValueFloat(
                value=data_dict.get("pmin")["value"],
                unit=data_dict.get("pmin")["unit"],
            ),
            pmax=WeatherValueFloat(
                value=data_dict.get("pmax")["value"],
                unit=data_dict.get("pmax")["unit"],
            ),
            spp=WeatherValueFloat(
                value=data_dict.get("spp")["value"],
                unit=data_dict.get("spp")["unit"],
            ),
            pcat=PCAT(data_dict.get("pcat")["value"]),
            pmean=WeatherValueFloat(
                value=data_dict.get("pmean")["value"],
                unit=data_dict.get("pmean")["unit"],
            ),
            pmedian=WeatherValueFloat(
                value=data_dict.get("pmedian")["value"],
                unit=data_dict.get("pmedian")["unit"],
            ),
            wsymb2=WeatherSymbol.from_code(data_dict.get("Wsymb2")["value"]),
        )

    def get_url(self) -> str:
        return (
            "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/"
            + f"2/geotype/point/lon/{self.lon}/lat/{self.lat}/data.json"
        )

    def fetch(self) -> None:
        weather = json.loads(requests.get(self.get_url()).text)
        for time_series in weather["timeSeries"]:
            date_time, forecast = self.SMHI_timeSeries_object_to_WeatherDataEntry(
                time_series
            )
            self.hourly_forecasts[date_time] = forecast

    def get_timestamps(self) -> List[datetime]:
        return sorted(self.hourly_forecasts.keys())

    def get_dates(self) -> List[date]:
        return {
            key: list(group)
            for key, group in itertools.groupby(
                self.get_timestamps(), key=lambda x: x.date()
            )
        }

    def get_current_weather(self) -> Tuple[datetime, WeatherDataEntry]:
        date_time = min(self.get_timestamps())
        return date_time, self.hourly_forecasts[date_time]

    def get_hourly_forecasts_for_date(
        self, date: date
    ) -> Dict[datetime, WeatherDataEntry]:
        return {
            date_time: self.hourly_forecasts[date_time]
            for date_time in self.get_dates()[date]
        }

    def get_forecast_data_entry_for_date(self, date: date) -> ForecastDataEntry:
        forecast_data = self.get_hourly_forecasts_for_date(date=date)
        datetime_series = [key for key in forecast_data]
        min_hour = min([date.hour for date in datetime_series])
        if min_hour > 14:
            symbol = forecast_data[datetime_series[0]].wsymb2
            ws = forecast_data[datetime_series[0]].ws
            wd = forecast_data[datetime_series[0]].wd
            gust = forecast_data[datetime_series[0]].gust
        else:
            symbol = next(
                value.wsymb2 for key, value in forecast_data.items() if key.hour == 14
            )
            ws = next(
                value.ws for key, value in forecast_data.items() if key.hour == 14
            )
            wd = next(
                value.wd for key, value in forecast_data.items() if key.hour == 14
            )
            gust = next(
                value.gust for key, value in forecast_data.items() if key.hour == 14
            )
        return ForecastDataEntry(
            date=date,
            symbol=symbol,
            t=ForecastData(
                [forecast_data[key].t.value for key in forecast_data],
                forecast_data[next(iter(forecast_data))].t.unit,
            ),
            ws=ws,
            wd=wd,
            gust=gust,
        )
