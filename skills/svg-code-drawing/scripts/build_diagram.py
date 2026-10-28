# -*- coding: utf-8 -*-
"""一条命令走完：生成 → 校验 → 导出 PNG（跨平台）。

用法:
  python build_diagram.py --type architecture --out out.svg [--data '{"title":"..."}']
                          [--style 1] [--png out.png] [--width 1920] [--portable] [--no-validate]

说明:
  --type   14 种图型之一（agent/architecture/class/comparison/data-flow/er-diagram/
           flowchart/memory/mind-map/network-topology/sequence/state-machine/timeline/use-case）
  --data   传给 generate-from-template.py 的数据；可以给 JSON 文件路径，
           也可以直接给 JSON 串，不给就从 stdin 读
  --style  1-7 配色风格，默认 1
  --portable 目标要进 PPT/打印/HMI/PDF 时加，校验会拦下 filter/mask/clipPath 等脆件
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
图型 = ["agent", "architecture", "class", "comparison", "data-flow", "er-diagram",
        "flowchart", "memory", "mind-map", "network-topology", "sequence",
        "state-machine", "timeline", "use-case"]


def 跑(args: list[str], stdin: str | None = None) -> int:
    r = subprocess.run([sys.executable] + args, input=stdin, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    for line in (r.stdout or "").splitlines():
        print(line)
    if r.returncode != 0:
        for line in (r.stderr or "").splitlines():
            print(line, file=sys.stderr)
    return r.returncode


def main() -> None:
    ap = argparse.ArgumentParser(description="生成 + 校验 + 导出 PNG")
    ap.add_argument("--type", required=True, choices=图型)
    ap.add_argument("--out", required=True, help="输出 SVG 路径")
    ap.add_argument(
        "--data",
        default=None,
        help="生成用数据。可以给 JSON 文件路径，也可以直接给 JSON 串；"
             "不给从 stdin 读",
    )
    ap.add_argument("--style", default="1", help="配色风格 1-7 或风格名，默认 1")
    ap.add_argument("--png", default=None, help="同时导出 PNG 到这个路径")
    ap.add_argument("--width", type=int, default=1920, help="PNG 目标宽度")
    ap.add_argument("--portable", action="store_true", help="可移植模式校验")
    ap.add_argument("--no-validate", action="store_true", help="跳过校验")
    args = ap.parse_args()

    raw = args.data if args.data is not None else sys.stdin.read()
    # --data 给文件路径时读文件，给 JSON 串时直接解析。两种都试，
    # 免得传了路径却报"JSON 解析失败"，看不出是路径写错还是内容错。
    候选 = [raw]
    看起来是路径 = raw.strip().startswith("{") is False
    if 看起来是路径:
        候选.insert(0, Path(raw).read_text(encoding="utf-8") if Path(raw).is_file() else raw)
    最后错误 = None
    for 试 in 候选:
        try:
            data = json.loads(试)
            break
        except json.JSONDecodeError as e:
            最后错误 = e
    else:
        print(f"Error: JSON 解析失败: {最后错误}", file=sys.stderr)
        if 看起来是路径 and not Path(raw).is_file():
            print(f"       找不到文件 {raw}", file=sys.stderr)
        sys.exit(1)
    data.setdefault("style", args.style)

    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"生成 {args.type} (style {data['style']}) → {out}")
    if 跑([str(HERE / "generate-from-template.py"), args.type, str(out), json.dumps(data, ensure_ascii=False)]) != 0:
        sys.exit(1)

    if not args.no_validate:
        vargs = [str(HERE / "validate_svg.py"), str(out)]
        if args.portable:
            vargs.append("--portable")
        if 跑(vargs) != 0:
            print("Error: 校验没过，先修再导出。", file=sys.stderr)
            sys.exit(1)

    if args.png:
        跑([str(HERE / "export_png.py"), str(out), str(Path(args.png).resolve()), str(args.width)])

    print(f"✓ {out}")


if __name__ == "__main__":
    main()
