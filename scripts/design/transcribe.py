"""ID 設計書（docs/design/）の各行を、振り分け先の文書へ転記する。

    python3 scripts/design/transcribe.py            # 転記する
    python3 scripts/design/transcribe.py --check    # 転記結果が設計書と食い違っていないかだけ確かめる（Lint 用）
    オプション: --design <設計書のフォルダ> --out <転記先のリポジトリのルート>

振り分け先は、見出しの設計項目の3属性（性質・機械検査・業務承認）と、書類の区分（共通か機能別か）で決まる
（ルールは _tazuna/id-design の Excel「振り分けルール」と同じ）。行の末尾に {性質:振る舞い 機械検査:実行で可} の
ように書くと、その行だけ属性を上書きできる。

転記先（書類実体ごとに1ブロック。ブロックは目印で囲み、作り直すたびに丸ごと置き換える。手で書いた部分には触らない）:
  機能別・テスト・業務承認=要   → docs/requirements/<書類実体>.md の「## REQ-ddnnn」（完了条件）
  共通・テスト・業務承認=要     → docs/domain/candidates/design-<書類実体>.md（不変条件の候補。社員が承認して invariants へ）
  AIへの条件（主・副とも）      → 機能別: docs/requirements/<書類実体>.md の「実装するときの条件」 / 共通: docs/conventions.md
  知識                          → docs/domain/background.md
  設計・Lint・実行検証・hooks・テスト（業務承認=不要）・人のための設計
                                → docs/tasks/<書類実体>.md（作業一覧。実装の issue から参照する）
  機械で守る項目で業務承認=要の根拠 → 機能別: 要件ファイルの「型・Lint で守る決まり」 / 共通: 候補ファイル
"""
import argparse
import csv
import os
import re
import sys

ROOT = os.environ.get("TAZUNA_ROOT") or os.getcwd()
FILE_RE = re.compile(r"^(S-(\d{2}))-(\d{3})_(.+)\.md$")
HEAD_RE = re.compile(r"^## (D-\d{5}) ")
LINE_RE = re.compile(r"^- (S-\d{2}-\d{3}-\d{3}) (.*)$")
OVER_RE = re.compile(r"\s*\{([^{}]*)\}\s*$")
TARGET_RE = re.compile(r"^> 対象: (S-22-\d{3}(?:[、,] *S-22-\d{3})*)\s*$")
KEYS = {"性質": "nature", "機械検査": "check", "業務承認": "appr"}


def load(name):
    with open(os.path.join(ROOT, "harness", "id-design", name), encoding="utf-8") as fp:
        return list(csv.DictReader(fp, delimiter="\t"))


def destination(n, c, a):
    """振り分けルール（Excel の数式と同じ）。(主, 副)"""
    if n == "行為・操作":
        return "hooks", "AIへの条件"
    if n == "背景知識":
        return "知識", ""
    if c == "静的に可":
        return ("Lint" if n == "構造・依存" else "設計"), ("根拠" if a == "要" else "")
    if c == "実行で可":
        return ("実行検証" if n == "方針・判断" else "テスト"), ("根拠" if a == "要" else "")
    return ("人のための設計", "AIへの条件") if a == "要" else ("AIへの条件", "")


def read_design(folder, items, docs):
    """[(書類実体, 書類ID, 名前, 区分, 対象の処理設計書, [(行ID, 本文, 項番, 属性)])]"""
    out = []
    for name in sorted(os.listdir(folder)):
        m = FILE_RE.match(name)
        if not m:
            continue
        doc, inst, title = m.group(1), f"{m.group(1)}-{m.group(3)}", m.group(4)
        lines, head, target = [], None, None
        with open(os.path.join(folder, name), encoding="utf-8") as fp:
            for raw in fp:
                raw = raw.rstrip("\n")
                t = TARGET_RE.match(raw)
                if t and head is None:
                    target = re.split(r"[、,] *", t.group(1))[0]
                    continue
                h = HEAD_RE.match(raw)
                if h:
                    head = h.group(1)
                    continue
                l = LINE_RE.match(raw)
                if not l or head not in items:
                    continue
                text = l.group(2)
                if text.startswith("（廃止）"):
                    continue
                x = {k: items[head][k] for k in ("性質", "機械検査", "業務承認")}
                o = OVER_RE.search(text)
                if o:
                    for part in o.group(1).split():
                        k, _, v = part.partition(":")
                        if k in KEYS:
                            x[k] = v
                    text = text[:o.start()]
                lines.append((l.group(1), text, head, x))
        out.append((inst, doc, title, docs[doc]["区分"] if doc in docs else "", target, lines))
    return out


def block(inst, body):
    return [f"<!-- tazuna:design {inst} begin（scripts/design/transcribe.py が作る。手で直さない） -->", *body,
            f"<!-- tazuna:design {inst} end -->"]


def build(folder):
    items = {r["項番"]: r for r in load("items.tsv")}
    docs = {r["書類ID"]: r for r in load("documents.tsv")}
    files = {}  # 相対パス -> {書類実体: [行]}
    headers = {}

    def put(path, inst, lines, header=None):
        files.setdefault(path, {}).setdefault(inst, []).extend(lines)
        if header and path not in headers:
            headers[path] = header

    design = read_design(folder, items, docs)
    stems = {d[0]: f"{d[0]}_{d[2]}" for d in design}
    for inst, doc, title, kind, target, lines in design:
        common = kind != "機能別設計"
        label = f"{inst} {docs[doc]['書類名'] if doc in docs else doc}：{title}"
        req, cond, basis, cand, know, tasks = [], [], [], [], [], {}
        for lid, text, iid, x in lines:
            main, sub = destination(x["性質"], x["機械検査"], x["業務承認"])
            entry = f"- {text}（{lid}・{items[iid]['設計項目']}）"
            if main == "テスト" and x["業務承認"] == "要":
                (cand if common else req).append(entry)
            elif main == "AIへの条件":
                cond.append(entry)
            elif main == "知識":
                know.append(entry)
            if main not in ("AIへの条件", "知識") and not (main == "テスト" and x["業務承認"] == "要"):
                tasks.setdefault(main, []).append(f"- [ ] {text}（{lid}・{items[iid]['設計項目']}）")
            if sub == "AIへの条件":
                cond.append(entry)
            if sub == "根拠" and main != "テスト":
                (cand if common else basis).append(entry)

        stem = f"{inst}_{title}"
        # 対象の処理設計書がある書類（テスト仕様書・画面・ジョブ・IF・帳票）は、要件と作業一覧を対象のファイルにまとめる
        home = stems.get(target, stem) if target else stem
        home_title = home.split("_", 1)[1]
        if not common and (req or cond or basis):
            body = [f"## REQ-{doc[2:]}{inst[-3:]} {title}（{docs[doc]['書類名'] if doc in docs else doc}）" if home != stem
                    else f"## REQ-{doc[2:]}{inst[-3:]} {title}", "",
                    f"- 背景: ID 設計 {label} で決めた完了条件。",
                    "- 完了条件:"] + [f"  {e}" for e in req]
            if cond:
                body += ["", f"### 実装するときの条件（{inst}）", ""] + cond
            if basis:
                body += ["", f"### 型・Lint で守る決まり（{inst}・業務の承認済み）", ""] + basis
            put(f"docs/requirements/{home}.md", inst, body,
                [f"# {home_title}", "", f"> ID 設計 {home.split('_')[0]} とその対象の書類から転記した要件。設計書を直して転記し直す。目印の中は手で直さない。", ""])
        if common and cond:
            put("docs/conventions.md", inst, [f"## 設計から転記した決まり（{label}）", ""] + cond)
        if common and cand:
            put(f"docs/domain/candidates/design-{stem}.md", inst,
                [f"## {label}", "", "社員が各行の判定（承認・却下・保留）を決め、承認したものを invariants.md に「防ぐ層」「担保」付きで移す。", ""]
                + [f"{e}　判定: 未" for e in cand],
                [f"# 不変条件の候補：{title}", "", "> ID 設計から転記した、システム共通の業務ルールの候補。正本ではない。", ""])
        if know:
            put("docs/domain/background.md", inst, [f"## {label}", ""] + know,
                ["# 背景知識", "", "> ID 設計から転記した、判断の材料になる事実。守らせるルールではない。", ""])
        if tasks:
            order = ["設計", "Lint", "テスト", "実行検証", "hooks", "人のための設計"]
            names = {"設計": "型・API・DB 制約で書けなくする", "Lint": "Lint を足す", "テスト": "テストを書く（業務承認の要らない振る舞い）",
                     "実行検証": "動かして測り、PR に結果を添える", "hooks": "hooks で操作を止める", "人のための設計": "承認されているか確かめる"}
            body = []
            for k in order:
                if k in tasks:
                    body += [f"## {names[k]}", ""] + tasks[k] + [""]
            if home != stem:
                body = [f"## {label}", ""] + [("#" + b if b.startswith("## ") else b) for b in body]
            put(f"docs/tasks/{home}.md", inst, body[:-1],
                [f"# 作業一覧：{home_title}", "", f"> ID 設計 {home.split('_')[0]} とその対象の書類から転記した作業。実装の issue から参照する。", ""])
    return files, headers


def render(current, header, blocks):
    """既存のファイルに、書類実体ごとのブロックを入れる（同じ書類実体のブロックは置き換え、なければ末尾に足す）"""
    text = current if current is not None else "\n".join(header) + "\n"
    for inst, body in blocks.items():
        new = "\n".join(block(inst, body))
        pat = re.compile(rf"<!-- tazuna:design {re.escape(inst)} begin.*?<!-- tazuna:design {re.escape(inst)} end -->", re.S)
        if pat.search(text):
            text = pat.sub(lambda _: new, text)
        else:
            text = text.rstrip("\n") + "\n\n" + new + "\n"
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", default=os.path.join(ROOT, "docs", "design"))
    ap.add_argument("--out", default=ROOT)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not os.path.isdir(a.design):
        return 0
    files, headers = build(a.design)
    stale = []
    for rel, blocks in sorted(files.items()):
        path = os.path.join(a.out, rel)
        current = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        text = render(current, headers.get(rel, [f"# {rel}", ""]), blocks)
        if text != current:
            if a.check:
                stale.append(rel)
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as fp:
                    fp.write(text)
                print("転記:", rel)
    if a.check and stale:
        for rel in stale:
            print(f"ERROR [COMMON-008] {rel}\n  内容: ID 設計書と転記結果が食い違っています\n"
                  "  理由: 設計書を直したのに転記し直していないか、転記した部分を手で直しています\n"
                  "  修正: python3 scripts/design/transcribe.py を実行し、差分を確かめてコミットしてください。直したい内容は設計書の方を直してください\n"
                  "  参照: scripts/design/transcribe.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
