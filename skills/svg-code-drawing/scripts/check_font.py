#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""字体名解析与中英混排字体栈。

SVG 里的 font-family 只是一个名字，最终渲染由系统字体匹配决定。这个脚本
把「名字会解析到什么」查清楚，避免三个坑：

1. .ttc 集合取错变体：多语言集合（Noto Sans CJK、Source Han Sans 这类）
   一个文件打包简中、繁中、日文、韩文、香港五个变体，裸名字按索引 0 取，
   而索引 0 常是日文。修法是写带地区后缀的精确名（'Noto Sans CJK SC'）。
2. 字体缺失静默回退：名字不存在时渲染器回退到默认字体，中文字形可能
   变成日文写法。脚本会点名未安装的字体。
3. 中英混排：中文字体和英文字体分开指定，英文在前、中文在后，英文
   字符用英文字体，中文按回退链落到中文字体。

用法：
  uv run --with fonttools python check_font.py --list --cjk
  uv run --with fonttools python check_font.py --check "宋体" "Noto Sans CJK"
  uv run --with fonttools python check_font.py --stack --cn 微软雅黑 --en "Helvetica Neue"
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from fontTools.ttLib import TTCollection, TTFont
except ImportError:
    sys.stderr.write(
        "需要 fontTools。用 uv 运行：\n"
        "  uv run --with fonttools python check_font.py ...\n"
    )
    sys.exit(2)

FONT_EXTS = {".ttf", ".otf", ".ttc", ".otc"}
REGION_SUFFIX = {"SC", "TC", "JP", "KR", "HK", "CN", "TW", "J", "K"}


def font_dirs() -> list[Path]:
    dirs: list[Path] = []
    if sys.platform == "win32":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        dirs.append(Path(windir) / "Fonts")
        local = os.environ.get("LOCALAPPDATA")
        if local:
            dirs.append(Path(local) / "Microsoft" / "Windows" / "Fonts")
    elif sys.platform == "darwin":
        dirs += [
            Path("/System/Library/Fonts"),
            Path("/Library/Fonts"),
            Path.home() / "Library" / "Fonts",
        ]
    else:
        dirs += [
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".local/share/fonts",
            Path.home() / ".fonts",
        ]
    return [d for d in dirs if d.is_dir()]


def localized_name(name_table, name_id: int, lang: int):
    for plat, enc in ((3, 1), (3, 10)):
        rec = name_table.getName(name_id, plat, enc, lang)
        if rec:
            try:
                return rec.toUnicode()
            except Exception:
                pass
    return None


def read_variant(font) -> dict:
    nt = font["name"]
    return {
        "family": (nt.getDebugName(1) or "").strip(),
        "family_zh": (localized_name(nt, 1, 0x804) or "").strip(),
        "full": (nt.getDebugName(4) or "").strip(),
        "ps": (nt.getDebugName(6) or "").strip(),
    }


def has_cjk(font) -> bool:
    try:
        cmap = font.getBestCmap()
    except Exception:
        return False
    if not cmap:
        return False
    for cp in cmap:
        if 0x4E00 <= cp <= 0x9FFF:
            return True
    return False


def scan(only_cjk: bool = False) -> list[dict]:
    """扫描系统字体目录，返回全部变体清单。"""
    out: list[dict] = []
    for d in font_dirs():
        for p in sorted(d.rglob("*")):
            if p.suffix.lower() not in FONT_EXTS:
                continue
            try:
                if p.suffix.lower() in (".ttc", ".otc"):
                    fonts = list(TTCollection(str(p), lazy=True).fonts)
                else:
                    fonts = [TTFont(str(p), lazy=True)]
            except Exception:
                continue
            if only_cjk and not any(has_cjk(f) for f in fonts):
                continue
            for idx, f in enumerate(fonts):
                try:
                    v = read_variant(f)
                except Exception:
                    continue
                if not v["family"]:
                    continue
                v.update({"file": p, "index": idx, "count": len(fonts)})
                out.append(v)
    return out


def region_base(family: str):
    """拆出地区后缀：'Noto Sans CJK SC' → ('Noto Sans CJK', 'SC')。"""
    parts = family.rsplit(" ", 1)
    if len(parts) == 2 and parts[1].upper() in REGION_SUFFIX:
        return parts[0], parts[1].upper()
    return family, None


def find_variants(name: str, variants: list[dict]) -> tuple[list[dict], bool]:
    """查名字命中的变体。返回（命中列表, 是否模糊命中）。

    精确匹配家族名、本地化名、完整名、PostScript 名；都不中时做前缀模糊
    匹配，模拟渲染器的近似解析：裸名 'Noto Sans CJK' 会命中 'Noto Sans
    CJK JP' 这一族，正是取错变体的来源。
    """
    key = name.strip().lower()
    exact = [
        v
        for v in variants
        if v["family"].lower() == key
        or v["family_zh"].lower() == key
        or v["full"].lower() == key
        or v["ps"].lower() == key
    ]
    if exact:
        return exact, False
    fuzzy = [
        v
        for v in variants
        if v["family"].lower().startswith(key + " ") or v["family"].lower().startswith(key)
    ]
    return fuzzy, True


def file_variants(path: Path, variants: list[dict]) -> list[dict]:
    return [v for v in variants if v["file"] == path]


def report_multi_language(path: Path, variants: list[dict]) -> list[str]:
    """同一文件里出现多地区变体时给出警告行。"""
    same = file_variants(path, variants)
    bases: dict[str, list[dict]] = {}
    for v in same:
        base, region = region_base(v["family"])
        if region:
            bases.setdefault(base.lower(), []).append(v)
    warnings: list[str] = []
    for base, group in bases.items():
        if len(group) < 2:
            continue
        warnings.append(f"  多语言集合：一个文件含 {len(group)} 个地区变体，索引 0 是「{group[0]['family']}」")
        for v in group:
            _, region = region_base(v["family"])
            mark = " ← 索引 0，裸名字会取到它" if v["index"] == 0 else ""
            warnings.append(f"    [{v['index']}] {v['family']}（{region}）{mark}")
        sc = [v for v in group if region_base(v["family"])[1] == "SC"]
        if sc:
            warnings.append(f"  建议写成带地区后缀的精确名：'{sc[0]['family']}'")
    return warnings


def cmd_list(variants: list[dict]) -> None:
    seen: set[tuple] = set()
    for v in variants:
        key = (v["family"], v["file"].name, v["index"])
        if key in seen:
            continue
        seen.add(key)
        zh = f"（{v['family_zh']}）" if v["family_zh"] and v["family_zh"] != v["family"] else ""
        tag = f" [{v['index']}/{v['count']}]" if v["count"] > 1 else ""
        print(f"{v['family']}{zh}{tag}  {v['file'].name}")


def cmd_check(names: list[str], variants: list[dict]) -> int:
    problems = 0
    for name in names:
        print(f"{name}")
        hits, fuzzy = find_variants(name, variants)
        if not hits:
            print("  ✗ 系统未安装")
            print("  后果：渲染时静默回退到默认字体，中文字形可能变成日文写法")
            problems += 1
        else:
            if fuzzy:
                print(f"  ⚠ 精确名不存在，近似命中 {len(hits)} 个家族，渲染器选中哪个不确定")
            by_family: dict[str, list[dict]] = {}
            for v in hits:
                by_family.setdefault(v["family"], []).append(v)
            for family, group in by_family.items():
                v = group[0]
                zh = f"（{v['family_zh']}）" if v["family_zh"] and v["family_zh"] != v["family"] else ""
                loc = f"{v['file'].name} 索引 {v['index']}" if v["count"] > 1 else v["file"].name
                extra = f"，同族另有 {len(group) - 1} 个文件" if len(group) > 1 else ""
                mark = "~" if fuzzy else "✓"
                print(f"  {mark} 匹配：{v['family']}{zh}  {loc}{extra}")
            warned = set()
            for v in hits:
                if v["file"] in warned:
                    continue
                warned.add(v["file"])
                for line in report_multi_language(v["file"], variants):
                    print(line)
                    problems += 1
            if fuzzy:
                problems += 1
        print()
    return problems


def cmd_stack(cn: str | None, en: str | None, variants: list[dict]) -> int:
    parts: list[str] = []
    problems = 0
    if en:
        parts.append(f"'{en}'")
    if cn:
        parts.append(f"'{cn}'")
    parts.append("sans-serif")
    print("font-family:", ", ".join(parts))
    print()
    for label, name in (("英文", en), ("中文", cn)):
        if not name:
            continue
        hits, fuzzy = find_variants(name, variants)
        if not hits:
            print(f"⚠ {label}字体「{name}」系统未安装，会回退到链上的下一个字体")
            problems += 1
        elif fuzzy:
            print(f"⚠ {label}字体「{name}」精确名不存在，近似命中：")
            seen: set[str] = set()
            for v in hits[:8]:
                if v["family"] in seen:
                    continue
                seen.add(v["family"])
                print(f"    {v['family']}")
            print("  建议改用上面的精确名，避免渲染器选中别的变体")
            problems += 1
        else:
            v = hits[0]
            zh = f"（{v['family_zh']}）" if v["family_zh"] and v["family_zh"] != v["family"] else ""
            print(f"✓ {label}字体「{name}」→ {v['family']}{zh}  {v['file'].name}")
            for line in report_multi_language(v["file"], variants):
                print(line)
                problems += 1
    print()
    print("写进 SVG 时，根元素带上 xml:lang=\"zh-CN\"，多语言字体按简中字形渲染")
    return problems


def main() -> None:
    ap = argparse.ArgumentParser(description="字体名解析与中英混排字体栈")
    ap.add_argument("--list", action="store_true", help="列出系统字体")
    ap.add_argument("--cjk", action="store_true", help="只列含中日韩字形的字体")
    ap.add_argument("--check", nargs="*", metavar="名字", help="检查字体名解析结果")
    ap.add_argument("--stack", action="store_true", help="生成中英混排字体栈")
    ap.add_argument("--cn", metavar="中文字体", help="中文字体名，可用中文名（宋体、微软雅黑）")
    ap.add_argument("--en", metavar="英文字体", help="英文字体名")
    args = ap.parse_args()

    if not (args.list or args.check or args.stack):
        ap.print_help()
        sys.exit(1)

    variants = scan(only_cjk=args.cjk)

    if args.list:
        cmd_list(variants)
    if args.check:
        sys.exit(1 if cmd_check(args.check, variants) else 0)
    if args.stack:
        sys.exit(1 if cmd_stack(args.cn, args.en, variants) else 0)


if __name__ == "__main__":
    main()
