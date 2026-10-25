# -*- coding: utf-8 -*-
"""SVG 语法校验：XML 合法性 + 标签闭合 + marker 引用 + 属性完整性 + path 数据粗检。
本机 rsvg-convert 不可用时用这个。
用法: uv run python validate_svg.py <file.svg> [more.svg ...] [--portable]
--portable：可移植模式（目标是 PPT/打印/HMI/PDF 链路时用）——filter/mask/clipPath/
foreignObject 在这些渲染器里行为不一致或直接失效，视为问题报出。
"""
import re
import sys
import xml.etree.ElementTree as ET

问题数 = 0
可移植脆件 = {"filter", "mask", "clippath", "foreignobject"}


def 报(文件, 说明):
    global 问题数
    问题数 += 1
    print(f"  [问题] {文件}: {说明}")


def 画布基准(根):
    """从 viewBox 或 width/height 取画布尺寸，作为坐标是否离谱的参照。"""
    数 = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", 根.attrib.get("viewBox", ""))]
    基准 = max(数[2], 数[3]) if len(数) == 4 else 0.0
    for 键 in ("width", "height"):
        m = re.match(r"([\d.]+)", 根.attrib.get(键, ""))
        if m:
            基准 = max(基准, float(m.group(1)))
    return 基准


def 校验(路径, portable=False):
    print(f"校验: {路径}{'（可移植模式）' if portable else ''}")
    try:
        树 = ET.parse(路径)
    except ET.ParseError as e:
        报(路径, f"XML 解析失败: {e}")
        return
    根 = 树.getroot()
    if not 根.tag.endswith("svg"):
        报(路径, f"根元素不是 svg: {根.tag}")
    if "viewBox" not in 根.attrib:
        报(路径, "根 svg 缺 viewBox（缩放必炸）")

    全部id = set()
    for el in 根.iter():
        if "id" in el.attrib:
            i = el.attrib["id"]
            if i in 全部id:
                报(路径, f"id 重复: #{i}（滤镜/渐变会串引用）")
            全部id.add(i)
    文本 = open(路径, encoding="utf-8").read()
    for ref in set(re.findall(r"url\(#([^)]+)\)", 文本)):
        if ref not in 全部id:
            报(路径, f"url(#{ref}) 引用的 id 不存在")
    for 外引 in set(re.findall(r'(?:href|src)="(https?://[^"]+)"', 文本)):
        报(路径, f"外部引用会离线失效: {外引[:60]}")
    _mm = bool(re.search(r'width="[\d.]+mm"', 文本))
    for m in re.finditer(r'font-size="(\d+(?:\.\d+)?)"', 文本):
        if (float(m.group(1)) < 1.5) if _mm else (float(m.group(1)) < 12):
            报(路径, f"font-size={m.group(1)} < 12，正常缩放下不可读")
            break

    基准 = 画布基准(根)
    坐标上限 = 基准 * 1.25 + 40 if 基准 else 1500
    for el in 根.iter():
        tag = el.tag.split("}")[-1]
        if portable and tag.lower() in 可移植脆件:
            报(路径, f"<{tag}> 是可移植脆件：PPT/打印/HMI 渲染器里会失效或行为不一致")
        for k, v in el.attrib.items():
            if v.strip().startswith("[("):
                报(路径, f"<{tag}> 的 {k}= 疑似塞了 Python list repr: {v[:60]}")
        if tag == "path":
            d = el.attrib.get("d", "")
            if not re.match(r"[Mm]", d):
                报(路径, "path 的 d 属性不以 M/m 开头")
            离谱 = [n for n in re.findall(r"-?\d+(?:\.\d+)?", d) if abs(float(n)) > 坐标上限]
            if 离谱:
                报(路径, f"path 数据疑似异常数字: {d[:60]}")
        if tag == "text" and not (el.text or "").strip() and not list(el):
            报(路径, "text 元素既无内容也无子元素")

    元素数 = sum(1 for _ in 根.iter())
    print(f"  通过: XML 合法, {元素数} 个元素, {len(全部id)} 个 id")


def main():
    args = sys.argv[1:]
    portable = "--portable" in args
    for p in [a for a in args if not a.startswith("--")]:
        校验(p, portable=portable)
    if 问题数:
        print(f"\n共 {问题数} 个问题")
        sys.exit(1)
    print("\n全部通过")


if __name__ == "__main__":
    main()
