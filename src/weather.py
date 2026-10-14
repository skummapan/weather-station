import itertools
import logging
from datetime import UTC, date, datetime, timezone

import aiohttp
from pydantic import BaseModel

from .common import (
    ForecastData,
    ForecastDataEntry,
    WeatherSymbol,
    WeatherValueFloat,
)

LOGGER = logging.getLogger(__name__)


class WeatherDataEntry(BaseModel):
    t: WeatherValueFloat  # Air temperature
    wd: WeatherValueFloat  # Wind direction
    ws: WeatherValueFloat  # Wind speed
    gust: WeatherValueFloat  # Wind gust speed
    pmean: WeatherValueFloat  # Mean precipitation amount
    wsymb2: WeatherSymbol  # Weather symbol


class SMHIHelper:
    def __init__(self, lon: float, lat: float, tz: timezone = UTC) -> None:
        self.lon = lon
        self.lat = lat
        self.hourly_forecasts: dict[datetime, WeatherDataEntry] = {}
        self.tz = tz

    def date_str_to_datetime(self, date_str: str) -> datetime:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).astimezone(UTC)

    def SMHI_timeSeries_object_to_WeatherDataEntry(
        self,
        obj: dict,
    ) -> tuple[datetime, WeatherDataEntry]:
        """Convert a SNOW1g time-series entry to the values used by the display."""
        valid_time = self.date_str_to_datetime(obj["time"])
        data = obj["data"]
        return valid_time, WeatherDataEntry(
            t=WeatherValueFloat(
                value=data["air_temperature"],
                unit="Cel",
            ),
            wd=WeatherValueFloat(
                value=data["wind_from_direction"],
                unit="degree",
            ),
            ws=WeatherValueFloat(
                value=data["wind_speed"],
                unit="m/s",
            ),
            gust=WeatherValueFloat(
                value=data["wind_speed_of_gust"],
                unit="m/s",
            ),
            pmean=WeatherValueFloat(
                # One kg/m² of water corresponds to one mm of precipitation.
                value=data["precipitation_amount_mean"],
                unit="mm",
            ),
            wsymb2=WeatherSymbol.from_code(data["symbol_code"]),
        )

    def get_url(self) -> str:
        return (
            "https://opendata-download-metfcst.smhi.se/api/category/snow1g/version/1/"
            f"geotype/point/lon/{self.lon}/lat/{self.lat}/data.json"
        )

    async def fetch(self):
        async with (
            aiohttp.ClientSession() as session,
            session.get(self.get_url()) as response,
        ):
            response.raise_for_status()
            weather = await response.json()
        for time_series in weather["timeSeries"]:
            date_time, forecast = self.SMHI_timeSeries_object_to_WeatherDataEntry(
                time_series
            )
            self.hourly_forecasts[date_time] = forecast

    def get_timestamps(self):
        return sorted(self.hourly_forecasts.keys())

    def get_dates(self):
        return {
            key: list(group)
            for key, group in itertools.groupby(
                self.get_timestamps(), key=lambda x: x.date()
            )
        }

    def get_current_weather(self):
        date_time = min(self.get_timestamps())
        return date_time, self.hourly_forecasts[date_time]

    def get_hourly_forecasts_for_date(self, date: date):
        return {
            date_time: self.hourly_forecasts[date_time]
            for date_time in self.get_dates()[date]
        }

    def get_forecast_data_entry_for_date(self, date: date):
        forecast_data = self.get_hourly_forecasts_for_date(date=date)
        datetime_series = list(forecast_data)
        symbol = next(
            (
                value.wsymb2
                for key, value in forecast_data.items()
                if key.hour in (13, 14)
            ),
            forecast_data[datetime_series[0]].wsymb2,
        )
        ws = next(
            (value.ws for key, value in forecast_data.items() if key.hour in (13, 14)),
            forecast_data[datetime_series[0]].ws,
        )
        wd = next(
            (value.wd for key, value in forecast_data.items() if key.hour in (13, 14)),
            forecast_data[datetime_series[0]].wd,
        )
        gust = next(
            (
                value.gust
                for key, value in forecast_data.items()
                if key.hour in (13, 14)
            ),
            forecast_data[datetime_series[0]].gust,
        )

        return ForecastDataEntry(
            date=date,
            symbol=symbol,
            t=ForecastData(
                values=[forecast_data[key].t.value for key in forecast_data],
                unit=forecast_data[next(iter(forecast_data))].t.unit,
            ),
            pmean=ForecastData(
                values=[forecast_data[key].pmean.value for key in forecast_data],
                unit=forecast_data[next(iter(forecast_data))].pmean.unit,
            ),
            ws=ws,
            wd=wd,
            gust=gust,
        )
