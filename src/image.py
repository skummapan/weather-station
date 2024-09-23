from typing import Tuple

import numpy as np
from common import ForecastData
from PIL import Image, ImageDraw, ImageFont

PALLET = np.array(
    [
        #  R     G     B
        [0x00, 0x00, 0x00],  # BLACK
        [0xFF, 0xFF, 0xFF],  # WHITE
        [0x00, 0xFF, 0x00],  # GREEN
        [0x00, 0x00, 0xFF],  # BLUE
        [0xFF, 0x00, 0x00],  # RED
        [0xFF, 0xFF, 0x00],  # YELLOW
        [0xFF, 0x80, 0x00],  # ORANGE
    ]
).astype(np.uint8)


def pixel_to_hex(pixel):
    tmp = pixel.astype(np.uint32)
    return (tmp[0] << 16) + (tmp[1] << 8) + tmp[2]


PALLET_TO_CODE_MAP = {
    pixel_to_hex(PALLET[0]): 0x0,  # Black
    pixel_to_hex(PALLET[1]): 0x1,  # White
    pixel_to_hex(PALLET[2]): 0x2,  # Green
    pixel_to_hex(PALLET[3]): 0x3,  # Blue
    pixel_to_hex(PALLET[4]): 0x4,  # Red
    pixel_to_hex(PALLET[5]): 0x5,  # Yellow
    pixel_to_hex(PALLET[6]): 0x6,  # Orange
}


def pixel_to_code(pixel):
    return PALLET_TO_CODE_MAP[pixel_to_hex(find_closest_palette_color(pixel, PALLET))]


def image_to_byte_array(image: Image) -> bytearray:
    tmp = b""
    for pixel in np.asanyarray(image):
        tmp += bytes(pixel_to_code(pixel))
    return tmp


def find_closest_palette_color(pixel: np.ndarray, pallet):
    idx = np.argmin([np.linalg.norm(pixel - color) for color in pallet])
    return pallet[idx]


def floyd_steinberg_dithering(img: np.ndarray, pallet=PALLET):
    """
    Does a Floyd-Steinberg dithering on an RGB image that is in an numpy array.
    Uses the defined PALLET in the file as default, can be overwritten.
    """
    tmp_img = img.copy()
    tmp_img.setflags(write=1)
    tmp_img = tmp_img.astype(float)

    height, width, _ = tmp_img.shape

    for y in range(height):
        for x in range(width):
            old_pixel = tmp_img[
                y, x
            ].copy()  # Ensure we are copying the current pixel value
            new_pixel = find_closest_palette_color(old_pixel, pallet)
            tmp_img[y, x] = new_pixel
            quant_error = old_pixel - new_pixel

            if x < width - 1:
                tmp_img[y, x + 1] += quant_error * 7 / 16
            if x > 0 and y < height - 1:
                tmp_img[y + 1, x - 1] += quant_error * 3 / 16
            if y < height - 1:
                tmp_img[y + 1, x] += quant_error * 5 / 16
            if x < width - 1 and y < height - 1:
                tmp_img[y + 1, x + 1] += quant_error * 1 / 16

    return np.clip(tmp_img, 0, 255).astype(
        np.uint8
    )  # Ensure pixel values are in the valid range and type


def center_text(
    draw: ImageDraw,
    height_position: int,
    message: str,
    font: ImageFont,
    text_color: Tuple[int, int, int] = (0, 0, 0),
):
    _, _, w, h = draw.textbbox((0, 0), message, font=font)

    draw.text(
        ((draw.im.size[0] - w) / 2, height_position),
        message,
        fill=text_color,
        font=font,
    )
    return h


def rotate_and_center_text(
    draw: ImageDraw,
    image: Image,
    height_position: int,
    message: str,
    font: ImageFont,
    rotate: int,
    text_color: Tuple[int, int, int] = (0, 0, 0),
):
    _, _, w, h = draw.textbbox((0, 0), message, font=font)
    new = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(new)
    d.text((0, 0), message, fill=text_color, font=font)
    w = new.rotate(rotate, expand=1, fillcolor=(255, 255, 255))

    image.paste(w, (int((draw.im.size[0] - w.size[0]) / 2), height_position))

    return w.size[1]


class ForecastCard:
    def __init__(
        self,
        forecast_entry: ForecastData,
        width: int,
        height: int,
        outer_margin: int,
        outer_radius: int,
        bg_color: Tuple[int, int, int] = (255, 255, 255),
    ):
        self.forecast_entry = forecast_entry
        self.width = width
        self.height = height
        self.outer_margin = outer_margin
        self.outer_radius = outer_radius
        self.bg_color = bg_color
        self.font_path = "font/"
        self.font = ImageFont.truetype(
            self.font_path + "FiraCodeNerdFontPropo-Regular.ttf", 25
        )
        self.light_font = ImageFont.truetype(
            self.font_path + "FiraCodeNerdFontPropo-Regular.ttf", 23
        )
        self.title_font = ImageFont.truetype(
            self.font_path + "FiraCodeNerdFontPropo-Regular.ttf", 30
        )
        self.emoji_font = ImageFont.truetype(
            self.font_path + "FiraCodeNerdFontPropo-Regular.ttf",
            30,
            layout_engine=ImageFont.Layout.RAQM,
        )
        self.card = Image.new("RGB", (self.width, self.height), self.bg_color)
        self.draw = ImageDraw.Draw(self.card)

    def add_border(self) -> None:
        self.draw.line(
            (
                self.outer_margin,
                self.outer_margin + self.outer_radius,
                self.outer_margin,
                self.height - self.outer_margin - self.outer_radius,
            ),
            width=3,
            fill=(0, 0, 0),
        )
        self.draw.line(
            (
                self.outer_margin + self.outer_radius,
                self.height - self.outer_margin,
                self.width - self.outer_margin - self.outer_radius,
                self.height - self.outer_margin,
            ),
            width=3,
            fill=(0, 0, 0),
        )
        self.draw.line(
            (
                self.width - self.outer_margin,
                self.outer_margin + self.outer_radius,
                self.width - self.outer_margin,
                self.height - self.outer_margin - self.outer_radius,
            ),
            width=3,
            fill=(0, 0, 0),
        )
        self.draw.line(
            (
                self.outer_margin + self.outer_radius,
                self.outer_margin,
                self.width - self.outer_margin - self.outer_radius,
                self.outer_margin,
            ),
            width=3,
            fill=(0, 0, 0),
        )
        self.draw.arc(
            (
                self.outer_margin,
                self.outer_margin,
                self.outer_margin * 2,
                self.outer_margin * 2,
            ),
            start=180,
            end=270,
            fill=(0, 0, 0),
            width=3,
        )
        self.draw.arc(
            (
                self.width - self.outer_margin * 2,
                self.outer_margin,
                self.width - self.outer_margin,
                self.outer_margin * 2,
            ),
            start=270,
            end=0,
            fill=(0, 0, 0),
            width=3,
        )
        self.draw.arc(
            (
                self.outer_margin,
                self.height - self.outer_margin * 2,
                self.outer_margin * 2,
                self.height - self.outer_margin,
            ),
            start=90,
            end=180,
            fill=(0, 0, 0),
            width=3,
        )
        self.draw.arc(
            (
                self.width - self.outer_margin * 2,
                self.height - self.outer_margin * 2,
                self.width - self.outer_margin,
                self.height - self.outer_margin,
            ),
            start=0,
            end=90,
            fill=(0, 0, 0),
            width=3,
        )

    def create_card(self) -> Image:
        # Create a blank image with white background
        self.add_border()
        margin = 20

        height_position = margin

        message = self.forecast_entry.date.strftime("%A").title()
        h = center_text(self.draw, height_position, message, self.emoji_font)
        height_position = height_position + h + margin

        message = self.forecast_entry.date.strftime("%d %b").title()
        h = center_text(self.draw, height_position, message, self.emoji_font)
        height_position = height_position + h + margin

        icon = Image.open(f"img/{self.forecast_entry.symbol.code}.png").convert("RGBA")

        new_icon = Image.new("RGBA", icon.size, "WHITE")
        new_icon.paste(icon, (0, 0), icon)

        dithered_icon = Image.fromarray(
            floyd_steinberg_dithering(np.asanyarray(new_icon.convert("RGB")))
        )
        icon_size = dithered_icon.size
        icon_position = (
            int((self.width - icon_size[0]) / 2),
            height_position,
        )
        self.card.paste(dithered_icon, icon_position, icon)
        height_position = height_position + icon_size[1] + margin

        h = center_text(
            self.draw, height_position, f"{max(self.forecast_entry.t):.0f}°", self.font
        )
        height_position = height_position + h + int(margin / 5)
        h = center_text(
            self.draw,
            height_position,
            f"{min(self.forecast_entry.t):.0f}°",
            self.light_font,
        )
        height_position = height_position + h + margin

        h = center_text(
            self.draw,
            height_position,
            f"{self.forecast_entry.ws.value:.1f} {self.forecast_entry.ws.unit}",
            self.font,
        )
        height_position = height_position + h + int(margin / 5)

        h = center_text(
            self.draw,
            height_position,
            f"{self.forecast_entry.gust.value:.1f} {self.forecast_entry.gust.unit}",
            self.light_font,
        )
        height_position = height_position + h + margin

        h = rotate_and_center_text(
            self.draw,
            self.card,
            height_position,
            "->",
            self.emoji_font,
            -self.forecast_entry.wd.value,
        )

        return self.card
