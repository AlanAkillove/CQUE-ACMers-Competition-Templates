#!/usr/bin/env python3
"""CQUE-ACMers 赛题 MD -> PDF 构建脚本"""
import argparse, os, subprocess, sys, tempfile, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(BASE, "template.tex")
ASSETS = os.path.join(BASE, "assets")
B = chr(92)
N = chr(10)

BD = B + "begin{document}"
ED = B + "end{document}"
SEP_OLD = B + "begin{center}" + B + "rule{0.5" + B + "linewidth}{0.5pt}" + B + "end{center}"
SEP_NEW = B + "problemsetsep"
ST = B + "sampletitle"
BF = B + "textbf"

def find_pandoc():
    r = subprocess.run(["where", "pandoc"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode == 0:
        return r.stdout.strip().split(N)[0]
    w = os.path.expandvars("%LOCALAPPDATA%" + B + "Microsoft" + B + "WinGet" + B + "Packages")
    if os.path.isdir(w):
        for root, dirs, files in os.walk(w):
            for f in files:
                if f == "pandoc.exe":
                    return os.path.join(root, f)
    print("pandoc not found", file=sys.stderr)
    sys.exit(1)

def md2tex(md, tex):
    pandoc = find_pandoc()
    subprocess.run([pandoc, md, "-o", tex, "--standalone",
        "--from", "markdown+pipe_tables+grid_tables", "--to", "latex", "--wrap=preserve"], check=True)

def extract_body(content):
    s = content.find(BD)
    e = content.find(ED)
    if s == -1 or e == -1:
        sys.exit(1)
    return content[s + len(BD):e]

def transform(body):
    body = body.replace(SEP_OLD, SEP_NEW)
    body = body.replace(BF + "{样例输入}", ST + "{样例输入}")
    body = body.replace(BF + "{样例输出}", ST + "{样例输出}")
    body = body.replace(BF + "{输入格式}", ST + "{输入格式}")
    body = body.replace(BF + "{输出格式}", ST + "{输出格式}")
    body = body.replace(B + "passthrough{" + B + "lstinline!", B + "texttt{")
    body = body.replace("!}", "}")
    # verbatim -> lstlisting (with frame for sample I/O)
    body = body.replace(B + "begin{verbatim}", B + "begin{lstlisting}[frame=single, basicstyle=" + B + "small" + B + "ttfamily, backgroundcolor=" + B + "color{codebg}]")
    body = body.replace(B + "end{verbatim}", B + "end{lstlisting}")
    # newpage before each subsection (except the first)
    sub = B + "subsection{"
    parts = body.split(sub)
    if len(parts) > 1:
        body = parts[0] + sub + parts[1]
        for p in parts[2:]:
            body += B + "newpage" + N + sub + p
    return body

def build_tex(body, title, date, author, out):
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        tpl = f.read()
    idx = tpl.find(BD)
    if idx == -1:
        sys.exit(1)
    preamble = tpl[:idx + len(BD)]
    preamble = preamble.replace("assets/", ASSETS.replace(B, "/") + "/")
    cover = B + "maketitlepage{" + title + "}{" + date + "}{" + author + "}"
    with open(out, "w", encoding="utf-8") as f:
        f.write(preamble + N + cover + N + body + N + ED + N)

def compile_pdf(tex, out_dir=None):
    d = os.path.dirname(os.path.abspath(tex))
    n = os.path.basename(tex)
    for i in range(2):
        subprocess.run(["xelatex", "-interaction=nonstopmode", "-shell-escape", n],
            cwd=d, capture_output=True, text=True, encoding="utf-8", errors="replace")
    pdf = tex.replace(".tex", ".pdf")
    if not os.path.exists(pdf):
        print("ERROR: PDF not generated", file=sys.stderr)
        sys.exit(1)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        dest = os.path.join(out_dir, os.path.basename(pdf))
        if os.path.exists(dest):
            os.remove(dest)
        shutil.move(pdf, dest)
        pdf = dest
    return pdf

def main():
    p = argparse.ArgumentParser(description="CQUE-ACMers MD->PDF")
    p.add_argument("md")
    p.add_argument("--title", default="CQUE-ACMers 集训队月赛")
    p.add_argument("--date", default="2026年6月")
    p.add_argument("--author", default="CQUE-ACMers 命题组")
    p.add_argument("--output", "-o", default=None)
    p.add_argument("--keep-tex", action="store_true")
    a = p.parse_args()
    md = os.path.abspath(a.md)
    if not os.path.exists(md):
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
        print("Done:", pdf)

if __name__ == "__main__":
    main()
