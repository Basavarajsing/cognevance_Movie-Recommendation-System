"""
CineMatch AI - Realistic Movie Poster Generator Module
Generates high-resolution, cinematic movie poster images using PIL (Pillow).
Features genre-tailored artistic motifs, cinematic lighting vignettes,
laurel festival wreaths, billing block credits, and bold typography.
"""

import io
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

# High-contrast color themes for genres (top, bottom, accent)
POSTER_THEMES = {
    "Action": {"bg": ((180, 20, 20), (20, 10, 15)), "accent": (249, 115, 22), "motif": "swords"},
    "Adventure": {"bg": ((2, 132, 199), (10, 25, 45)), "accent": (56, 189, 248), "motif": "compass"},
    "Animation": {"bg": ((217, 119, 6), (45, 10, 35)), "accent": (244, 114, 182), "motif": "star"},
    "Children's": {"bg": ((16, 185, 129), (15, 30, 45)), "accent": (52, 211, 153), "motif": "wand"},
    "Comedy": {"bg": ((124, 58, 237), (35, 15, 40)), "accent": (236, 72, 153), "motif": "masks"},
    "Crime": {"bg": ((71, 85, 105), (10, 15, 25)), "accent": (203, 213, 225), "motif": "spotlight"},
    "Documentary": {"bg": ((13, 148, 136), (10, 25, 30)), "accent": (45, 212, 191), "motif": "lens"},
    "Drama": {"bg": ((79, 70, 229), (15, 15, 35)), "accent": (167, 139, 250), "motif": "curtains"},
    "Fantasy": {"bg": ((147, 51, 234), (20, 10, 40)), "accent": (192, 132, 252), "motif": "crown"},
    "Film-Noir": {"bg": ((39, 39, 42), (5, 5, 10)), "accent": (244, 244, 245), "motif": "venetian"},
    "Horror": {"bg": ((136, 19, 55), (15, 5, 10)), "accent": (244, 63, 94), "motif": "moon"},
    "Musical": {"bg": ((190, 24, 93), (35, 10, 25)), "accent": (251, 113, 133), "motif": "notes"},
    "Mystery": {"bg": ((55, 48, 163), (12, 12, 30)), "accent": (129, 140, 248), "motif": "key"},
    "Romance": {"bg": ((225, 29, 72), (35, 10, 20)), "accent": (251, 113, 133), "motif": "heart"},
    "Sci-Fi": {"bg": ((29, 78, 216), (5, 15, 40)), "accent": (34, 211, 238), "motif": "saturn"},
    "Thriller": {"bg": ((127, 29, 29), (25, 8, 10)), "accent": (239, 68, 68), "motif": "target"},
    "War": {"bg": ((68, 64, 60), (20, 18, 15)), "accent": (214, 211, 209), "motif": "shield"},
    "Western": {"bg": ((180, 83, 9), (35, 18, 10)), "accent": (245, 158, 11), "motif": "star"},
    "default": {"bg": ((79, 70, 229), (15, 23, 42)), "accent": (167, 139, 250), "motif": "reel"},
}


def draw_vertical_gradient(draw: ImageDraw.ImageDraw, width: int, height: int, c1: Tuple[int, int, int], c2: Tuple[int, int, int]):
    """Fills the image with a smooth vertical linear color gradient."""
    for y in range(height):
        factor = y / height
        r = int(c1[0] + (c2[0] - c1[0]) * factor)
        g = int(c1[1] + (c2[1] - c1[1]) * factor)
        b = int(c1[2] + (c2[2] - c1[2]) * factor)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def generate_movie_poster(
    title: str,
    genres: str,
    year: int,
    rating: Optional[float] = None,
    width: int = 320,
    height: int = 460
) -> bytes:
    """
    Generates a realistic, high-resolution portrait movie poster in PNG bytes format.
    Styled with authentic cinematic billing blocks, genre motifs, and title typography.
    """
    primary_genre = genres.split("|")[0].strip() if genres else "Drama"
    theme = POSTER_THEMES.get(primary_genre, POSTER_THEMES["default"])
    c1, c2 = theme["bg"]
    accent = theme["accent"]

    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # 1. Base Gradient
    draw_vertical_gradient(draw, width, height, c1, c2)

    # 2. Cinematic Vignette (Dark shadows at top, bottom, and borders)
    draw.rectangle([0, 0, width, 40], fill=(0, 0, 0, 120))
    for y in range(height - 130, height):
        alpha = int(((y - (height - 130)) / 130) * 220)
        draw.line([(0, y), (width, y)], fill=(8, 12, 22))

    # Inner Border Frame (Classic Film Poster Border)
    draw.rectangle([10, 10, width - 10, height - 10], outline=(255, 255, 255), width=1)
    draw.rectangle([14, 14, width - 14, height - 14], outline=accent, width=1)

    # 3. Top Banner: CINEMATCH ARCHIVE & Year
    draw.text((width // 2, 24), "★  C I N E M A T C H   C I N E M A  ★", fill=(226, 232, 240), anchor="mm")
    
    # Year & Genre Pill Badge
    genre_badge_text = f" {year}  •  {primary_genre.upper()} "
    draw.rectangle([width // 2 - 65, 36, width // 2 + 65, 52], fill=(0, 0, 0), outline=accent, width=1)
    draw.text((width // 2, 44), genre_badge_text, fill=(255, 255, 255), anchor="mm")

    # 4. Central Cinematic Motif Art (Genre specific geometric emblem)
    cx, cy = width // 2, 175
    # Ambient Glow circle
    for r in range(75, 45, -5):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=accent)

    motif = theme["motif"]
    if motif == "saturn":
        # Planet & Ring
        draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=accent, outline=(255, 255, 255), width=2)
        draw.ellipse([cx - 55, cy - 14, cx + 55, cy + 14], outline=(255, 255, 255), width=3)
    elif motif == "swords":
        # Crossed Swords / Blade
        draw.line([cx - 35, cy - 35, cx + 35, cy + 35], fill=(255, 255, 255), width=4)
        draw.line([cx + 35, cy - 35, cx - 35, cy + 35], fill=(255, 255, 255), width=4)
        draw.polygon([(cx, cy - 45), (cx + 12, cy), (cx, cy + 15), (cx - 12, cy)], fill=accent)
    elif motif == "heart":
        draw.ellipse([cx - 24, cy - 25, cx, cy], fill=accent)
        draw.ellipse([cx, cy - 25, cx + 24, cy], fill=accent)
        draw.polygon([(cx - 24, cy - 10), (cx + 24, cy - 10), (cx, cy + 28)], fill=accent)
    elif motif == "star":
        # Multi-pointed cinema star
        draw.polygon([(cx, cy - 40), (cx + 10, cy - 12), (cx + 40, cy), (cx + 10, cy + 12),
                      (cx, cy + 40), (cx - 10, cy + 12), (cx - 40, cy), (cx - 10, cy - 12)], fill=accent)
    elif motif == "masks":
        # Comedy / Drama masks
        draw.ellipse([cx - 35, cy - 25, cx - 5, cy + 15], outline=(255, 255, 255), width=2)
        draw.arc([cx - 28, cy - 10, cx - 12, cy + 5], start=0, end=180, fill=accent, width=2)
        draw.ellipse([cx + 5, cy - 15, cx + 35, cy + 25], outline=(255, 255, 255), width=2)
        draw.arc([cx + 12, cy + 5, cx + 28, cy + 18], start=180, end=360, fill=accent, width=2)
    elif motif == "moon":
        draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=(244, 63, 94))
        draw.ellipse([cx - 16, cy - 36, cx + 44, cy + 28], fill=(15, 5, 10))
    else:
        # Classic Film Reel
        draw.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], outline=(255, 255, 255), width=3)
        draw.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=accent)
        for angle_offset in [(-25, -25), (25, -25), (-25, 25), (25, 25)]:
            draw.ellipse([cx + angle_offset[0] - 6, cy + angle_offset[1] - 6,
                          cx + angle_offset[0] + 6, cy + angle_offset[1] + 6], fill=(255, 255, 255))

    # Festival Laurels Banner
    draw.text((width // 2, 258), "✦  CRITICS' CHOICE AWARD WINNER  ✦", fill=(251, 191, 36), anchor="mm")

    # 5. Movie Title (Auto-wrapped in Bold All-Caps with Drop Shadow)
    clean_title = title.upper()
    words = clean_title.split()
    lines = []
    curr_line = []
    for w in words:
        if len(" ".join(curr_line + [w])) <= 16:
            curr_line.append(w)
        else:
            if curr_line:
                lines.append(" ".join(curr_line))
            curr_line = [w]
    if curr_line:
        lines.append(" ".join(curr_line))
    lines = lines[:3]  # Max 3 lines

    title_y = 290
    line_spacing = 22
    for line in lines:
        # Drop shadow
        draw.text((width // 2 + 2, title_y + 2), line, fill=(0, 0, 0), anchor="mm")
        draw.text((width // 2 + 1, title_y + 1), line, fill=(0, 0, 0), anchor="mm")
        # Main text
        draw.text((width // 2, title_y), line, fill=(255, 255, 255), anchor="mm")
        title_y += line_spacing

    # 6. Star Rating Highlight
    if rating:
        stars_str = "★" * int(round(rating)) + "☆" * (5 - int(round(rating)))
        score_text = f"{stars_str}  {rating:.1f} / 5.0"
        draw.text((width // 2, title_y + 12), score_text, fill=(251, 191, 36), anchor="mm")

    # 7. Authentic Movie Billing Block (Credits Footer)
    billing_lines = [
        "GROUPLENS RESEARCH PRESENTS A CINEMATCH MASTERWORK PRODUCTION",
        "DIRECTED BY ACADEMIC AI • SCREENPLAY BY COLLABORATIVE FILTERING",
        f"STARRING {primary_genre.upper()} ENSEMBLE • ORIGINAL SCORE IN DOLBY ATMOS",
        "ALL RIGHTS RESERVED • MOVIELENS 100K BENCHMARK EDITION"
    ]
    b_y = height - 48
    for bl in billing_lines:
        draw.text((width // 2, b_y), bl, fill=(148, 163, 184), anchor="mm")
        b_y += 9

    buf = io.BytesIO()
    img.save(buf, format="PNG", quality=95)
    return buf.getvalue()
