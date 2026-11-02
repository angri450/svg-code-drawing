#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""趋势 + 摆动 + 包络 的曲线生成器。

把一个 JSON 配置变成两条岸线，中间是河道。
三层模型和推导见 references/curve-composition.md。

用法：
  python curve_builder.py curve.json --out river.svg
  python curve_builder.py curve.json --fit-phase 265 --report
"""

import argparse
import json
import math
from pathlib import Path


def trend(x, t):
    return t.get("b", 0.0) + t.get("k", 0.0) * x


def wave_amp(x, w):
    return w.get("a0", 0.0) + w.get("ak", 0.0) * x


def phase(x, w):
    f0, f1, L = w["f0"], w["f1"], w["L"]
    return 2 * math.pi * (f0 * x + (f1 - f0) * x * x / (2 * L)) + w.get("phi0", 0.0)


def swing(x, w):
    return wave_amp(x, w) * math.sin(phase(x, w))


def center(x, cfg):
    return trend(x, cfg["trend"]) + swing(x, cfg["wave"])


def half(x, cfg):
    e = cfg["envelope"]
    return e.get("h0", 0.0) + e.get("hk", 0.0) * x - e.get("hq", 0.0) * x * x


def banks(x, cfg):
    c, h = center(x, cfg), half(x, cfg)
    return c + h, c - h


def fit_phase(x1, cfg, trough=True):
    """给定特征点的 x，反解让波形在此落到谷（或峰）的初始相位。"""
    w = cfg["wave"]
    target = 3 * math.pi / 2 if trough else math.pi / 2
    f0, f1, L = w["f0"], w["f1"], w["L"]
    base = 2 * math.pi * (f0 * x1 + (f1 - f0) * x1 * x1 / (2 * L))
    k = round((target - base) / (2 * math.pi))
    return target + 2 * math.pi * k - base


def sample(cfg, n=400):
    w = cfg["canvas"]["w"]
    return [(w * i / n, *banks(w * i / n, cfg)) for i in range(n + 1)]


def to_svg(cfg, pts):
    w, h = cfg["canvas"]["w"], cfg["canvas"]["h"]
    flip = cfg.get("svg_flip", True)

    def sy(y):
        return h - y if flip else y

    upper = " ".join(f"{x:.1f},{sy(u):.1f}" for x, u, _ in pts)
    lower_line = " ".join(f"{x:.1f},{sy(l):.1f}" for x, _, l in pts)
    lower_rev = " ".join(f"{x:.1f},{sy(l):.1f}" for x, _, l in reversed(pts))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">\n'
        f'  <rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'  <polygon points="{upper} {lower_rev}" fill="#cfe3ee"/>\n'
        f'  <polyline points="{upper}" fill="none" stroke="#c0392b" stroke-width="3"/>\n'
        f'  <polyline points="{lower_line}" fill="none" stroke="#2c6e8a" stroke-width="3"/>\n'
        f'</svg>\n'
    )


def report(cfg):
    w = cfg["canvas"]["w"]
    print(f"画布 {w} x {cfg['canvas']['h']}")
    print(f"{'x':>6} {'上缘':>9} {'下缘':>9} {'河宽':>9} {'圈数':>8}")
    for frac in (0, 0.25, 0.5, 0.75, 1.0):
        x = w * frac
        u, l = banks(x, cfg)
        turns = phase(x, cfg["wave"]) / (2 * math.pi)
        print(f"{x:6.0f} {u:9.1f} {l:9.1f} {u - l:9.1f} {turns:8.2f}")


def main():
    ap = argparse.ArgumentParser(description="趋势 + 摆动 + 包络的曲线生成器")
    ap.add_argument("config")
    ap.add_argument("--out")
    ap.add_argument("--samples", type=int, default=400)
    ap.add_argument("--fit-phase", type=float, metavar="X1",
                    help="用第一个波谷的 x 反解初始相位")
    ap.add_argument("--peak", action="store_true", help="配合 --fit-phase，按波峰对表")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))

    if args.fit_phase is not None:
        phi0 = fit_phase(args.fit_phase, cfg, trough=not args.peak)
        print(f"phi0 = {phi0:.4f}（{phi0 / math.pi:.3f}π）")
        cfg["wave"]["phi0"] = phi0

    if args.report:
        report(cfg)

    if args.out:
        Path(args.out).write_text(to_svg(cfg, sample(cfg, args.samples)), encoding="utf-8")
        print(f"写出 {args.out}")


if __name__ == "__main__":
    main()
