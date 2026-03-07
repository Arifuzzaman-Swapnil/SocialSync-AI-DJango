"""
Copy Overlay Service
Renders marketing copy text onto images using Pillow with professional typography.
Supports multiple layout modes, font styles, text shadows, and semi-transparent backgrounds.
"""

import logging
import os
import textwrap
from io import BytesIO
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter, ImageFont

logger = logging.getLogger(__name__)

# Font directory relative to this file
FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts')

# Font mapping
FONT_MAP = {
    'montserrat_bold': 'Montserrat-Bold.ttf',
    'montserrat_regular': 'Montserrat-Regular.ttf',
    'playfair_bold': 'PlayfairDisplay-Bold.ttf',
    'roboto_bold': 'Roboto-Bold.ttf',
    'bebas_neue': 'BebasNeue-Regular.ttf',
}

# Position layout configurations
POSITION_CONFIG = {
    'center': {'y_ratio': 0.5, 'anchor': 'mm'},
    'bottom_banner': {'y_ratio': 0.85, 'anchor': 'mm'},
    'top_banner': {'y_ratio': 0.15, 'anchor': 'mm'},
    'top_bottom_split': None,  # Special handling
}


def _get_font(font_style: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a font from the fonts directory."""
    filename = FONT_MAP.get(font_style, 'Montserrat-Bold.ttf')
    font_path = os.path.join(FONTS_DIR, filename)
    if not os.path.exists(font_path):
        logger.warning(f"Font {font_path} not found, using default")
        return ImageFont.load_default()
    return ImageFont.truetype(font_path, size)


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> Tuple[int, int, int, int]:
    """Convert hex color string to RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (r, g, b, alpha)


def _calculate_font_size(image_width: int, text: str, font_style: str) -> int:
    """Auto-calculate optimal font size based on image width and text length."""
    base_size = image_width // 15
    min_size = image_width // 30
    max_size = image_width // 8

    # Adjust based on text length
    if len(text) > 40:
        base_size = int(base_size * 0.7)
    elif len(text) > 25:
        base_size = int(base_size * 0.85)
    elif len(text) < 10:
        base_size = int(base_size * 1.2)

    return max(min_size, min(base_size, max_size))


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = font.getbbox(test_line)
        text_width = bbox[2] - bbox[0]
        if text_width <= max_width and current_line:
            current_line.append(word)
        elif not current_line:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def _draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    position: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    text_color: Tuple[int, int, int, int],
    alignment: str,
    add_shadow: bool,
):
    """Draw text with optional shadow for depth."""
    x, y = position

    if add_shadow:
        shadow_color = (0, 0, 0, 128)
        shadow_offset = 2
        draw.text(
            (x + shadow_offset, y + shadow_offset),
            text, font=font, fill=shadow_color, anchor=f"{alignment[0]}a"
        )

    draw.text(
        (x, y), text, font=font, fill=text_color, anchor=f"{alignment[0]}a"
    )


def render_copy_overlay(
    image_data: bytes,
    copy_text: str,
    position: str = 'bottom_banner',
    font_style: str = 'montserrat_bold',
    text_color: str = '#FFFFFF',
    overlay_opacity: int = 60,
    font_size_override: int = 0,
    text_alignment: str = 'center',
    add_text_shadow: bool = True,
) -> Optional[bytes]:
    """
    Render copy text onto an image with professional typography.

    Args:
        image_data: Source image as bytes
        copy_text: Text to overlay
        position: Layout mode (center, bottom_banner, top_banner, top_bottom_split)
        font_style: Font to use (montserrat_bold, playfair_bold, etc.)
        text_color: Hex color for text
        overlay_opacity: 0-100, opacity of background strip
        font_size_override: 0 = auto, otherwise specific pixel size
        text_alignment: left, center, right
        add_text_shadow: Whether to add drop shadow

    Returns:
        PNG image bytes with text overlay, or None on failure
    """
    try:
        # Open source image
        source = Image.open(BytesIO(image_data)).convert('RGBA')
        img_w, img_h = source.size

        # Work at 2x for smoother text, then downscale
        scale = 2
        canvas = source.resize((img_w * scale, img_h * scale), Image.LANCZOS)
        cw, ch = canvas.size

        # Calculate font size
        if font_size_override > 0:
            font_size = font_size_override * scale
        else:
            font_size = _calculate_font_size(cw, copy_text, font_style)

        font = _get_font(font_style, font_size)
        text_rgba = _hex_to_rgba(text_color)

        # Word wrap text
        max_text_width = int(cw * 0.85)
        lines = _wrap_text(copy_text, font, max_text_width)

        # Calculate line height and total text block height
        sample_bbox = font.getbbox('Ay')
        line_height = int((sample_bbox[3] - sample_bbox[1]) * 1.3)
        total_text_height = line_height * len(lines)

        # Padding for background strip
        pad_x = int(font_size * 0.8)
        pad_y = int(font_size * 0.6)

        # Create overlay layer for semi-transparent background
        overlay = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # Calculate positions based on layout mode
        if position == 'top_bottom_split':
            # Split text: first line at top, rest at bottom
            _render_split_layout(
                overlay_draw, canvas, overlay, lines, font, text_rgba,
                line_height, pad_x, pad_y, overlay_opacity, text_alignment,
                add_text_shadow, cw, ch
            )
        else:
            # Standard single-block layout
            config = POSITION_CONFIG.get(position, POSITION_CONFIG['bottom_banner'])
            center_y = int(ch * config['y_ratio'])

            # Background strip
            strip_top = center_y - total_text_height // 2 - pad_y
            strip_bottom = center_y + total_text_height // 2 + pad_y
            bg_alpha = int(255 * overlay_opacity / 100)
            overlay_draw.rectangle(
                [(0, strip_top), (cw, strip_bottom)],
                fill=(0, 0, 0, bg_alpha)
            )

            # Draw each line
            y = center_y - total_text_height // 2 + line_height // 2
            for line in lines:
                if text_alignment == 'left':
                    x = pad_x
                elif text_alignment == 'right':
                    x = cw - pad_x
                else:  # center
                    x = cw // 2

                _draw_text_with_shadow(
                    overlay_draw, (x, y), line, font, text_rgba,
                    text_alignment, add_text_shadow
                )
                y += line_height

        # Composite overlay onto canvas
        canvas = Image.alpha_composite(canvas, overlay)

        # Downscale back to original resolution
        canvas = canvas.resize((img_w, img_h), Image.LANCZOS)

        # Convert to RGB for PNG/JPEG output
        final = canvas.convert('RGB')

        buffer = BytesIO()
        final.save(buffer, format='PNG', quality=95)
        buffer.seek(0)
        return buffer.read()

    except Exception as e:
        logger.error(f"Copy overlay rendering failed: {e}")
        return None


def _render_split_layout(
    overlay_draw, canvas, overlay, lines, font, text_rgba,
    line_height, pad_x, pad_y, overlay_opacity, text_alignment,
    add_text_shadow, cw, ch
):
    """Render top/bottom split layout — first line at top, rest at bottom."""
    bg_alpha = int(255 * overlay_opacity / 100)

    if len(lines) <= 1:
        # Only one line — put it at top
        top_lines = lines
        bottom_lines = []
    else:
        # Split: first line top, rest bottom
        top_lines = [lines[0]]
        bottom_lines = lines[1:]

    # Top section
    top_y = int(ch * 0.12)
    top_height = line_height * len(top_lines)
    overlay_draw.rectangle(
        [(0, top_y - pad_y), (cw, top_y + top_height + pad_y)],
        fill=(0, 0, 0, bg_alpha)
    )
    y = top_y + line_height // 2
    for line in top_lines:
        x = cw // 2 if text_alignment == 'center' else (pad_x if text_alignment == 'left' else cw - pad_x)
        _draw_text_with_shadow(overlay_draw, (x, y), line, font, text_rgba, text_alignment, add_text_shadow)
        y += line_height

    # Bottom section
    if bottom_lines:
        bottom_y = int(ch * 0.82)
        bottom_height = line_height * len(bottom_lines)
        overlay_draw.rectangle(
            [(0, bottom_y - pad_y), (cw, bottom_y + bottom_height + pad_y)],
            fill=(0, 0, 0, bg_alpha)
        )
        y = bottom_y + line_height // 2
        for line in bottom_lines:
            x = cw // 2 if text_alignment == 'center' else (pad_x if text_alignment == 'left' else cw - pad_x)
            _draw_text_with_shadow(overlay_draw, (x, y), line, font, text_rgba, text_alignment, add_text_shadow)
            y += line_height
