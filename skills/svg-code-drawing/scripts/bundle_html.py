# -*- coding: utf-8 -*-
"""把 SVG 打包成单文件 HTML 交付物（内联 SVG，双击即开，文字可选中）。
用法: uv run python bundle_html.py <in.svg> [out.html] [--title 标题] [--inspect]
--inspect：注入审查交互——hover 描边高亮任意元素并浮出其类型/文字，点击锁定信息。
多张 SVG 依次传入可拼一页画板。
"""
import re
import sys
from pathlib import Path

审查层 = """
<style>
  .insp-tip{position:fixed;z-index:99;background:#111c27;color:#e2e8f0;font:12px/1.5 'FangSong SC','Times New Roman',serif;
    padding:5px 10px;border-radius:6px;pointer-events:none;max-width:340px;white-space:pre-wrap}
  .insp-on [data-insp]:hover{outline:2px dashed #2563eb;outline-offset:2px;cursor:crosshair}
  .insp-on [data-insp].insp-sel{outline:2px solid #e11d48!important}
</style>
<script>
document.addEventListener('DOMContentLoaded',()=>{
  document.body.classList.add('insp-on');
  let tip=document.createElement('div');tip.className='insp-tip';tip.style.display='none';
  document.body.appendChild(tip);
  document.querySelectorAll('svg *').forEach(el=>{if(el.tagName!=='defs'&&el.tagName!=='g')el.setAttribute('data-insp','')});
  document.addEventListener('mouseover',e=>{
    const t=e.target.closest('[data-insp]');if(!t){tip.style.display='none';return}
    const txt=(t.textContent||'').trim().slice(0,60);
    tip.textContent=t.tagName.toLowerCase()+(txt?'  文字: '+txt:'');
    tip.style.display='block';
    tip.style.left=Math.min(e.clientX+14,innerWidth-360)+'px';
    tip.style.top=(e.clientY+16)+'px';
  });
  document.addEventListener('click',e=>{
    const t=e.target.closest('[data-insp]');if(!t)return;
    document.querySelectorAll('.insp-sel').forEach(x=>x.classList.remove('insp-sel'));
    t.classList.add('insp-sel');
    const txt=(t.textContent||'').trim().slice(0,60);
    console.log('INSPECT-CLICK', t.tagName.toLowerCase(), JSON.stringify(txt), e.clientX, e.clientY);
    e.preventDefault();e.stopPropagation();
  },true);
});
</script>
"""


def 内联(svg: Path) -> str:
    文 = svg.read_text(encoding="utf-8")
    m = re.search(r"<svg\b.*?</svg>", 文, re.S)
    if not m:
        raise SystemExit(f"Error: {svg} 里找不到 svg 元素")
    片 = m.group(0)
    片 = re.sub(r'<svg([^>]*?)\swidth="\d+(?:\.\d+)?"', r"<svg\1", 片, count=1)
    片 = re.sub(r'<svg([^>]*?)\sheight="\d+(?:\.\d+)?"', r"<svg\1", 片, count=1)
    return 片.replace("<svg", '<svg style="max-width:100%;height:auto"', 1)


def main():
    args = [a for a in sys.argv[1:]]
    标题 = "SVG 制图交付"
    if "--title" in args:
        i = args.index("--title")
        标题 = args[i + 1]
        del args[i:i + 2]
    审查 = "--inspect" in args
    if 审查:
        args.remove("--inspect")
    if not args:
        print(__doc__)
        sys.exit(1)
    源们 = [Path(a).resolve() for a in args]
    for s in 源们:
        if not s.is_file():
            raise SystemExit(f"Error: 找不到 {s}")
    出 = 源们[0].with_suffix(".html") if len(源们) == 1 else 源们[0].parent / f"{源们[0].stem}-拼页.html"

    画板 = "\n".join(
        f'<section class="board"><h2>{s.stem}</h2>{内联(s)}</section>' for s in 源们
    )
    html = f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><title>{标题}</title>
<style>
  body {{ margin:0; background:#eef1f4; font-family:'Times New Roman','FangSong SC',serif; }}
  h1 {{ margin:18px 24px 10px; font-size:18px; font-weight:600; }}
  .board {{ background:#fff; margin:16px 20px; padding:12px; border-radius:10px;
           box-shadow:0 2px 10px rgba(0,0,0,.12); }}
  .board h2 {{ margin:2px 4px 10px; font-size:14px; color:#666; font-weight:500; }}
</style></head>
<body><h1>{标题}</h1>
{画板}
{审查层 if 审查 else ""}
</body></html>"""
    出.write_text(html, encoding="utf-8")
    print(f"✓ {出}  ({出.stat().st_size} bytes, {len(源们)} 张画板)")


if __name__ == "__main__":
    main()
