# CQUE-ACMers 赛题 LaTeX 模板

重庆第二师范学院 · 数学与大数据学院 CQUE-ACMers 集训队专用 ACM 赛题排版模板。

## 项目简介

本模板为 CQUE-ACMers 集训队定制的 ACM/ICPC 赛题 LaTeX 排版解决方案，融合学校视觉形象识别系统（VIS），提供从 Markdown 到 PDF 的一键构建能力。

### 特性

- **学校专属视觉** — 封面使用重庆第二师范学院 VIS 规范标识（校训、校风、学风等）
- **双色边框封面** — 深蓝 + 金色双边框设计，简洁庄重
- **正文水印** — 主标识简化图案半透明水印（仅正文页，封面/目录页自动跳过）
- **交替页脚** — 页脚交替展示"学风"与"形象宣传语"VIS 图案
- **代码高亮框** — 样例输入/输出自动转为带边框的 lstlisting 代码框
- **自动分页** — 每题自动从新页开始
- **一键构建** — Markdown 源文件 → `build_pdf.py` → 可直接交付的 PDF

## 目录结构

```
CQUE-ACMers-Templates/
├── template.tex          # LaTeX 主模板（含封面命令、样式、水印等）
├── build_pdf.py          # MD → PDF 一键构建脚本
├── README.md             # 本文件
├── SKILL.md              # AI 助手使用指南
├── .gitignore
├── assets/               # VIS 视觉素材
│   ├── 主标识简化图案.png
│   ├── 主标识与校名中英文组合（上下横式）.png
│   ├── 校训.png
│   ├── 校风.png
│   ├── 教风.png
│   ├── 学风.png
│   ├── 形象宣传语.png
│   ├── 中文校名.png
│   └── 主标识.png
└── examples/             # 示例输出
    └── template.pdf
```

## 前置依赖

| 工具 | 用途 | 安装方式 |
|------|------|----------|
| **XeLaTeX** (TeX Live / MiKTeX) | LaTeX 编译引擎 | [TUG.org](https://tug.org/) |
| **Pandoc** | Markdown → LaTeX 转换 | `winget install pandoc` 或 [pandoc.org](https://pandoc.org/) |
| **Python 3** | 构建脚本运行环境 | [python.org](https://python.org/) |

**所需 LaTeX 宏包：**
`ctex`、`xcolor`、`geometry`、`fancyhdr`、`lastpage`、`titlesec`、`enumitem`、`framed`、`listings`、`longtable`、`booktabs`、`hyperref`、`graphicx`、`tikz`、`atbegshi`、`amsmath`、`amssymb`、`bookmark`

**字体要求：**
- 中文字体：SimSun（宋体）、SimHei（黑体）、KaiTi（楷体）
- 英文字体：Times New Roman、Consolas

## 使用方法

### 1) 直接编译模板（查看效果）

```bash
cd CQUE-ACMers-Templates
xelatex -shell-escape template.tex
xelatex -shell-escape template.tex   # 需两遍编译以解析交叉引用
```

### 2) 从 Markdown 构建赛题 PDF

```bash
cd CQUE-ACMers-Templates
python build_pdf.py path/to/problems.md --title "比赛标题" --date "2026年6月" --author "命题人"
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `md` | 源 Markdown 文件路径（必填） | — |
| `--title` | 封面比赛标题 | `CQUE-ACMers 集训队月赛` |
| `--date` | 比赛日期 | `2026年6月` |
| `--author` | 命题人 | `CQUE-ACMers 命题组` |
| `--output` / `-o` | 输出目录（默认源文件所在目录） | 源文件目录 |
| `--keep-tex` | 保留中间生成的 .tex 文件 | 不保留 |

**示例：**

```bash
python build_pdf.py "../【26春6月】CQUE-ACM校赛.md" \
    --title "CQUE重庆市赛练习赛" \
    --date "2026年6月" \
    --author "CQUE-ACMers 郑建秋" \
    --keep-tex
```

### 3) 自定义封面标题

直接编辑 `template.tex`，在 `\maketitlepage` 处修改参数，或通过 `build_pdf.py` 命令行传入。

## Markdown 编写规范

为了让 `build_pdf.py` 正确处理，Markdown 源文件应遵循以下约定：

- **一级标题** `#` → LaTeX `\section`，用于比赛说明等大章节
- **二级标题** `##` → LaTeX `\subsection`，每道题使用一个二级标题
- **样例输入/输出** 使用代码块（` ``` ` 包裹），会自动转换为带边框的 lstlisting
- **加粗关键词** `**输入格式**`、`**输出格式**`、`**样例输入**`、`**样例输出**` 会自动格式化为金色标签
- **水平分隔线** `---` 会被替换为题目间分隔线

## AI 助手集成（SKILL）

本仓库包含 `SKILL.md`，为 [Qoder](https://qoder.com) AI 编码助手提供该模板的完整使用指南，让 AI 能够直接理解项目结构并执行构建。

### 安装方式

1. 在 Qoder 中打开本项目工作目录
2. 将 `SKILL.md` 放置在 Qoder 的技能加载路径中（例如 `.qoder/skills/` 目录），或在 Qoder 配置中注册该 skill
3. 完成后，AI 助手即可在对话中通过 `/CQUE-ACMers-Templates` 或 `@CQUE-ACMers-Templates` 调用该 skill

### AI 助手能做什么

启用 SKILL 后，AI 助手将能够自动执行：

- 从 Markdown 源文件一键构建带 VIS 封面的 PDF
- 调整封面标题、日期、命题人
- 配置水印透明度、样式自定义
- 排查编译错误（依赖缺失、字体问题等）

## 许可证

本项目仅限 CQUE-ACMers 集训队内部使用。VIS 素材版权归重庆第二师范学院所有。
