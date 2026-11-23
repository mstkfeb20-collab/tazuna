"""base-design-check の指摘一覧（タブ区切り）を、正解（expected.csv）と突き合わせて採点する。

    python3 _tazuna/id-design/eval/score.py <指摘一覧.tsv> [...]

指摘一覧は複数ファイルに分けてよい（まとめて読む）。採点すること:
  1. 置き場所の間違い（項目違い・書類違い）を見つけたか。正しい書類ID・項番まで合っているか
  2. 属性の例外を見つけたか。3属性まで合っているか
  3. 指摘のない行も含めて、最終的な振り分け先（主）が正解と一致した行の割合
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compat as build  # noqa: E402

exp = {r["行ID"]: r for r in csv.DictReader(open(os.path.join(HERE, "expected.csv"), encoding="utf-8-sig"))}
items = {build.ID[x["item"]]: x for x in build.I}

got = {}
for path in sys.argv[1:]:
    for raw in open(path, encoding="utf-8"):
        cols = raw.rstrip("\n").split("\t")
        if len(cols) < 2 or cols[0] == "行ID" or cols[0] not in exp:
            continue
        cols += [""] * (8 - len(cols))
        lid, kind, doc, iid, n, c, a, why = cols[:8]
        got[lid] = dict(kind=kind.strip(), doc=doc.strip(), iid=iid.strip(), nature=n.strip(), check=c.strip(),
                        appr=a.strip(), why=why)

mis = {k for k, r in exp.items() if r["置き場所の判定"] != "正しい"}
exc = {k for k, r in exp.items() if r["備考"]}
place_kinds = ("項目違い", "書類違い")

found = {k for k, g in got.items() if g["kind"] in place_kinds}
tp = found & mis
exact = {k for k in tp if got[k]["iid"] == exp[k]["正しい項番"] and got[k]["doc"] == exp[k]["正しい書類実体"][:4]}
fp_place = sorted(found - mis)

flag_exc = {k for k, g in got.items() if g["kind"] == "属性の例外" or (g["kind"] in place_kinds and g["nature"])}
tp_e = flag_exc & exc
exact_e = {k for k in tp_e if (got[k]["nature"], got[k]["check"], got[k]["appr"]) ==
           (exp[k]["性質"], exp[k]["機械検査"], exp[k]["業務承認"])}
fp_exc = sorted(k for k in flag_exc - exc if got[k]["kind"] == "属性の例外")

# 最終的な振り分け先: 指摘がなければ書いた見出しの既定。指摘があればその項目・属性
ok = 0
wrong = []
for k, r in exp.items():
    iid = r["書いた項番"]
    x = dict(items[iid])
    g = got.get(k)
    if g:
        if g["kind"] in place_kinds and g["iid"] in items:
            x = dict(items[g["iid"]])
        if g["nature"]:
            x.update(nature=g["nature"], check=g["check"] or x["check"], appr=g["appr"] or x["appr"])
    main, _ = build.map_item(x)
    if main == r["振り分け先（主）"]:
        ok += 1
    else:
        wrong.append((k, main, r["振り分け先（主）"]))

n = len(exp)
base_ok = sum(1 for k, r in exp.items() if build.map_item(items[r["書いた項番"]])[0] == r["振り分け先（主）"])
print(f"置き場所の間違い  : {len(tp)}/{len(mis)} 件を発見、うち正しい書類・項番まで一致 {len(exact)} 件、誤検出 {len(fp_place)} 件")
print(f"属性の例外        : {len(tp_e)}/{len(exc)} 件を発見、うち3属性まで一致 {len(exact_e)} 件、誤検出 {len(fp_exc)} 件")
print(f"振り分け先（主）  : {ok}/{n} 行が一致（{ok / n:.1%}）。指摘なしで見出しどおりに振り分けた場合は {base_ok}/{n}（{base_ok / n:.1%}）")
print(f"迷い              : {sum(1 for g in got.values() if '迷い' in g['why'])} 件")
if "-v" in os.environ.get("SCORE_FLAGS", "-v"):
    for k in sorted(mis - tp):
        print("  見逃し（置き場所）", k, exp[k]["書いた設計項目"], "→", exp[k]["正しい設計項目"], "|", exp[k]["本文"][:40])
    for k in sorted(tp - exact):
        print("  先が違う", k, got[k]["doc"], got[k]["iid"], "正解", exp[k]["正しい書類実体"][:4], exp[k]["正しい項番"])
    for k in fp_place:
        print("  誤検出（置き場所）", k, exp[k]["書いた設計項目"], "→", got[k]["iid"], items.get(got[k]["iid"], {}).get("item", "?"), "|", exp[k]["本文"][:40])
    for k in sorted(exc - tp_e):
        print("  見逃し（例外）", k, exp[k]["書いた設計項目"], exp[k]["備考"], "|", exp[k]["本文"][:40])
    for k in sorted(tp_e - exact_e):
        print("  属性が違う", k, got[k]["nature"], got[k]["check"], got[k]["appr"], "正解", exp[k]["性質"], exp[k]["機械検査"], exp[k]["業務承認"])
    for k in fp_exc:
        print("  誤検出（例外）", k, exp[k]["書いた設計項目"], got[k]["nature"], got[k]["check"], got[k]["appr"], "|", exp[k]["本文"][:40])
