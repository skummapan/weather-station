import locale
from datetime import date, timedelta, timezone

import pytz
from image import ForecastCard
from lib import epd5in65f
from PIL import Image
from weather import SMHIHelper


class WeatherDisplay:
    def __init__(
        self,
        lon: float,
        lat: float,
        width: int,
        height: int,
        number_of_days: int,
        tz: timezone,
    ):
        self.weather = SMHIHelper(lon, lat, tz)
        self.width = width
        self.height = height
        self.number_of_days = number_of_days
        self.bg_color = (255, 255, 255)
        self.epd = epd5in65f.EPD()

    def serve(self) -> None:
        self.epd.init()

    def fetch_data(self) -> None:
        self.weather.fetch()

    def update_display(self) -> None:
        self.epd.Clear()
        self.fetch_data()

        image = self.card = Image.new("RGB", (self.width, self.height), self.bg_color)
        today = date.today()
        card_width = int(self.width / self.number_of_days)
        for i in range(self.number_of_days):
            forecast = self.weather.get_forecast_data_entry_for_date(
                today + timedelta(days=i)
            )
            card = ForecastCard(forecast, card_width, self.height, 10, 5).create_card()
            image.paste(card, (int((card_width * i)), 0))
        self.epd.display(self.epd.getbuffer(image=image))
        image.save("generated/image.png")


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "sv_SE")
    display = WeatherDisplay(
        lon=15.580572,
        lat=58.381857,
        width=600,
        height=448,
        number_of_days=3,
        tz=pytz.timezone("Europe/Berlin"),
    )
    display.serve()
    display.update_display()
