import logging
import sys
from datetime import date, datetime, timedelta, timezone
from io import BytesIO
from urllib.parse import urlencode

from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image
from playwright.async_api import async_playwright

from .image import ForecastCard, image_to_byte_array
from .weather import SMHIHelper

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


app = FastAPI()


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
        logger.info("Fetching data and generating image")
        self.fetch_data()

        image = self.card = Image.new("RGB", (self.width, self.height), self.bg_color)
        today = date.today()
        card_width = int(self.width / self.number_of_days)
        for i in range(self.number_of_days):
            forecast = self.weather.get_forecast_data_entry_for_date(
                today + timedelta(days=i)
            )
            card = ForecastCard(forecast, card_width, self.height, 10, 5).create_card()
            image.paste(card, (int(card_width * i), 0))
        return image


app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")


@app.get("/")
async def read_item(
    request: Request,
    lon: float = 16,
    lat: float = 58,
    dither: bool = False,
    days: int = 3,
    tz: str = Query(
        description="Timezone, e.g., 'Europe/Berlin'",
        default="Europe/Berlin",
    ),
) -> HTMLResponse:
    smhi = SMHIHelper(lon, lat)
    await smhi.fetch()

    now = datetime.now()

    forecasts = [
        smhi.get_forecast_data_entry_for_date((now + timedelta(days=i)).date())
        for i in range(days)
    ]

    return templates.TemplateResponse(
        "forecast_cards.html",
        {"request": request, "forecasts": forecasts, "dither": dither},
    )


@app.get("/export")
async def export_forecast_image(
    lon: float = 16,
    lat: float = 58,
    width: int = 600,
    height: int = 448,
    days: int = 3,
    dither: bool = True,
):
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
        )
        params = {
            "lon": lon,
            "lat": lat,
            "days": days,
            "dither": dither,
        }
        query_string = urlencode(params)
        await page.goto(
            f"http://localhost:8000/?{query_string}", wait_until="domcontentloaded"
        )
        await page.evaluate("document.body.style.zoom = '0.65'")
        screenshot = await page.screenshot()
        await browser.close()

        bytes_array = image_to_byte_array(Image.open(BytesIO(screenshot)))
    return Response(content=bytes(bytes_array), media_type="application/octet-stream")
