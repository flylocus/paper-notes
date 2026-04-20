#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build publish_pack.md from simple title/summary inputs.

Usage:
  python3 build_publish_pack.py \
    --out outputs/20260415/2604.09285/publish_pack.md \
    --title "标题1" --title "标题2" --title "标题3" \
    --intro "导语" \
    --summary "摘要版文案"
"""

import argparse
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--title', action='append', default=[])
    ap.add_argument('--intro', required=True)
    ap.add_argument('--summary', required=True)
    args = ap.parse_args()

    titles = args.title or ['默认标题']

    lines = []
    lines.append('# 发布包装\n')
    lines.append('## 备选标题')
    for i, t in enumerate(titles, 1):
        lines.append(f'{i}. {t}')
    lines.append('\n## 导语')
    lines.append(args.intro)
    lines.append('\n## 摘要版文案')
    lines.append(args.summary)
    lines.append('\n## 最终发布前 Checklist')
    lines.append('- [ ] 确认标题使用哪一版')
    lines.append('- [ ] 检查 score_card / info_card / cover_235 是否与正文表述一致')
    lines.append('- [ ] 确认作者与机构展示是否符合发布需求（是否需要精简）')
    lines.append('- [ ] 确认是否保留英文原题与 arXiv 链接')
    lines.append('- [ ] 检查 HTML 在编辑器中的图片相对路径是否正常')
    lines.append('- [ ] 确认正文语气是否符合目标发布渠道')

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(args.out)


if __name__ == '__main__':
    main()
