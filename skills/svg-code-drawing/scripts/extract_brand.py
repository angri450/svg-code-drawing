# -*- coding: utf-8 -*-
"""品牌 onboarding：抓用户网站的 CSS，提取主色板与字体，输出 brand.json。
输出可直接当 generate-from-template.py 的 style_overrides 用。
用法: uv run python extract_brand.py <https://站点> [out.json]
纯 stdlib，无第三方依赖；网络不通/超时会给出明确报错并非零退出。
"""
import json
import re
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from urllib.parse import urljoin

UA = {"User-Agent": "Mozilla/5.0 (brand-extract; svg-code-drawing skill)"}


def 抓(url: str, 超时=15) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=超时) as r:
        编码 = r.headers.get_content_charset() or "utf-8"
        return r.read().decode(编码, errors="replace")


def 拿样式表(页url: str, html: str) -> list:
    css们 = re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I)
    for href in re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', html, re.I):
        链 = urljoin(页url, href)
        if 链.startswith("http"):
            try:
                css们.append(抓(链, 超时=10))
                print(f"  + 外链样式: {链[:80]}")
            except Exception as e:
                print(f"  - 外链取不到 {链[:80]}: {e}")
    return css们


def 提色(css们: list) -> list:
    计 = Counter()
    for c in css们:
        for m in re.finditer(r"(?:^|[:\s,(])((?:#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}))(?=[;\s,)}])", c, re.M):
            色 = m.group(1).lower()
            if len(色) == 4:  # #abc 展开
                色 = "#" + "".join(ch * 2 for ch in 色[1:])
            计[色] += 1
        for m in re.finditer(r"rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)", c):
            r, g, b = (int(x) for x in m.groups())
            计[f"#{r:02x}{g:02x}{b:02x}"] += 1
    def 是品牌候选(色):
        r, g, b = int(色[1:3], 16), int(色[3:5], 16), int(色[5:7], 16)
        return max(r, g, b) - min(r, g, b) > 18  # 有色相才叫品牌色
    排序 = [c for c in 计.most_common(30) if 是品牌候选(c[0])]
    return [c for c, _ in 排序[:8]]


def 提字体(css们: list) -> list:
    栈 = Counter()
    for c in css们:
        for m in re.finditer(r"font-family\s*:\s*([^;}{]+)", c, re.I):
            首 = m.group(1).split(",")[0].strip().strip("'\"")
            if 首 and not re.match(r"(?i)(sans-serif|serif|monospace|system-ui)$", 首):
                栈[首] += 1
    return [f for f, _ in 栈.most_common(3)]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]
    if not url.startswith("http"):
        print("Error: 传 http(s) URL")
        sys.exit(1)
    出 = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path("brand.json").resolve()
    try:
        html = 抓(url)
    except (urllib.error.URLError, OSError) as e:
        print(f"Error: 抓不到 {url}: {e}")
        sys.exit(2)
    css们 = 拿样式表(url, html)
    if not css们:
        print("Error: 页面里没找到任何样式（内联 style 或外链 stylesheet）")
        sys.exit(3)
    色 = 提色(css们)
    字体 = 提字体(css们)
    if not 色:
        print("Error: 没提取到有彩色相的色板（站点可能纯灰阶）")
        sys.exit(4)
    brand = {
        "来源": url,
        "colors": 色,
        "fonts": 字体,
        "说明": "colors 按出现频次排序（已滤黑白灰）；可作 generate-from-template.py 输入里 style_overrides 的取值",
    }
    出.write_text(json.dumps(brand, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ {出}")
    print(f"  色板: {', '.join(色)}")
    print(f"  字体: {', '.join(字体) or '（未提取到自定义字体）'}")


if __name__ == "__main__":
    main()
