#!/usr/bin/env python3
"""CQUE-ACMers 赛题 MD -> PDF 构建脚本"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(BASE, "template.tex")
ASSETS = os.path.join(BASE, "assets")
BS = "\\"  # backslash
NL = "\n"

# pandoc inline code pattern: \passthrough{\lstinline!code!}
_PASSTHROUGH_RE = re.compile(r"\\passthrough\{\\lstinline!(.*?)!\}")


def find_pandoc() -> str:
    """查找 pandoc 可执行文件路径"""
    pandoc = shutil.which("pandoc")
    if pandoc:
        return pandoc
    # WinGet Packages fallback
    localappdata = os.environ.get("LOCALAPPDATA", "")
    if localappdata:
        p = os.path.join(
            localappdata,
            "Microsoft",
            "WinGet",
            "Packages",
            "Winget.Pandoc",
            "pandoc.exe",
        )
        if os.path.isfile(p):
            return p
    print("错误: 未找到 pandoc，请先安装: https://pandoc.org/", file=sys.stderr)
    sys.exit(1)


def escape_latex(text: str) -> str:
    """转义 LaTeX 特殊字符，防止编译错误或注入"""
    char_map = {
        "\\": "\\textbackslash{}",
        "{": "\\{",
        "}": "\\}",
        "%": "\\%",
        "&": "\\&",
        "#": "\\#",
        "^": "\\textasciicircum{}",
        "_": "\\_",
        "~": "\\textasciitilde{}",
    }
    for char, escaped in char_map.items():
        text = text.replace(char, escaped)
    return text


def md2tex(md: str, tex: str) -> None:
    """调用 pandoc 将 Markdown 转换为 LaTeX"""
    pandoc = find_pandoc()
    subprocess.run(
        [
            pandoc,
            md,
            "-o",
            tex,
            "--standalone",
            "--from",
            "markdown+pipe_tables+grid_tables",
            "--to",
            "latex",
            "--wrap=preserve",
        ],
        check=True,
    )


def extract_body(content: str) -> str:
    """从 pandoc 输出的完整 LaTeX 中提取 body 部分"""
    bd = BS + "begin{document}"
    ed = BS + "end{document}"
    s = content.find(bd)
    e = content.find(ed)
    if s == -1 or e == -1:
        print(
            "错误: 无法在 pandoc 输出中找到 \\begin{document} 或 \\end{document}",
            file=sys.stderr,
        )
        sys.exit(1)
    return content[s + len(bd) : e]


def transform(body: str) -> str:
    """对提取的 body 进行模板适配转换"""
    # pandoc inline code: \passthrough{\lstinline!code!} -> \texttt{code}
    body = _PASSTHROUGH_RE.sub(r"\\texttt{\1}", body)

    # \textbf{...} -> \sampletitle{...} for known labels
    for label in ["样例输入", "样例输出", "输入格式", "输出格式"]:
        body = body.replace(f"{BS}textbf{{{label}}}", f"{BS}sampletitle{{{label}}}")

    # center-rule separator -> \problemsetsep
    sep_old = (
        f"{BS}begin{{{BS}center}}{BS}rule{{0.5{BS}linewidth}}{{0.5pt}}{BS}end{{{BS}center}}"
    )
    body = body.replace(sep_old, f"{BS}problemsetsep")

    # verbatim -> lstlisting with frame
    body = body.replace(
        f"{BS}begin{{verbatim}}",
        f"{BS}begin{{lstlisting}}[frame=single, basicstyle={BS}small{BS}ttfamily, backgroundcolor={BS}color{{codebg}}]",
    )
    body = body.replace(f"{BS}end{{verbatim}}", f"{BS}end{{lstlisting}}")

    # \newpage before each \subsection (except the first)
    sub = f"{BS}subsection{{"
    parts = body.split(sub)
    if len(parts) > 1:
        body = parts[0] + sub + parts[1]
        for p in parts[2:]:
            body += f"{BS}newpage{NL}" + sub + p
    return body


def build_tex(body: str, title: str, date: str, author: str, out: str) -> None:
    """将 body 嵌入模板生成完整的 .tex 文件"""
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        tpl = f.read()
    bd = BS + "begin{document}"
    idx = tpl.find(bd)
    if idx == -1:
        print("错误: 模板中未找到 \\begin{document}", file=sys.stderr)
        sys.exit(1)
    preamble = tpl[: idx + len(bd)]
    cover = (
        f"{BS}maketitlepage{{{escape_latex(title)}}}"
        f"{{{escape_latex(date)}}}"
        f"{{{escape_latex(author)}}}"
    )
    with open(out, "w", encoding="utf-8") as f:
        f.write(preamble + NL + cover + NL + body + NL + f"{BS}end{{document}}" + NL)


def _print_xelatex_errors(log: str) -> None:
    """从 xelatex 日志中提取并打印关键错误行"""
    seen = set()
    for line in log.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if any(kw in stripped for kw in ("Error", "Fatal", "! ")):
            if stripped not in seen:
                print(f"  {stripped}", file=sys.stderr)
                seen.add(stripped)


def compile_pdf(tex: str, out_dir: str | None = None) -> str:
    """编译 .tex -> PDF"""
    tex_dir = os.path.dirname(os.path.abspath(tex))
    tex_name = os.path.basename(tex)

    # assets 复制到编译目录，确保相对路径引用有效
    assets_link = os.path.join(tex_dir, "assets")
    if not os.path.exists(assets_link):
        shutil.copytree(ASSETS, assets_link)

    ok = True
    for i in range(2):
        r = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-shell-escape", tex_name],
            cwd=tex_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if r.returncode != 0:
            ok = False
            if i == 0:
                print("警告: 第一次编译出错，尝试第二次编译...", file=sys.stderr)

    if not ok:
        # 尝试从 .log 文件中提取错误信息
        log_file = tex.replace(".tex", ".log")
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                _print_xelatex_errors(f.read())
        else:
            print("错误: xelatex 编译失败，无日志文件", file=sys.stderr)

    pdf = tex.replace(".tex", ".pdf")
    if not os.path.exists(pdf):
        print("错误: PDF 未生成，请检查上方 LaTeX 错误信息", file=sys.stderr)
        sys.exit(1)

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        dest = os.path.join(out_dir, os.path.basename(pdf))
        shutil.move(pdf, dest)
        return dest
    return pdf


def main() -> None:
    p = argparse.ArgumentParser(description="CQUE-ACMers MD->PDF 构建工具")
    p.add_argument("md", help="源 Markdown 文件路径")
    p.add_argument("--title", default="CQUE-ACMers 集训队月赛", help="封面比赛标题")
    p.add_argument("--date", default="2026年6月", help="比赛日期")
    p.add_argument("--author", default="CQUE-ACMers 命题组", help="命题人")
    p.add_argument("--output", "-o", default=None, help="输出目录")
    p.add_argument("--keep-tex", action="store_true", help="保留中间 .tex 文件")
    a = p.parse_args()

    md = os.path.abspath(a.md)
    if not os.path.exists(md):
        print(f"错误: 文件不存在: {md}", file=sys.stderr)
        sys.exit(1)

    out_dir = a.output or os.path.dirname(md)

    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "raw.tex")
        final = os.path.join(td, "final.tex")

        md2tex(md, raw)
        with open(raw, "r", encoding="utf-8") as f:
            body = extract_body(f.read())
        body = transform(body)
        build_tex(body, a.title, a.date, a.author, final)

        if a.keep_tex:
            bn = os.path.splitext(os.path.basename(md))[0]
            shutil.copy(final, os.path.join(out_dir, bn + ".tex"))

        pdf = compile_pdf(final, out_dir)
        print("完成:", pdf)


if __name__ == "__main__":
    main()
