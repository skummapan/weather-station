import unittest
from datetime import UTC, datetime

from src.common import WeatherSymbol
from src.weather import SMHIHelper


class SnowForecastParsingTests(unittest.TestCase):
    def test_parses_snow1g_time_series_entry(self) -> None:
        entry = {
            "time": "2026-07-20T13:00:00Z",
            "intervalParametersStartTime": "2026-07-20T12:00:00Z",
            "data": {
                "air_temperature": 18.4,
                "wind_from_direction": 204,
                "wind_speed": 2.8,
                "wind_speed_of_gust": 8.4,
                "precipitation_amount_mean": 1.2,
                "symbol_code": 3,
            },
        }

        valid_time, forecast = SMHIHelper(
            15.6, 58.4
        ).SMHI_timeSeries_object_to_WeatherDataEntry(entry)

        self.assertEqual(valid_time, datetime(2026, 7, 20, 13, tzinfo=UTC))
        self.assertEqual(forecast.t.value, 18.4)
        self.assertEqual(forecast.t.unit, "Cel")
        self.assertEqual(forecast.ws.value, 2.8)
        self.assertEqual(forecast.ws.unit, "m/s")
        self.assertEqual(forecast.gust.value, 8.4)
        self.assertEqual(forecast.pmean.value, 1.2)
        self.assertEqual(forecast.pmean.unit, "mm")
        self.assertEqual(forecast.wsymb2, WeatherSymbol.VARIABLE_CLOUDINESS)
