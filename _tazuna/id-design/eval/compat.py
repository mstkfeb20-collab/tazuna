"""評価セットのスクリプトが使う、型（docs/design/ID設計.md）の読み出し。

原本は docs/design/ID設計.xlsx。以前の生成スクリプト（build.py・documents.py）と同じ名前で、型の中身を渡す。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, "scripts", "design"))
import catalog  # noqa: E402

_cat = catalog.load(os.path.join(ROOT, "docs", "design"))
I = [dict(item=r["設計項目"], view=r["観点"], nature=r["性質"], check=r["機械検査"], appr=r["業務承認"], ex=r["例"])
     for r in _cat.data["設計項目"]]
ID = {r["設計項目"]: r["項番"] for r in _cat.data["設計項目"]}
DOCS = [(r["書類ID"], r["書類名"], r["区分"], r["作る単位"]) for r in _cat.data["書類の種類"]]
A = {}
for r in _cat.data["記載項目"]:
    A.setdefault(r["書類ID"], []).append((r["設計項目"], r["記載"], r["この書類で書くこと"]))
LAYER = catalog.LAYER
DATA = _cat.data

def map_item(x):
    """性質・機械検査・業務承認から、振り分け先（主・副）を決める。人の判断を入れない。"""
    n, c, a = x["nature"], x["check"], x["appr"]
    if n == "行為・操作":
        return "hooks（行為を止める）", "AIへの条件（AGENTS.md に禁止事項として明記）"
    if n == "背景知識":
        return "知識", "—"
    if c == "静的に可":
        main = "Lint（成果物を検査）" if n == "構造・依存" else "設計（型・API・DB制約で防ぐ）"
    elif c == "実行で可":
        main = "実行検証（動かして測る）" if n == "方針・判断" else "テスト"
    else:
        if a == "要":
            return "人のための設計（承認の対象）", "AIへの条件（決まった内容を伝える）"
        return "AIへの条件（文章で伝える）", "—"
    return main, ("正本に根拠を記載（承認）" if a == "要" else "—")
def place_owner(main, appr, layer):
    """振り分け先と書類の区分（共通／機能別）から、案件リポジトリでの置き場所と持ち主を決める。"""
    common = layer == "共通"
    head = main.split("（")[0]
    if head == "hooks":
        place = ".github/hooks/（deny-commands・protected-paths）"
    elif head == "知識":
        place = "docs/domain/（glossary・参照文書の一覧）" if common else "docs/domain/feature-map.md"
    elif head == "Lint":
        place = "scripts/lint/domain/・ArchitectureTest" if common else "scripts/lint/domain/"
    elif head == "設計":
        place = "案件の共通部品・コード定義・DDL（src/main）" if common else "src/main の型・DDL の制約"
    elif head == "実行検証":
        place = "性能・運用試験＋PRの証拠"
    elif head == "テスト":
        if appr == "要":
            place = "docs/domain/invariants.md・共通の要件 → src/test" if common else "docs/requirements/<機能>.md の完了条件 → src/test"
        else:
            place = "src/test"
    elif head == "人のための設計":
        place = "設計書（承認）→ 決定事項を docs/domain へ"
    else:  # AIへの条件
        place = "docs/conventions.md・.github/skills/proj-*" if common else "issue の参照先・.github/skills/proj-*（その業務）"
    return place, ("社員" if appr == "要" else "案件リーダー")
