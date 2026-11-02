# 混合管线：画风归生图、文字归代码

需要画风质感（吉卜力/日漫/水彩氛围）时走这条。SVG 管结构与文字，MiniMax 出图通道管氛围，base64 内嵌合成单文件 SVG。

## 出底图：MiniMax 出图通道

底图和配件都走本机的 MiniMax 出图通道，文生图和改图是同一个入口：

```bash
mcode-tools connector call connector__matrix__generate_image --args-file 参数.json
```

```json
{"requests": [{"prompt": "底图提示词", "aspect_ratio": "16:9", "resolution": "2K"}]}
```

`aspect_ratio` 可选 `1:1`、`16:9`、`9:16`、`4:3`、`3:4`、`21:9`，`resolution` 可选 `1K`、`2K`、`4K`。改图时把参考图放进 `input_urls`，本地图先 `mcode-tools upload_temp_url 图.png` 换成临时地址。

成功后返回 `node_id`，调 `mcode-tools get_asset_url <node_id>` 取下载地址，再下载成本地 PNG 交给合成脚本。一次只提交一条请求，失败率低。

## 一键合成：compose_layers.py

抠图、摆位、合成、自检全部由脚本完成，生成侧只读数字，不反复看图。

```bash
uv run --with opencv-python-headless --with numpy --with resvg-py python scripts/compose_layers.py \
  --bg 底.png --svg 线稿.svg --out 成品.svg [--png 成品.png] [--wide 1600] \
  --prop 工人.png:612:373:72 --prop 猫.png:238:396:46
```

PNG 导出按 resvg → rsvg-convert → Chromium 自动降级；本机装了 resvg-py，`uv run` 时带 `--with resvg-py` 就能直接出 PNG。

--prop 格式 `路径:x:y:h`（viewBox 单位）；省略坐标时自动居中底部，h=60。路径解析兼容 Windows 盘符，从右往左剥坐标。

配件默认不做去水印处理。素材确实带水印时加 `--remove-watermark`，默认清右下 20% 宽 × 7% 高；水印位置不固定时用 `--watermark-box x1,y1,x2,y2` 指定像素区域。

数字验收线（全部达标即可，无需目检）：
每个配件不透明占比 40-60% 为正常，低于 10% 判为抠图漏底，直接报错不出图；
输出文件 KB 数合理（底图加两配件约 4MB 级）；
validate_svg.py 全部通过（data URI 不是 http 外链，可以过检）。
最终目检只保留一次，由用户查看交付物。

## 选画幅

按线稿 viewBox 宽高比选最接近的 `aspect_ratio`，比例差超过 25% 时 slice 裁切会伤内容。

1. 内容贴上下边（标题、图例）时选更宽的横图幅，裁切只裁左右。
2. 内容贴左右边（多设备横排）时选更高的竖图幅。
3. 上下左右都贴时选最接近的图幅，并在 prompt 里放大留白承诺（如"95% 宽"）。
4. 每次出图把所选图幅和理由写进汇报，换主题或换画布尺寸必须重选。

## 读图修改循环

先判断浏览器在哪台机器。`127.0.0.1` 是回环地址，只指服务器自己；内置浏览器或远程浏览器打开只会"拒绝连接"。

### 同一台机器：点选 SVG

1. 在产物目录起 `uv run python -m http.server 8897`（避开被旧进程占用的端口），用 `bundle_html.py 成品.svg --title "审查标题"` 生成 HTML 壳并打开。HTML 内联版撑满窗格，每个元素是可点 DOM；文件名用 ASCII，中文名在 http.server 上 404。
2. 用户在页面上点选元素、圈出问题。
3. 修法是改线稿 SVG 的坐标（如标题 y=46→82），重跑 compose_layers.py（秒级），浏览器刷新即见。
4. 底图构图缺陷（纸太小、场景侵入）才重出背景；先修线稿坐标试一轮，确认是底图问题再重新生成。
5. 循环到用户确认。每轮只合成一次。

### 浏览器不在同一台机器：单文件标注页

1. 不要起 `http.server`，也不要把 `127.0.0.1` 发给用户。运行：

   ```bash
   uv run --with pillow python scripts/annotate_html.py 成品.png --out review.html --title "图稿评审"
   ```

2. 把 HTML 用 `website_deploy` 发布成 MiniMax 站点链接，或直接把文件发给用户。页面自带图片，不需要服务器、端口、外链。
3. 用户框选/点选，写说明，点"导出 JSON"或"复制 JSON"。
4. 读 `annotations.json`，按 `rect`/`point` 坐标改 SVG，重跑 compose_layers.py。
5. 重新导出 PNG，再生成一份新的标注页给用户复查。每轮只合成一次。

详细字段和消费流程见 [annotation-review.md](annotation-review.md)。

## 管线（线稿先行）

顺序：线稿 → 算包围盒 → 背景 prompt 按盒承诺留白 → 配件 → 合成。先画背景再画线稿会让场景元素侵入线稿区，导致标题压暗底、标签被遮、设备悬在场景边缘。

1. 线稿层：先画完 SVG（P&ID/示意图，铅笔风与水彩底搭配）。
2. 算内容包围盒：标题最上、图例最下、最左/最右元素边缘，四周留 5-8% 余量。例：700×500 画布内容 x∈[40,660] y∈[40,452]，背景"必须空白"区约为全幅 92% 宽 × 90% 高。
3. 氛围底：按包围盒写死留白承诺。prompt 模板："画面中央 {宽}% × {高}% 必须是干净空白纸面（无任何物体/文字/深色块），场景元素只允许出现在四周 {余量}% 的窄边框里"。比例数字按包围盒计算填入。改图时反过来：拿线稿当参考，指令"线稿区域全部替换为空白纸面，只保留边缘装饰"。
4. 配件小图（可选）：工人、动物、道具。prompt 要求"纯白背景、单主体、无阴影、无文字"。摆位对照线稿标签坐标，不压设备标签、图例、标题。
5. 合成：优先走 compose_layers.py。手工合成时剥掉 SVG 纯色底纸矩形，最前面插入 `<image href="data:image/png;base64,…">` 铺满 viewBox（`preserveAspectRatio="xMidYMid slice"`）。
6. 验收：按数字验收线，并目检"标题无暗底、标签无遮挡、设备全在纸上"。

## 三层布景：底图 + 配件层 + 线稿层

配件层是出图通道出的小图（工人/动物/道具/实地元素），坐标由 SVG 控制，站在设备旁营造场景感。

1. 出配件：prompt 要求"纯白背景、单主体、无阴影、无文字"，白底是抠图前提。文生图直接出；改图拿已有图当参考。
2. 抠图：不用洪水填充。水彩/手绘软边会渗漏，填充会沿抗锯齿边缘钻进角色内部。用连通域方案：近白阈值（亮度>228 且饱和度<30）→ connectedComponents → 只有贴画布边界的近白连通块判为背景。动画描边反而有利：内部浅色被黑线包住，与边界断开。
3. 后处理：默认不做去水印；素材确实带水印时加 `--remove-watermark`，或用 `--watermark-box` 指定区域。按 alpha bbox 裁边；按目标尺寸换算 viewBox 坐标（700×500 画布中配件建议高 40-75 单位）。
4. 叠层顺序：底图 → 配件 `<image>`（脚对齐设备地面线 y≈440-445）→ 线稿与文字层。线稿在最上层，位号不被遮。
5. 检查配件不透明占比（正常 40-60%），低于 10% 说明抠漏，回到第 2 步。

## 边界

结构层始终由 SVG 输出，生图只出底图或做整体风格化。
氛围底是位图，放大幅度有限；工程交付仍走纯 SVG 管线。
叠印图适合封面、报告插图、演示；期刊投稿不走此管线。
