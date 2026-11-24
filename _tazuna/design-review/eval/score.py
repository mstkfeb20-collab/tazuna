"""設計書レビュー（base-design-review）の結果を採点する。

    python3 score.py <結果の TSV> [...]

結果の TSV は「種別<TAB>根拠の行ID（カンマ区切り）<TAB>指摘」。質問は採点しない（件数だけ出す）。
指摘が欠陥に当たる: 根拠の行IDが欠陥の行IDと1つでも重なる。種別も合えば「種別一致」。
誤指摘: どの欠陥にも当たらない指摘。そのうち、おとり（問題のない行）だけを根拠にしたものを別に数える。
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LID = re.compile(r"S-\d{2}-\d{3}/D-\d{5}/\d+")


def load(path):
    with open(path, encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


defects = [(r["欠陥ID"], set(r["種別"].split("|")), set(r["根拠の行ID"].split(";")), r["内容"]) for r in load(os.path.join(HERE, "expected.csv"))]
decoys = {r["行ID"] for r in load(os.path.join(HERE, "decoys.csv"))}
stars = {r["共通の見出し"]: (r["判断"], r["理由"]) for r in load(os.path.join(HERE, "stars.csv"))}
HEAD = re.compile(r"S-\d{2}-\d{3}/D-\d{5}")
judged = {}

findings, questions = [], 0
for path in sys.argv[1:]:
    with open(path, encoding="utf-8") as fp:
        for line in fp:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 2 or cols[0] in ("種別", "") or not (LID.search(cols[1]) or (cols[0] == "★" and HEAD.search(cols[1]))):
                continue
            if cols[0] == "★":
                for h in HEAD.findall(cols[1]):
                    m = re.match(r"\s*([123])", cols[2] if len(cols) > 2 else "")
                    judged[h] = m.group(1) if m else "?"
                continue
            if cols[0] == "質問":
                questions += 1
                continue
            findings.append((cols[0], set(LID.findall(cols[1])), cols[2] if len(cols) > 2 else ""))

hit, kind_ok, wrong, bait = {}, set(), [], []
for kind, ids, text in findings:
    m = [d for d in defects if ids & d[2]]
    if not m:
        (bait if ids <= decoys else wrong).append((kind, ids, text))
        continue
    for d in m:
        hit.setdefault(d[0], []).append(kind)
        if kind in d[1]:
            kind_ok.add(d[0])

print(f"欠陥 {len(defects)} 件のうち、当たった {len(hit)} 件（種別も一致 {len(kind_ok)} 件）")
print(f"指摘 {len(findings)} 件のうち、誤指摘 {len(wrong) + len(bait)} 件（おとりに当たった {len(bait)} 件）・質問 {questions} 件")
for d in defects:
    mark = "○" if d[0] in kind_ok else ("△" if d[0] in hit else "×")
    print(f"  {mark} {d[0]} {'/'.join(sorted(d[1]))}: {d[3]}" + (f"（出た種別: {', '.join(hit[d[0]])}）" if d[0] in hit and d[0] not in kind_ok else ""))
for kind, ids, text in bait + wrong:
    print(f"  誤 {kind} {','.join(sorted(ids))} {text[:60]}")
ok = sum(1 for h, (j, _) in stars.items() if judged.get(h) == j)
print(f"★ {len(stars)} 件のうち、判断が答えと同じ {ok} 件・判断なし {sum(1 for h in stars if h not in judged)} 件")
for h, (j, why) in stars.items():
    print(f"  {'○' if judged.get(h) == j else '×'} {h} 答え {j}（{why[:30]}…）・出た判断 {judged.get(h, 'なし')}")
