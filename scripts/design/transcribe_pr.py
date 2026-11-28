"""転記の PR（MR）の本文を作る。設計書の変更がマージされたとき、CI が transcribe.py の後に使う。

    python3 scripts/design/transcribe_pr.py --base main --range <前のコミット>..<今のコミット> [--no-ci-note]

転記した結果（作業ツリーの変更）と、もとになった設計書の変更（コミットの題）から、PR テンプレートに沿った本文を出す。
転記の PR も人が確かめてマージする（機能の横断面として、要件・テスト仕様に過不足がないか）。
自動で動かなかったときは、手元で python3 scripts/design/transcribe.py を実行して PR を出せばよい（結果は同じ）。
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.environ.get("TAZUNA_ROOT") or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def git(*args):
    r = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def changed():
    """作業ツリーで変わったファイル（転記の結果）"""
    out = []
    for line in git("-c", "core.quotepath=false", "status", "--porcelain", "--untracked-files=all").splitlines():
        path = line[3:].strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        out.append(path)
    return sorted(out)


def sources(rng):
    """もとになった設計書の変更（コミットの題）。範囲が読めなければ、最後のコミット"""
    log = git("log", "--format=%h %s", rng, "--", "docs/design") if rng and not rng.startswith("0000000") else ""
    return [l for l in log.splitlines() if l.strip()] or [l for l in git("log", "-1", "--format=%h %s").splitlines() if l]


def undecided():
    """転記先の要件にある未決の行の数 (全部, うち（案）)"""
    total = props = 0
    req = os.path.join(ROOT, "docs", "requirements")
    for name in sorted(os.listdir(req)) if os.path.isdir(req) else []:
        if name.endswith(".md"):
            for line in open(os.path.join(req, name), encoding="utf-8"):
                if line.startswith("- 未決（案）"):
                    total, props = total + 1, props + 1
                elif line.startswith("- 未決"):
                    total += 1
    return total, props


def body(base, rng, ci_note):
    files = changed()
    total, props = undecided()
    prs = sorted(set(re.findall(r"[#!]\d+", " ".join(sources(rng)))))
    out = ["## 対象の要件", "対象要件: なし", "",
           "## 変更の概要",
           f"{base} に入った設計書の変更を、`python3 scripts/design/transcribe.py` で転記しました（CI が自動で作成。手では直していません）。",
           "", "もとになった設計書の変更:"]
    out += [f"- {s}" for s in sources(rng)]
    out += ["", "変わった転記先:"] + [f"- `{f}`" for f in files]
    out += ["", f"転記先にある未決: {total} 件（うち「（案）」のまま {props} 件）。未決はエージェントが実装しません。"]
    out += ["", "## 確かめてほしいこと",
            "- 機能の横断面として、要件・テスト仕様に過不足がないか（転記の PR は設計工程の最後の検査）",
            "- 設計の誤り・欠落が見つかったら、この PR は直さずに設計書を直す（転記先は手で直さない。COMMON-008）。"
            "設計書の変更がマージされると、この PR が自動で更新される"]
    if total:
        out.append("- 未決のまま実装に進んでよいか（決めるなら、設計書に書くか「該当なし（理由）」と書く。（案）は人が確かめて外す）")
    if prs:
        out += ["", "関連: " + " ".join(prs)]
    if ci_note:
        out += ["", "## 注意",
                "この PR は CI の標準の権限で作ったため、**この PR の CI は動いていません**。"
                "PR を一度閉じて開き直すと動きます（専用のトークン TAZUNA_BOT_TOKEN を登録すると不要になります）。"]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--range", default="")
    ap.add_argument("--no-ci-note", action="store_true", help="この PR の CI が動くとき（専用のトークン・GitLab）")
    a = ap.parse_args()
    sys.stdout.write(body(a.base, a.range, not a.no_ci_note))
    return 0


if __name__ == "__main__":
    sys.exit(main())
