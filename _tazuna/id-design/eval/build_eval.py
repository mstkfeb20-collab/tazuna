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
from source import FILES, L  # noqa: E402

items = {x["item"]: x for x in build.I}
errors = []

for f, item, text, over in L:
    for k, v in over.items():
        if k in items.get(item, {}) and items[item][k] == v:
            errors.append(f"既定と同じ上書き（{k}={v}）: {text}")
    if f not in FILES:
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

# ---- 行IDを振る（ファイルごとの連番）
by_file = defaultdict(list)
for f, item, text, over in L:
    by_file[f].append((item, text, over))

order = list(FILES)
rows = []
os.makedirs(os.path.join(HERE, "design"), exist_ok=True)
for f in order:
    prefix = "D-CM" if f == "common" else "D-" + f.replace("F-", "").replace("-", "")
    lines = by_file[f]
    # インプットは観点ごとにまとめる（ID 設計書の章立てに合わせる）。観点の順は振り分け表の順
    view_order = list(dict.fromkeys(x["view"] for x in build.I))
    lines.sort(key=lambda t: view_order.index(items[t[0]]["view"]))
    md = [f"# {'' if f == 'common' else f + ' '}{FILES[f]}", ""]
    md.append("> 振り分け評価のインプット。1行に1つの決定事項を書く。設計項目や振り分け先は書かない。")
    current = None
    for n, (item, text, over) in enumerate(lines, 1):
        x = dict(items[item])
        x.update(over)
        diff = "・".join(f"{k}: {items[item][k]}→{v}" for k, v in over.items() if items[item][k] != v)
        diff = diff.replace("nature", "性質").replace("check", "機械検査").replace("scope", "適用範囲").replace("appr", "業務承認")
        if diff:
            diff = "項目の既定と違う（" + diff + "）"
        view = items[item]["view"]
        if view != current:
            md += ["", f"## {view}", ""]
            current = view
        lid = f"{prefix}-{n:03d}"
        md.append(f"- {lid} {text}")
        main, sub, place, owner = build.map_item(x)
        rows.append([lid, f, view, item, text, x["nature"], x["check"], x["scope"], x["appr"],
                     main, sub, place, owner, diff])
    with open(os.path.join(HERE, "design", f"{f}.md"), "w", encoding="utf-8") as fp:
        fp.write("\n".join(md) + "\n")

hdr = ["行ID", "ファイル", "観点", "設計項目", "本文", "性質", "機械検査", "適用範囲", "業務承認",
       "振り分け先（主）", "振り分け先（副）", "tazuna の置き場所", "持ち主", "備考"]
with open(os.path.join(HERE, "expected.csv"), "w", encoding="utf-8-sig", newline="") as fp:
    w = csv.writer(fp)
    w.writerow(hdr)
    w.writerows(rows)

print(f"{len(rows)} 行 / {len(FILES)} ファイル / 設計項目 {len(used)}/{len(items)}")
print("振り分け先（主）:", dict(Counter(r[9] for r in rows)))
print("ファイル別:", dict(Counter(r[1] for r in rows)))
