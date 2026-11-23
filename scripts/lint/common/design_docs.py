"""ID 設計書（docs/design/*.md）の置き場所と番号を検査する。design-docs.sh から呼ぶ。

    python3 scripts/lint/common/design_docs.py [設計書のフォルダ] [--base <git ref>]

検査すること（どれも読むだけで判定できる構造の検査。中身が正しい見出しに書かれているかはスキル base-design-check が見る）:
  1. ファイル名が「書類実体ID_名前.md」（例 S-21-002_予約入力.md）で、書類IDがドキュメント体系にある
  2. 見出し「## D-ccsss 設計項目名」の項番と名前がカタログと一致し、その書類の記載項目に入っている
  3. 行「- 行ID 本文」の行IDが「書類実体ID-通し番号3桁」で、ファイル名の書類実体IDと一致し、重複しない
  4. 行がどれかの見出しの下にある
  5. --base を付けたとき: base にあった行IDが消えていない（廃止は消さずに「（廃止）」と書く）
  警告だけ出すこと: 書類の「必須」の記載項目に見出しがない
カタログ: harness/id-design/{items,documents,records}.tsv（_tazuna/id-design/build.py が Excel と同時に作る）
"""
import csv
import os
import re
import subprocess
import sys

ROOT = os.environ.get("TAZUNA_ROOT") or os.getcwd()
CAT = os.path.join(ROOT, "harness", "id-design")
REF = "harness/id-design/（カタログ）・_tazuna/id-design/ドキュメント体系.md"
errors = 0


def error(where, what, why, fix, ref=REF):
    global errors
    errors += 1
    print(f"ERROR [COMMON-007] {where}\n  内容: {what}\n  理由: {why}\n  修正: {fix}\n  参照: {ref}", file=sys.stderr)


def warn(where, what):
    print(f"WARN  [COMMON-007] {where} : {what}", file=sys.stderr)


def load(name):
    with open(os.path.join(CAT, name), encoding="utf-8") as fp:
        return list(csv.DictReader(fp, delimiter="\t"))


FILE_RE = re.compile(r"^(S-\d{2})-(\d{3})_.+\.md$")
HEAD_RE = re.compile(r"^## (D-\d{5}) (.+?)\s*$")
LINE_RE = re.compile(r"^- (\S+) (.*)$")


def parse(text):
    """(見出し行番号, 項番, 名前) と (行番号, 行ID, 本文, 直前の見出しの項番) を返す"""
    heads, lines, current = [], [], None
    for n, raw in enumerate(text.splitlines(), 1):
        if raw.startswith("## "):
            m = HEAD_RE.match(raw)
            heads.append((n, m.group(1) if m else None, m.group(2) if m else raw[3:]))
            current = m.group(1) if m else "?"
        elif raw.startswith("- "):
            m = LINE_RE.match(raw)
            lines.append((n, m.group(1) if m else "", m.group(2) if m else raw[2:], current))
    return heads, lines


def main():
    args = sys.argv[1:]
    base = None
    if "--base" in args:
        i = args.index("--base")
        base = args[i + 1]
        del args[i:i + 2]
    folder = args[0] if args else os.path.join(ROOT, "docs", "design")
    if not os.path.isdir(folder):
        return 0  # ID 設計書を置いていない案件では何もしない
    if not os.path.isdir(CAT):
        error("harness/id-design/", "ID 設計のカタログがありません",
              "書類と設計項目の一覧がないと、置き場所を検査できません",
              "tazuna の型から harness/id-design/ を取り込んでください")
        return 1

    items = {r["項番"]: r for r in load("items.tsv")}
    docs = {r["書類ID"]: r for r in load("documents.tsv")}
    records = {}
    for r in load("records.tsv"):
        records.setdefault(r["書類ID"], {})[r["項番"]] = r

    seen = {}
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name.lower() == "readme.md":
            continue
        path = os.path.join(folder, name)
        rel = os.path.relpath(path, ROOT)
        m = FILE_RE.match(name)
        if not m:
            error(rel, f"ファイル名 '{name}' が「書類実体ID_名前.md」になっていません",
                  "ファイル名の書類実体IDから、どの書類か（共通設計か機能別設計か）と行IDを決めるためです",
                  "S-21-002_予約入力.md のように、書類ID（S-xx）と3桁の番号を付けてください")
            continue
        doc, inst = m.group(1), f"{m.group(1)}-{m.group(2)}"
        if doc not in docs:
            error(rel, f"書類ID {doc} がドキュメント体系にありません",
                  "書類ごとに書いてよい設計項目が決まっているためです",
                  "ドキュメント体系の書類IDを使ってください。新しい書類が要るなら tazuna の documents.py に足す提案をしてください")
            continue
        allowed = records.get(doc, {})
        with open(path, encoding="utf-8") as fp:
            heads, lines = parse(fp.read())

        for n, iid, label in heads:
            where = f"{rel}:{n}"
            if iid is None:
                error(where, f"見出し '## {label}' が「## D-ccsss 設計項目名」になっていません",
                      "見出しの項番から、行の振り分け先を機械的に決めるためです",
                      "カタログ（items.tsv）の項番と設計項目名で見出しを書いてください")
            elif iid not in items:
                error(where, f"項番 {iid} がカタログにありません",
                      "カタログにない項目は振り分け先が決まりません",
                      "items.tsv の項番を使ってください。足りない項目は tazuna に追加を提案してください")
            elif items[iid]["設計項目"] != label:
                error(where, f"項番 {iid} の名前が違います（'{label}'、カタログでは '{items[iid]['設計項目']}'）",
                      "項番と名前がずれると、どちらが正しいか分からなくなります",
                      f"'## {iid} {items[iid]['設計項目']}' に直してください")
            elif iid not in allowed:
                docs_for = sorted(d for d, rs in records.items() if iid in rs)
                error(where, f"{iid} {label} は {doc} {docs[doc]['書類名']} に書く項目ではありません",
                      "書類ごとに書く項目を決めておくと、共通か機能別かと置き場所が書類で決まります",
                      f"この項目は {'・'.join(docs_for)} に書いてください")

        for n, lid, text, under in lines:
            where = f"{rel}:{n}"
            if not re.fullmatch(rf"{re.escape(inst)}-\d{{3}}", lid):
                error(where, f"行ID '{lid}' が「{inst}-通し番号3桁」になっていません",
                      "行IDは書類実体IDとファイル内の通し番号で決め、人の判断を入れないためです",
                      f"{inst}-NNN の形にしてください。番号はファイルの末尾の次の番号です")
                continue
            if lid in seen:
                error(where, f"行ID {lid} が重複しています（{seen[lid]} にもある）",
                      "1つの行IDは1つの決定事項だけを指します",
                      "後から足した方の行に、ファイルの末尾の次の番号を付け直してください")
            seen[lid] = where
            if under is None:
                error(where, f"行 {lid} がどの見出しの下にもありません",
                      "見出しの設計項目が決まらないと、振り分け先が決まりません",
                      "当てはまる設計項目の見出しの下に移してください")

        have = {iid for _, iid, _ in heads}
        for iid, r in allowed.items():
            if r["記載"] == "必須" and iid not in have:
                warn(rel, f"必須の記載項目 {iid} {r['設計項目']} の見出しがありません")

    if base:
        for lid in removed_ids(folder, base, seen):
            error(lid, f"行ID {lid} が {base} から消えています",
                  "行IDはチケットや転記先から参照されます。消すと参照が切れます",
                  "行を消さずに、本文を「（廃止）理由」や「（廃止）→ 移した先の行ID」にしてください")
    return 1 if errors else 0


def removed_ids(folder, base, current):
    rel = os.path.relpath(folder, ROOT)
    try:
        names = subprocess.run(["git", "-C", ROOT, "ls-tree", "-z", "--name-only", f"{base}:{rel}"],
                               capture_output=True, text=True, check=True).stdout.split("\0")
    except subprocess.CalledProcessError:
        return []
    old = set()
    for name in names:
        if not FILE_RE.match(name):
            continue
        text = subprocess.run(["git", "-C", ROOT, "show", f"{base}:{rel}/{name}"],
                              capture_output=True, text=True).stdout
        old |= {lid for _, lid, _, _ in parse(text)[1] if lid}
    return sorted(old - set(current))


if __name__ == "__main__":
    sys.exit(main())
