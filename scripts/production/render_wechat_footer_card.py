#!/usr/bin/env python3
"""Render a two-column WeChat account footer card for paper-notes."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ASSET_ROOT = Path("/Users/shenfei/Downloads/公众号资产")
AI_QR = ASSET_ROOT / "AI 系统笔记.jpg"
DARE_QR = ASSET_ROOT / "daretob2b.jpg"


def font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        ASSET_ROOT / "HYQiHei-60S.otf",
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(str(path), size=size, index=0)
        except Exception:
            continue
    return ImageFont.load_default()


def paste_qr(base: Image.Image, path: Path, xy: tuple[int, int], size: int) -> None:
    qr = Image.open(path).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    pad = 18
    box = Image.new("RGBA", (size + pad * 2, size + pad * 2), (255, 255, 255, 255))
    box.alpha_composite(qr, (pad, pad))
    base.alpha_composite(box, xy)


def draw_account(
    img: Image.Image,
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    *,
    name: str,
    desc_lines: list[str],
    qr_path: Path,
) -> None:
    slate = (15, 23, 42, 255)
    muted = (71, 85, 105, 255)

    draw.text((x, y), name, fill=slate, font=font(38))
    text_y = y + 64
    for line in desc_lines:
        draw.text((x, text_y), line, fill=muted, font=font(22))
        text_y += 36

    qr_size = 238
    qr_x = x + (width - qr_size - 36) // 2
    qr_y = y + 180
    paste_qr(img, qr_path, (qr_x, qr_y), qr_size)


def draw_card(out_path: Path) -> None:
    w, h = 1280, 760
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    navy = (11, 76, 129, 255)
    blue = (47, 107, 255, 255)
    line = (219, 231, 245, 255)
    pale = (248, 251, 255, 255)
    green_pale = (246, 255, 251, 255)

    draw.rectangle((0, 0, w, 8), fill=navy)
    draw.rounded_rectangle((26, 30, w - 26, h - 30), radius=24, fill=pale, outline=line, width=1)
    draw.rectangle((26, 30, 34, h - 30), fill=blue)

    draw.rounded_rectangle((64, 42, 192, 66), radius=12, fill=green_pale, outline=(187, 247, 208, 255), width=1)
    draw.text((82, 43), "Paper / AI / ToB", fill=(4, 120, 87, 255), font=font(15))
    draw.text((64, 82), "更多 AI 论文与 ToB 落地笔记", fill=navy, font=font(42))

    card_y = 185
    draw.rounded_rectangle((64, card_y, w - 64, h - 62), radius=22, fill=(255, 255, 255, 255), outline=line, width=1)
    draw.line((w // 2, card_y + 42, w // 2, h - 104), fill=line, width=2)

    draw_account(
        img,
        draw,
        104,
        card_y + 56,
        500,
        name="AI 系统笔记",
        desc_lines=["全球 AI 进展与关键论文", "模型、Agent、基础设施的结构化笔记"],
        qr_path=AI_QR,
    )
    draw_account(
        img,
        draw,
        700,
        card_y + 56,
        500,
        name="Dare to B2B",
        desc_lines=["ToB · AI · Cloud 一线实战", "追踪产品、技术与商业化落地"],
        qr_path=DARE_QR,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, quality=96)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    draw_card(Path(args.out))
    print(args.out)


if __name__ == "__main__":
    main()
