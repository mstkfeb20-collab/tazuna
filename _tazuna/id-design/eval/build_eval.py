"""source.py から、インプット（design/*.md）と正解（expected.csv）を作る。

    python3 _tazuna/id-design/eval/build_eval.py

あわせて次を確かめ、満たさなければ終了コード1で止まる。
  - 書類実体の書類ID・設計項目名が、型（docs/design/ID設計.md）の書類の種類と設計項目にある
  - 書いた設計項目が、その書類の記載項目に入っている（正しい設計項目も、正しい書類の記載項目に入っている）
  - 振り分け表の198項目が、すべて1行以上インプットに現れる（正しい設計項目で数える）
  （警告だけ）振り分け表の「例」が、その項目のどれかの行の本文と一致しない
"""
import csv
import os
import re
import shutil
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compat as build  # noqa: E402
documents = build  # noqa: E402
from source import INSTANCES, L, TARGET  # noqa: E402

items = {x["item"]: x for x in build.I}
docs = {d[0]: d for d in documents.DOCS}
allowed = {d: {it for it, _, _ in lst} for d, lst in documents.A.items()}
inst = {a: (b, c) for a, b, c in INSTANCES}
errors = []
warnings = []  # 止めない。型（Excel）が原本なので、例を書き換えても評価セットは作れる

for i, item, text, correct, cdoc, over in L:
    if i not in inst:
        errors.append(f"未定義の書類実体 {i}: {text}")
        continue
    if item not in items:
        errors.append(f"振り分け表にない設計項目「{item}」: {text}")
    elif item not in allowed[inst[i][0]]:
        errors.append(f"{inst[i][0]} の記載項目にない「{item}」: {text}")
    ci, cd = correct or item, cdoc or i
    if ci not in items:
        errors.append(f"正しい設計項目が振り分け表にない「{ci}」: {text}")
    elif cd not in inst or ci not in allowed[inst[cd][0]]:
        errors.append(f"正しい書類 {cd} の記載項目にない「{ci}」: {text}")
    for k, v in over.items():
        if k not in ("nature", "check", "appr"):
            errors.append(f"上書きできない属性 {k}: {text}")
        elif ci in items and items[ci][k] == v:
            errors.append(f"既定と同じ上書き（{k}={v}）: {text}")

texts = {}
for _, item, text, correct, _, _ in L:
    texts.setdefault(correct or item, set()).add(text)
for name, x in items.items():
    if name not in texts:
        errors.append(f"インプットに現れない設計項目「{name}」")
    elif x["ex"] not in texts[name]:
        warnings.append(f"振り分け表の例がインプットのどの行とも一致しない「{name}」: {x['ex']}")

for w in warnings:
    print("警告:", w)
if errors:
    print("\n".join(errors))
    sys.exit(1)

LABEL = {"nature": "性質", "check": "機械検査", "appr": "業務承認"}
design_dir = os.path.join(HERE, "design")
shutil.rmtree(design_dir, ignore_errors=True)
os.makedirs(design_dir)
rows = []
files = 0
for i, (doc, title) in inst.items():
    lines = [x for x in L if x[0] == i]
    if not lines:
        continue
    files += 1
    fname = f"{i}_{re.sub(r'（.*?）', '', title).replace(' ', '')}.md"
    md = [f"# {i} {docs[doc][1]}：{title}", "",
          "> 振り分け評価のインプット。設計項目の見出しの下に、1行に1つの決定事項を「- [番号] 本文」で書く。振り分け先は書かない。"]
    order = sorted(dict.fromkeys(x[1] for x in lines), key=lambda it: build.ID[it])
    for it in order:
        md += ["", f"## {build.ID[it]} {it}", ""]
        n = 0  # 番号は見出しの中で付ける
        for _, item, text, correct, cdoc, over in lines:
            if item != it:
                continue
            n += 1
            lid = f"{i}/{build.ID[it]}/{n}"
            md.append(f"- [{n}] {text}")
            ci, cd = correct or item, cdoc or i
            x = dict(items[ci]); x.update(over)
            main, sub = build.map_item(x)
            layer = build.LAYER[docs[inst[cd][0]][2]]
            place, owner = build.place_owner(main, x["appr"], layer)
            judge = "正しい" if (ci, cd) == (item, i) else ("書類違い" if cd != i else "項目違い")
            note = "・".join(f"{LABEL[k]}: {items[ci][k]}→{v}" for k, v in over.items())
            rows.append([lid, fname, doc, docs[doc][1], docs[doc][2], build.ID[item], item, judge,
                         cd, build.ID[ci], ci, text, x["nature"], x["check"], x["appr"],
                         main, sub, place, owner, ("項目の既定と違う（" + note + "）") if note else ""])
    with open(os.path.join(design_dir, fname), "w", encoding="utf-8") as fp:
        fp.write("\n".join(md) + "\n")

# 書類一覧（ID設計.xlsx の書き出しと同じ形で、型に評価セットの機能一覧・書類一覧を入れる）
sys.path.insert(0, os.path.join(build.ROOT, "scripts", "design"))
import catalog  # noqa: E402
snap = dict(build.DATA)
names = {i: re.sub(r"（.*?）", "", title).replace(" ", "") for i, (doc, title) in inst.items()}
snap["書類一覧"] = [{"書類実体ID": i, "書類ID": doc, "書類名": docs[doc][1], "名前": names[i],
                   "機能": TARGET.get(i, ""), "作成": "書く", "理由": ""} for i, (doc, title) in inst.items()]
funcs = {}
for i, (doc, title) in inst.items():
    if doc == "S-22":
        funcs[i] = {"機能": names[i], "画面": [], "ジョブ": [], "IF": [], "帳票": [], "テーブル": [], "説明": ""}
col = {"S-21": "画面", "S-23": "ジョブ", "S-24": "IF", "S-25": "帳票"}
for i, (doc, title) in inst.items():
    if doc in col and TARGET.get(i) in funcs:
        funcs[TARGET[i]][col[doc]].append(names[i])
snap["機能一覧"] = [{k: ("、".join(v) if isinstance(v, list) else v) for k, v in f.items()} for f in funcs.values()]
catalog.write_snapshot(snap, os.path.join(design_dir, catalog.SNAPSHOT))

hdr = ["行ID", "ファイル", "書類ID", "書類名", "区分", "書いた項番", "書いた設計項目", "置き場所の判定",
       "正しい書類実体", "正しい項番", "正しい設計項目", "本文", "性質", "機械検査", "業務承認",
       "振り分け先（主）", "振り分け先（副）", "置き場所", "持ち主", "備考"]
with open(os.path.join(HERE, "expected.csv"), "w", encoding="utf-8-sig", newline="") as fp:
    w = csv.writer(fp)
    w.writerow(hdr)
    w.writerows(rows)

print(f"{len(rows)} 行 / {files} ファイル / 設計項目 {len(texts)}/{len(items)}")
print("置き場所の判定:", dict(Counter(r[7] for r in rows)))
print("属性の上書き:", sum(1 for r in rows if r[19]))
print("区分:", dict(Counter(r[4] for r in rows)))
print("振り分け先（主）:", dict(Counter(r[15] for r in rows)))
