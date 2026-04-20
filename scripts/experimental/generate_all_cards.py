#!/usr/bin/env python3
"""Generate all three cards for paper notes using Pillow.

Experimental script only.

This file is not the default production image pipeline.
For formal publishing, use:
  - generate_cards.py
  - generate_cover.py
or call the full orchestrator:
  - daily_runner.py
"""

from PIL import Image, ImageDraw, ImageFont
import json
import os
import sys

# Constants
SCORE_CARD_SIZE = (1200, 800)
INFO_CARD_SIZE = (800, 1000)
COVER_SIZE = (2350, 1000)

# Colors
PRIMARY = (11, 20, 48)
PRIMARY_LIGHT = (26, 42, 74)
ACCENT = (76, 195, 255)
WHITE = (255, 255, 255)
LIGHT_GRAY = (200, 200, 200)
MUTED = (150, 150, 150)

def get_fonts():
    """Load fonts"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    fonts = {}
    try:
        fonts['bold_large'] = ImageFont.truetype(os.path.join(base_path, "SourceHanSansCN-Bold.otf"), 72)
        fonts['bold_medium'] = ImageFont.truetype(os.path.join(base_path, "SourceHanSansCN-Bold.otf"), 48)
        fonts['bold_normal'] = ImageFont.truetype(os.path.join(base_path, "SourceHanSansCN-Bold.otf"), 32)
        fonts['bold_small'] = ImageFont.truetype(os.path.join(base_path, "SourceHanSansCN-Bold.otf"), 24)
        
        fonts['regular_large'] = ImageFont.truetype(os.path.join(base_path, "SourceHanSansCN-Regular.otf"), 48)
        fonts['regular_medium'] = ImageFont.truetype(os.path.join(base_path, "SourceHanSansCN-Regular.otf"), 32)
        fonts['regular_normal'] = ImageFont.truetype(os.path.join(base_path, "SourceHanSansCN-Regular.otf"), 24)
        fonts['regular_small'] = ImageFont.truetype(os.path.join(base_path, "SourceHanSansCN-Regular.otf"), 18)
    except Exception as e:
        print(f"Font loading error: {e}")
        # Fallback to default
        fonts['bold_large'] = ImageFont.load_default()
        fonts['regular_normal'] = ImageFont.load_default()
    
    return fonts

def create_gradient(width, height, color1, color2):
    """Create vertical gradient background"""
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        ratio = y / height
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    return img

def generate_score_card(data, output_path, fonts):
    """Generate score card (1200x800)"""
    img = create_gradient(SCORE_CARD_SIZE[0], SCORE_CARD_SIZE[1], PRIMARY, PRIMARY_LIGHT)
    draw = ImageDraw.Draw(img)
    
    scores = data.get('scores', {})
    dimensions = scores.get('dimensions', {})
    total = scores.get('total', 8.3)
    
    # Title
    draw.text((60, 50), "评分卡", font=fonts['bold_large'], fill=WHITE)
    draw.text((60, 140), "Experience Compression Spectrum", font=fonts['regular_normal'], fill=LIGHT_GRAY)
    
    # Total score
    draw.text((900, 80), f"{total:.1f}", font=fonts['bold_large'], fill=ACCENT)
    draw.text((1050, 120), "/ 10", font=fonts['regular_medium'], fill=MUTED)
    
    # Rank badge
    draw.rounded_rectangle((900, 200, 1100, 260), radius=30, fill=ACCENT)
    draw.text((960, 215), "TOP 1", font=fonts['bold_normal'], fill=PRIMARY)
    
    # Five dimensions
    dim_names = [
        ("重要性 Impact", dimensions.get('impact', 1.8)),
        ("创新性 Novelty", dimensions.get('novelty', 1.8)),
        ("可验证性 Evidence", dimensions.get('evidence', 1.4)),
        ("产业可用性 Applicability", dimensions.get('applicability', 1.7)),
        ("可复用性 Reusability", dimensions.get('reusability', 1.6)),
    ]
    
    y = 350
    for name, score in dim_names:
        # Name
        draw.text((60, y), name, font=fonts['regular_normal'], fill=LIGHT_GRAY)
        
        # Bar background
        draw.rounded_rectangle((350, y+5, 750, y+30), radius=12, fill=(50, 60, 80))
        
        # Progress bar
        width = int(400 * score / 2.0)
        draw.rounded_rectangle((350, y+5, 350+width, y+30), radius=12, fill=ACCENT)
        
        # Score
        draw.text((780, y), f"{score:.1f}/2", font=fonts['regular_normal'], fill=ACCENT)
        
        y += 70
    
    # Footer
    draw.text((60, 740), "AI 系统笔记 · 论文速记", font=fonts['regular_small'], fill=MUTED)
    draw.text((900, 740), "arXiv:2604.15877", font=fonts['regular_small'], fill=MUTED)
    
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Score card saved: {output_path}")

def generate_info_card(data, output_path, fonts):
    """Generate info card (800x1000)"""
    img = create_gradient(INFO_CARD_SIZE[0], INFO_CARD_SIZE[1], PRIMARY, PRIMARY_LIGHT)
    draw = ImageDraw.Draw(img)
    
    paper = data.get('paper', {})
    
    # Logo placeholder (top right)
    draw.rounded_rectangle((620, 40, 740, 120), radius=20, fill=WHITE)
    draw.text((635, 65), "AI\n系统\n笔记", font=fonts['regular_small'], fill=PRIMARY)
    
    # Title section
    draw.text((40, 180), "论文信息", font=fonts['bold_large'], fill=WHITE)
    
    # Chinese title
    title_cn = paper.get('title_cn', '')
    draw.text((40, 260), title_cn, font=fonts['bold_medium'], fill=ACCENT)
    
    # English title (wrapped)
    title_en = paper.get('title', '')
    y = 340
    for line in [title_en[:50], title_en[50:100]]:
        if line:
            draw.text((40, y), line, font=fonts['regular_normal'], fill=LIGHT_GRAY)
            y += 40
    
    # Meta information
    y = 450
    
    # Authors
    draw.text((40, y), "作者", font=fonts['regular_normal'], fill=MUTED)
    authors = paper.get('authors', '')[:50] + '...'
    draw.text((150, y), authors, font=fonts['regular_small'], fill=LIGHT_GRAY)
    y += 60
    
    # arXiv ID
    draw.text((40, y), "arXiv", font=fonts['regular_normal'], fill=MUTED)
    draw.text((150, y), paper.get('arxiv_id', ''), font=fonts['regular_small'], fill=LIGHT_GRAY)
    y += 60
    
    # Score
    scores = data.get('scores', {})
    draw.text((40, y), "评分", font=fonts['regular_normal'], fill=MUTED)
    draw.text((150, y), f"{scores.get('total', 8.3)}/10", font=fonts['bold_normal'], fill=ACCENT)
    y += 60
    
    # Keywords
    draw.text((40, y), "关键词", font=fonts['regular_normal'], fill=MUTED)
    keywords = ', '.join(paper.get('keywords', [])[:4])
    draw.text((150, y), keywords, font=fonts['regular_small'], fill=LIGHT_GRAY)
    
    # Footer
    draw.text((40, 940), "AI 系统笔记 · 论文速记", font=fonts['regular_small'], fill=MUTED)
    draw.text((550, 940), f"arXiv:{paper.get('arxiv_id', '')}", font=fonts['regular_small'], fill=MUTED)
    
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Info card saved: {output_path}")

def generate_cover_card(data, output_path, fonts):
    """Generate cover card 2.35:1 (2350x1000)"""
    img = create_gradient(COVER_SIZE[0], COVER_SIZE[1], PRIMARY, (13, 31, 51))
    draw = ImageDraw.Draw(img)
    
    paper = data.get('paper', {})
    scores = data.get('scores', {})
    
    # Top brand
    draw.text((80, 60), "AI 系统笔记", font=fonts['bold_normal'], fill=WHITE)
    draw.text((350, 65), "论文速记", font=fonts['regular_normal'], fill=MUTED)
    
    # Category badge
    draw.rounded_rectangle((1850, 50, 2270, 110), radius=30, outline=ACCENT, width=2)
    draw.text((1900, 68), "Agent 系统架构", font=fonts['regular_normal'], fill=ACCENT)
    
    # Main title
    title_cn = paper.get('title_cn', '')
    draw.text((80, 200), title_cn, font=fonts['bold_large'], fill=WHITE)
    
    # Subtitle
    draw.text((80, 340), "记忆、技能与规则的统一框架", font=fonts['bold_medium'], fill=LIGHT_GRAY)
    
    # English title
    draw.text((80, 440), "Experience Compression Spectrum", font=fonts['regular_small'], fill=MUTED)
    
    # Score circle (right side)
    # Draw circle background
    circle_x, circle_y = 1850, 500
    circle_r = 200
    
    # Outer ring (progress)
    total = scores.get('total', 8.3)
    progress = total / 10.0
    
    # Draw background circle
    draw.ellipse((circle_x-circle_r, circle_y-circle_r, circle_x+circle_r, circle_y+circle_r), fill=PRIMARY, outline=(50, 60, 80), width=10)
    
    # Inner circle
    inner_r = 160
    draw.ellipse((circle_x-inner_r, circle_y-inner_r, circle_x+inner_r, circle_y+inner_r), fill=PRIMARY)
    
    # Score text
    draw.text((circle_x-80, circle_y-60), f"{total:.1f}", font=fonts['bold_large'], fill=ACCENT)
    draw.text((circle_x+60, circle_y-20), "/ 10", font=fonts['regular_normal'], fill=MUTED)
    
    # TOP 1 badge
    draw.rounded_rectangle((circle_x-80, circle_y+80, circle_x+80, circle_y+130), radius=25, fill=ACCENT)
    draw.text((circle_x-50, circle_y+95), "TOP 1", font=fonts['bold_normal'], fill=PRIMARY)
    
    # Keywords
    keywords = paper.get('keywords', [])[:3]
    y = 600
    for kw in keywords:
        draw.rounded_rectangle((1850, y, 2270, y+40), radius=20, outline=ACCENT, width=1)
        draw.text((1870, y+8), kw, font=fonts['regular_small'], fill=LIGHT_GRAY)
        y += 50
    
    # Footer
    draw.text((80, 900), f"AI 系统笔记 · {paper.get('authors', '').split(',')[0]} et al.", font=fonts['regular_small'], fill=MUTED)
    draw.text((1900, 900), f"arXiv:{paper.get('arxiv_id', '')}", font=fonts['regular_small'], fill=MUTED)
    
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Cover card saved: {output_path}")

def main():
    """Generate all three cards"""
    import sys
    
    # Default paths
    data_path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    # Load data
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get fonts
    fonts = get_fonts()
    
    # Generate all cards
    generate_score_card(data, os.path.join(output_dir, "score_card.png"), fonts)
    generate_info_card(data, os.path.join(output_dir, "info_card.png"), fonts)
    generate_cover_card(data, os.path.join(output_dir, "cover_235.png"), fonts)
    
    print("\n✅ All cards generated successfully!")

if __name__ == "__main__":
    main()
