"""書類一覧（docs/design/書類一覧.md）を読む。Lint（design_docs.py）と転記ツール（transcribe.py）が使う。

書類一覧は、案件の ID 設計書の書類実体と、それがどの機能のものかを1か所にまとめた表。機能一覧（S-10）を作るときに一緒に作る。

    | 書類実体ID | 書類 | 名前 | 機能 |
    | --- | --- | --- | --- |
    | S-22-005 | 処理設計書 | 振込データ取込 | |
    | S-23-001 | ジョブ設計書 | J110振込取込 | S-22-005 |
    | S-24-002 | IF定義書 | 手配会社予約受付API | S-22-002、S-22-003 |

- 名前は、ファイル名の「書類実体ID_」の後ろと同じにする（S-23-001_J110振込取込.md）。
- 機能の欄: 機能別設計の書類のうち、処理設計書（S-22）以外は、その書類を使う処理設計書を書く（複数可）。
  共通設計・開発運用の書類と、処理設計書自身は空にする。
"""
import os
import re

NAME = "書類一覧.md"
ROW_RE = re.compile(r"^\|\s*(S-\d{2}-\d{3})\s*\|(.*)\|\s*$")


def path(folder):
    return os.path.join(folder, NAME)


def read(folder):
    """{書類実体ID: dict(行番号, 書類, 名前, 機能=[S-22-nnn...])} と、重複した書類実体IDの一覧を返す。ファイルがなければ None"""
    p = path(folder)
    if not os.path.exists(p):
        return None, []
    rows, dups = {}, []
    with open(p, encoding="utf-8") as fp:
        for n, raw in enumerate(fp, 1):
            m = ROW_RE.match(raw.rstrip("\n"))
            if not m:
                continue
            cells = [c.strip() for c in m.group(2).split("|")]
            cells += [""] * (3 - len(cells))
            funcs = [s.strip() for s in re.split(r"[、,]", cells[2]) if s.strip() and s.strip() not in ("—", "-")]
            if m.group(1) in rows:
                dups.append((n, m.group(1)))
            rows[m.group(1)] = dict(line=n, doc=cells[0], name=cells[1], funcs=funcs)
    return rows, dups
