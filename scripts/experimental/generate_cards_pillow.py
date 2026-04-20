#!/usr/bin/env python3
"""
使用 Pillow 生成论文卡片图片
生成三张卡片：评分卡、信息卡、封面卡
"""

from PIL import Image, ImageDraw, ImageFont
import json
import os
import sys

def get_fonts():
    """获取字体（优先使用系统中文字体）"""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
        "/System/Library/Fonts/STHeiti Light.ttc",  # macOS 黑体
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",  # Linux 文泉驿
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # 备用
    ]
    
    default_font = None
    for path in font_paths:
        if os.path.exists(path):
            try:
                default_font = path
                break
            except:
                continue
    
    if default_font is None:
        default_font = "/System/Library/Fonts/Helvetica.ttc"
    
    return {
        'large': (default_font, 72),
        'medium': (default_font, 48),
        'normal': (default_font, 32),
        'small': (default_font, 24),
        'tiny': (default_font, 18),
    }

def create_gradient(width, height, color1, color2):
    """创建渐变背景"""
    base = Image.new('RGB', (width, height), color1)
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        for x in range(width):
            base.putpixel((x, y), (r, g, b))
    return base

def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def generate_score_card(data, output_path, fonts):
    """生成评分卡"""
    width, height = 1200, 800
    
    # 创建渐变背景
    img = create_gradient(width, height, (11, 20, 48), (26, 42, 74))
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    font_large = ImageFont.truetype(*fonts['large'])
    font_medium = ImageFont.truetype(*fonts['medium'])
    font_normal = ImageFont.truetype(*fonts['normal'])
    font_small = ImageFont.truetype(*fonts['small'])
    
    # 标题区域
    draw.text((60, 60), "评分卡", font=font_large, fill=(255, 255, 255))
    draw.text((60, 150), "Experience Compression Spectrum", font=font_normal, fill=(200, 200, 200))
    
    # 总分区域
    score = data.get('scores', {}).get('total', 8.3)
    draw.text((900, 100), f"{score}", font=ImageFont.truetype(*fonts['large']), fill=(76, 195, 255))
    draw.text((1050, 130), "/ 10", font=font_medium, fill=(150, 150, 150))
    
    # 排名
    draw.rounded_rectangle((900, 200, 1100, 260), radius=30, fill=(76, 195, 255))
    draw.text((960, 215), "TOP 1", font=font_normal, fill=(11, 20, 48))
    
    # 五个维度
    dimensions = data.get('scores', {}).get('dimensions', {})
    dim_names = [
        ("重要性 Impact", dimensions.get('impact', 1.8)),
        ("创新性 Novelty", dimensions.get('novelty', 1.8)),
        ("可验证性 Evidence", dimensions.get('evidence', 1.4)),
        ("产业可用性 Applicability", dimensions.get('applicability', 1.7)),
        ("可复用性 Reusability", dimensions.get('reusability', 1.6)),
    ]
    
    y_start = 350
    for i, (name, score) in enumerate(dim_names):
        y = y_start + i * 80
        # 维度名称
        draw.text((60, y), name, font=font_small, fill=(220, 220, 220))
        # 进度条背景
        draw.rounded_rectangle((350, y+5, 750, y+30), radius=12, fill=(50, 60, 80))
        # 进度条
        width = int(400 * score / 2.0)
        draw.rounded_rectangle((350, y+5, 350+width, y+30), radius=12, fill=(76, 195, 255))
        # 分数
        draw.text((780, y), f"{score:.1f}/2", font=font_small, fill=(76, 195, 255))
    
    # 底部信息
    draw.text((60, 750), "AI 系统笔记 · 论文速记", font=font_small, fill=(150, 150, 150))
    draw.text((900, 750), "arXiv:2604.15877", font=font_small, fill=(150, 150, 150))
    
    # 保存
    img.save(output_path, 'PNG', quality=95)
    print(f"评分卡已保存: {output_path}")

def generate_info_card(data, output_path, fonts):
    """生成信息卡"""
    width, height = 800, 1000
    
    # 创建渐变背景
    img = create_gradient(width, height, (11, 20, 48), (26, 42, 74))
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    font_large = ImageFont.truetype(*fonts['medium'])
    font_medium = ImageFont.truetype(*fonts['normal'])
    font_small = ImageFont.truetype(*fonts['small'])
    font_tiny = ImageFont.truetype(*fonts['tiny'])
    
    # 标题区域
    paper = data.get('paper', {})
    draw.text((50, 50), paper.get('title_cn', ''), font=font_large, fill=(255, 255, 255))
    draw.text((50, 120), paper.get('title', '')[:60] + '...', font=font_tiny, fill=(180, 180, 180))
    
    # 元信息区域
    y = 200
    meta_items = [
        ("作者", paper.get('authors', '')),
        ("arXiv ID", paper.get('arxiv_id', '')),
        ("关键词", ', '.join(paper.get('keywords', [])[:4])),
        ("领域", paper.get('category', '')),
    ]
    
    for label, value in meta_items:
        draw.text((50, y), label, font=font_tiny, fill=(150, 150, 150))
        draw.text((150, y), value[:70], font=font_small, fill=(220, 220, 220))
        y += 60
    
    # 评分区域
    scores = data.get('scores', {})
    y = 550
    draw.rounded_rectangle((50, y, 750, y+300), radius=16, fill=(255, 255, 255, 10), outline=(76, 195, 255, 50))
    
    # 总分
    total = scores.get('total', 8.3)
    draw.text((400, y+50), f"{total}", font=ImageFont.truetype(*fonts['large']), fill=(76, 195, 255))
    draw.text((550, y+80), "/ 10", font=font_medium, fill=(150, 150, 150))
    
    # 排名
    draw.rounded_rectangle((300, y+150, 500, y+200), radius=25, fill=(76, 195, 255))
    draw.text((370, y+165), "TOP 1", font=font_medium, fill=(11, 20, 48))
    
    # 底部
    draw.text((50, 960), "AI 系统笔记 · 论文速记", font=font_tiny, fill=(150, 150, 150))
    draw.text((600, 960), f"arXiv:{paper.get('arxiv_id', '')}", font=font_tiny, fill=(150, 150, 150))
    
    # 保存
    img.save(output_path, 'PNG', quality=95)
    print(f"信息卡已保存: {output_path}")

def generate_cover_card(data, output_path, fonts):
    """生成封面卡（2.35:1）"""
    width, height = 2350, 1000
    
    # 创建渐变背景
    img = create_gradient(width, height, (11, 20, 48), (13, 31, 51))
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    font_huge = ImageFont.truetype(*fonts['large'])
    font_large = ImageFont.truetype(*fonts['medium'])
    font_medium = ImageFont.truetype(*fonts['normal'])
    font_small = ImageFont.truetype(*fonts['small'])
    font_tiny = ImageFont.truetype(*fonts['tiny'])
    
    # 顶部品牌区域
    draw.text((80, 60), "AI 系统笔记", font=font_medium, fill=(255, 255, 255))
    draw.text((450, 60), "论文速记", font=font_small, fill=(150, 150, 150))
    
    # 右侧分类标签
    draw.rounded_rectangle((1850, 50, 2270, 110), radius=30, fill=(76, 195, 255, 30), outline=(76, 195, 255))
    draw.text((1900, 65), "Agent 系统架构", font=font_small, fill=(76, 195, 255))
    
    # 主标题区域（左侧）
    paper = data.get('paper', {})
    title_cn = paper.get('title_cn', '')
    
    # 主标题（大字）
    draw.text((80, 200), "经验压缩谱", font=ImageFont.truetype(*fonts['large']), fill=(255, 255, 255))
    
    # 副标题
    draw.text((80, 340), "记忆、技能与规则的统一框架", font=font_large, fill=(200, 200, 200))
    
    # 英文标题
    draw.text((80, 440), "Experience Compression Spectrum", font=font_tiny, fill=(150, 150, 150))
    
    # 评分区域（右侧圆形）
    scores = data.get('scores', {})
    total = scores.get('total', 8.3)
    
    # 绘制圆形背景
    circle_x, circle_y = 1850, 500
    circle_r = 200
    
    # 外圆（进度环）
    import math
    for angle in range(0, 298):  # 8.3/10 = 83% = 298 degrees
        rad = math.radians(angle - 90)
        x = circle_x + int((circle_r + 20) * math.cos(rad))
        y = circle_y + int((circle_r + 20) * math.sin(rad))
        draw.ellipse((x-8, y-8, x+8, y+8), fill=(76, 195, 255))
    
    # 内圆背景
    draw.ellipse((circle_x-circle_r, circle_y-circle_r, circle_x+circle_r, circle_y+circle_r), fill=(11, 20, 48))
    
    # 分数
    score_str = f"{total}"
    draw.text((circle_x-80, circle_y-60), score_str, font=ImageFont.truetype(*fonts['large']), fill=(76, 195, 255))
    draw.text((circle_x+60, circle_y-20), "/ 10", font=font_medium, fill=(150, 150, 150))
    
    # TOP 1 标签
    draw.rounded_rectangle((circle_x-80, circle_y+80, circle_x+80, circle_y+130), radius=25, fill=(76, 195, 255))
    draw.text((circle_x-50, circle_y+95), "TOP 1", font=font_medium, fill=(11, 20, 48))
    
    # 底部信息
    draw.text((80, 900), f"AI 系统笔记 · {paper.get('authors', '').split(',')[0]} et al.", font=font_tiny, fill=(150, 150, 150))
    draw.text((1900, 900), f"arXiv:{paper.get('arxiv_id', '')}", font=font_tiny, fill=(150, 150, 150))
    
    # 保存
    img.save(output_path, 'PNG', quality=95)
    print(f"封面卡已保存: {output_path}")

def main():
    """主函数"""
    import sys
    
    # 默认数据文件路径
    data_path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    # 加载数据
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取字体
    fonts = get_fonts()
    
    # 生成三张卡片
    generate_score_card(data, os.path.join(output_dir, "score_card.png"), fonts)
    generate_info_card(data, os.path.join(output_dir, "info_card.png"), fonts)
    generate_cover_card(data, os.path.join(output_dir, "cover_235.png"), fonts)
    
    print("所有卡片生成完成！")

if __name__ == "__main__":
    main()
