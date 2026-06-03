---
name: cque-acmers-templates
description: CQUE-ACMers ACM赛题LaTeX模板 — 从Markdown构建排版精美的比赛PDF，包含学校VIS规范的封面、水印、页脚等视觉元素
---

# CQUE-ACMers 赛题模板 — Agent 使用指南

## 项目概述

为重庆第二师范学院 CQUE-ACMers 集训队定制的 ACM 赛题 LaTeX 模板，支持从 Markdown 一键构建为排版精美的比赛 PDF。包含学校 VIS 规范的封面、水印、页脚等视觉元素。

## 核心文件

| 文件 | 作用 |
|------|------|
| `template.tex` | LaTeX 主模板，含 `\maketitlepage` 封面命令、水印、全部样式定义 |
| `build_pdf.py` | Python 构建脚本：pandoc 转 LaTeX → 提取正文 → 合并模板 → xelatex 编译 |
| `assets/` | VIS 图像素材（校徽、校训、学风、水印等） |

## 构建命令

### 从 Markdown 构建 PDF

```bash
python build_pdf.py path/to/source.md --title "标题" --date "日期" --author "命题人" --keep-tex
```

示例：
```bash
python build_pdf.py "../【26春6月】CQUE-ACM校赛.md" --title "CQUE重庆市赛练习赛" --date "2026年6月" --author "CQUE-ACMers 郑建秋" --keep-tex
```

### 参数说明

- `md` — 源文件路径（必填）
- `--title` — 封面标题（默认：CQUE-ACMers 集训队月赛）
- `--date` — 比赛日期（默认：2026年6月）
- `--author` — 命题人（默认：CQUE-ACMers 命题组）
- `--output / -o` — 输出目录（默认：源文件所在目录）
- `--keep-tex` — 保留中间 .tex 文件

### 直接编译模板

```bash
xelatex -interaction=nonstopmode -shell-escape template.tex
# 两遍编译
```

## 模板自定义要点

### 覆盖命令参数

封面使用 `\maketitlepage{标题}{日期}{命题人}`，模板中已内置示例调用。通过 `build_pdf.py` 构建时自动传入。

### 水印配置

在 `template.tex` 中使用 `atbegshi` 宏包实现，仅在真实 shipout 时渲染：

```latex
\AtBeginShipout{%
  \ifnum\value{page}>1    % 跳过封面和目录页
    \AtBeginShipoutUpperLeft{%
      \begin{tikzpicture}[remember picture, overlay]
        \node[opacity=0.07, inner sep=0pt] at (current page.center) {%
          \includegraphics[width=12cm]{assets/主标识简化图案.png}%
        };
      \end{tikzpicture}%
    }%
  \fi
}
```

**调整透明度**：修改 `opacity` 值（0=完全透明，1=完全不透明）。

### 封面边框

双层矩形边框：
- 外层：深蓝 `#0F2440`，线宽 3.5pt
- 内层：金色 `#D4A843`，线宽 1.0pt

### 颜色系统

| 变量 | 色值 | 用途 |
|------|------|------|
| `navy` | `#1A365D` | 主色：标题文字 |
| `steel` | `#2C608A` | 辅色：说明文字 |
| `gold` | `#9B6B1E` | 点缀：样例标签 |
| `coverbg` | `#0F2440` | 封面边框 |
| `coveraccent` | `#D4A843` | 封面金边 |
| `codebg` | `#F2F3F5` | 代码背景 |
| `coderule` | `#CFD4DB` | 代码边框 |

### 字体配置

- 中文正文：SimSun（宋体）
- 中文标题：SimHei（黑体）
- 中文等宽：KaiTi（楷体）
- 英文正文：Times New Roman
- 英文代码：Consolas

## build_pdf.py 自动转换逻辑

构建脚本在 `transform()` 函数中执行以下自动转换：

| 原内容 | 转换后 |
|--------|--------|
| `\textbf{样例输入}` | `\sampletitle{样例输入}` |
| `\textbf{样例输出}` | `\sampletitle{样例输出}` |
| `\textbf{输入格式}` | `\sampletitle{输入格式}` |
| `\textbf{输出格式}` | `\sampletitle{输出格式}` |
| `\begin{verbatim}...\end{verbatim}` | `\begin{lstlisting}[frame=single,...]\end{lstlisting}` |
| `---` 分隔线 | `\problemsetsep` |
| 每个 `\subsection`（除首个） | 前插 `\newpage` |

## 常见问题

### Q: 水印在不同页面深浅不一致？
确保使用 `atbegshi` 宏包（非 `eso-pic` 或 `\AddToHook`），`atbegshi` 会过滤掉 `longtable` 等环境的试排 shipout，保证每页水印仅渲染一次。

### Q: 编译出错？
确认已安装所有依赖宏包，以及 SimSun/SimHei/KaiTi 等中文字体。

### Q: 封面不显示校名图片？
确认 `assets/` 目录下的 PNG 文件存在且未损坏。路径使用相对路径 `assets/xxx.png`。
