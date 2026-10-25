# 字体：中英混排与 .ttc 规避

## 中英混排

font-family 列表按顺序做字形回退，英文名在前、中文名在后：英文、数字、标点用英文字体，中文按回退链落到中文字体。

```
font-family: 'Georgia', '宋体', sans-serif;
```

生成器直接传参：

```json
{"font_en": "Georgia", "font_cn": "宋体"}
```

输出的 SVG 根元素自动带 `xml:lang="zh-CN"`，多语言字体按简中字形渲染（触发字体的 locl 特性）。传 `"lang": ""` 可以去掉这个属性。

## .ttc 集合的坑

.ttc（TrueType Collection）一个文件打包多个字体。两种踩法，结果都是中文字渲染成日文写法（「直」「骨」「今」这类字最容易看出）。

**一、多语言集合取错变体。** Noto Sans CJK、Source Han Sans 这类集合，一个文件含简中、繁中、日文、韩文、香港五个变体，裸名字按索引 0 取，而索引 0 常是日文。修法是写带地区后缀的精确名：

```
'Noto Sans CJK SC'      ← 正确
'Noto Sans CJK'         ← 裸名，可能取到日文变体
```

Windows 自带的 simsun.ttc（SimSun + NSimSun）、msyh.ttc（YaHei + YaHei UI）只含简中变体，没有这个问题，但同样建议先查一遍再写。

**二、名字不存在静默回退。** 字体没装时渲染器回退到默认字体，某些系统（尤其是 Linux）默认 CJK 字体是日文字体，同样出日文字形。名字写错一个字母就可能触发。

## 机制：check_font.py

写字体名前先查一遍，三个命令：

```bash
# 检查字体名会解析到什么文件、哪个索引；点名未安装的；标出多语言集合
uv run --with fonttools python scripts/check_font.py --check "宋体" "Noto Sans CJK"

# 生成中英混排字体栈
uv run --with fonttools python scripts/check_font.py --stack --cn 微软雅黑 --en "Helvetica Neue"

# 列出系统里含中日韩字形的字体
uv run --with fonttools python scripts/check_font.py --list --cjk
```

`--check` 对多语言集合会给建议（`建议写成带地区后缀的精确名：'Noto Sans CJK SC'`），对未安装的字体点名后果（回退到默认字体的风险）。退出码非零表示有问题。

## 本机实测（Windows 11）

`check_font.py --check` 在本机的结果：宋体命中 simsun.ttc 索引 0，微软雅黑命中 msyh.ttc 索引 0，Noto Sans CJK 未安装。所以本机的中文字体写 `'Microsoft YaHei'` 或 `'宋体'` 都能命中，不要拿 `'Noto Sans CJK'` 兜底（没装，会被静默回退）。

未安装的名字会被渲染器静默回退到默认字体，中文可能出日文字形，所以每加一个新字体名先跑一次 `--check`。

## 常用字体对

| 中文 | 英文 | 场景 |
|---|---|---|
| 微软雅黑 | Segoe UI、Helvetica Neue | 屏幕、通用 |
| 宋体 | Times New Roman、Georgia | 正式、印刷 |
| 黑体 | Arial、Segoe UI Semibold | 强调、标题 |
| Noto Sans SC | Inter、Source Sans | 开源、跨平台 |
| 楷体 | Georgia | 手写感 |

英文字体名在 Windows 上优先选自带的（Segoe UI、Georgia、Times New Roman、Arial、Consolas），macOS 场景用 Helvetica Neue、SF Pro，Linux 场景用 DejaVu、Liberation。链上写多个，缺哪个回退哪个。
