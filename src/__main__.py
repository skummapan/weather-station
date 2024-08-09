import locale
import pytz
import os
import logging
from http.server import HTTPServer as BaseHTTPServer
from http.server import SimpleHTTPRequestHandler
from socket import socket
from datetime import date, timedelta, timezone

from image import ForecastCard

from PIL import Image
from weather import SMHIHelper

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, "sv_SE.utf8")

DUMMY_RESPONSE = b"""
<html>
<head>
<title>Python Test</title>
</head>

<body>
Test page...success.
</body>
</html>
"""


class HTTPHandler(SimpleHTTPRequestHandler):
    """This handler uses server.base_path instead of always using os.getcwd()"""

    def translate_path(self, path):
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        relpath = os.path.relpath(path, os.getcwd())
        fullpath = os.path.join(self.server.base_path, relpath)
        return fullpath

    def do_GET(self):
        if self.path == "/image":
            with open(self.directory + "/generated/image.png", "rb") as f:
                image = f.read()
                self.send_response(200)
                self.send_header("Content-type", "image/png")
                self.send_header("Content-length", len(image))
                self.end_headers()
                self.wfile.write(image)
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(DUMMY_RESPONSE))
            self.end_headers()
            self.wfile.write(DUMMY_RESPONSE)


class HTTPServer(BaseHTTPServer):
    """The main server, you pass in base_path which is the path you want to serve requests from"""

    def __init__(self, base_path, server_address, RequestHandlerClass=HTTPHandler):
        super().__init__(server_address, RequestHandlerClass)
        self.base_path = base_path


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

    def fetch_data(self) -> None:
        self.weather.fetch()

    def update_display(self) -> Image:
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
        return image


if __name__ == "__main__":
    display = WeatherDisplay(
        lon=15.580572,
        lat=58.381857,
        width=600,
        height=448,
        number_of_days=3,
        tz=pytz.timezone("Europe/Stockholm"),
    )
    display.update_display()
    web_dir = os.path.join(os.path.dirname(__file__), "my_dir")
    httpd = HTTPServer(web_dir, ("", 8000))
    httpd.serve_forever()
