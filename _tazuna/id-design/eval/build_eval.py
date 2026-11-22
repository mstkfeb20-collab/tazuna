"""source.py から、インプット（design/*.md）と正解（expected.csv）を作る。

    python3 _tazuna/id-design/eval/build_eval.py

あわせて次を確かめ、満たさなければ終了コード1で止まる。
  - source.py の設計項目名が、すべて振り分け表（build.py）にある
  - 振り分け表の198項目が、すべて1行以上インプットに現れる
  - 振り分け表の「例」が、その項目のどれかの行の本文と一致する（Excel とインプットが同じ題材を指す）
"""
import csv
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build  # noqa: E402  振り分け表の項目と map_item
from source import DETAILED, FILES, L  # noqa: E402

items = {x["item"]: x for x in build.I}
errors = []

def feature_of(f):
    return f.split("/")[0]

RAW = list(L)  # 中見出しを含む、書いた順
L = [x for x in RAW if x[1] is not None]

for f, item, text, over in L:
    for k, v in over.items():
        if k in items.get(item, {}) and items[item][k] == v:
            errors.append(f"既定と同じ上書き（{k}={v}）: {text}")
    if f not in FILES and feature_of(f) not in DETAILED:
        errors.append(f"未定義のファイル {f}: {text}")
    if item not in items:
        errors.append(f"振り分け表にない設計項目「{item}」: {text}")
    for k in over:
        if k not in ("nature", "check", "scope", "appr"):
            errors.append(f"上書きできない属性 {k}: {text}")

used = {item for _, item, _, _ in L}
for name in items:
    if name not in used:
        errors.append(f"インプットに現れない設計項目「{name}」")

texts = defaultdict(set)
for _, item, text, _ in L:
    texts[item].add(text)
for name, x in items.items():
    if name in texts and x["ex"] not in texts[name]:
        errors.append(f"振り分け表の例がインプットにない「{name}」: {x['ex']}")

if errors:
    print("\n".join(errors))
    sys.exit(1)

# ---- 行IDを振る
# 観点でまとめるファイル（common と詳細化していない機能）: D-RV01-001 のようにファイル内の連番
# 書類ごとに分けた機能: D-RV02-301 のように 書類番号 + 2桁の連番。中見出しは書いた順に出す
ALL = RAW
order = sorted(dict.fromkeys(x[0] for x in ALL))
view_order = list(dict.fromkeys(x["view"] for x in build.I))
rows = []
design_dir = os.path.join(HERE, "design")
import shutil
shutil.rmtree(design_dir, ignore_errors=True)
for f in order:
    feat = feature_of(f)
    code = "CM" if f == "common" else feat.replace("F-", "").replace("-", "")
    entries = [x for x in ALL if x[0] == f]
    detailed = "/" in f
    md = []
    if detailed:
        num, docname = f.split("/")[1].split("_", 1)
        md.append(f"# {feat} {DETAILED[feat]} — {docname}")
    else:
        md.append(f"# {'' if f == 'common' else f + ' '}{FILES[f]}")
        entries = [x for x in entries if x[1] is not None]
        entries.sort(key=lambda x: view_order.index(items[x[1]]["view"]))
    md += ["", "> 振り分け評価のインプット。1行に1つの決定事項を書く。設計項目や振り分け先は書かない。"]
    current = None
    n = 0
    for _, item, text, over in entries:
        if item is None:
            md += ["", f"## {text}", ""]
            continue
        view = items[item]["view"]
        if not detailed and view != current:
            md += ["", f"## {view}", ""]
            current = view
        if detailed and (len(md) == 0 or md[-1].startswith(">")):
            md.append("")
        n += 1
        lid = f"D-{code}-{num}{n:02d}" if detailed else f"D-{code}-{n:03d}"
        md.append(f"- {lid} {text}")
        x = dict(items[item])
        x.update(over)
        diff = "・".join(f"{k}: {items[item][k]}→{v}" for k, v in over.items() if items[item][k] != v)
        diff = diff.replace("nature", "性質").replace("check", "機械検査").replace("scope", "適用範囲").replace("appr", "業務承認")
        if diff:
            diff = "項目の既定と違う（" + diff + "）"
        main, sub, place, owner = build.map_item(x)
        rows.append([lid, f, view, item, text, x["nature"], x["check"], x["scope"], x["appr"],
                     main, sub, place, owner, diff])
    if detailed and n > 99:
        print(f"{f}: 99行を超えた")
        sys.exit(1)
    path = os.path.join(design_dir, f + ".md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        fp.write("\n".join(md) + "\n")

hdr = ["行ID", "ファイル", "観点", "設計項目", "本文", "性質", "機械検査", "適用範囲", "業務承認",
       "振り分け先（主）", "振り分け先（副）", "tazuna の置き場所", "持ち主", "備考"]
with open(os.path.join(HERE, "expected.csv"), "w", encoding="utf-8-sig", newline="") as fp:
    w = csv.writer(fp)
    w.writerow(hdr)
    w.writerows(rows)

print(f"{len(rows)} 行 / {len(order)} ファイル / 設計項目 {len(used)}/{len(items)}")
print("上書き行:", sum(1 for r in rows if r[13]))
print("振り分け先（主）:", dict(Counter(r[9] for r in rows)))
print("機能別:", dict(Counter(feature_of(r[1]) for r in rows)))
