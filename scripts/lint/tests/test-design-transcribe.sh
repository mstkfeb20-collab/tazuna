#!/usr/bin/env bash
# scripts/design/transcribe.py の自己テスト。転記・作り直し（冪等）・手で直したときの検出・手で書いた部分の保持を確かめる。
set -u
cd "$(dirname "$0")/../../.." || exit 2
ROOT="$PWD"; PY="$ROOT/scripts/design/transcribe.py"
pass=0; fail=0
ok() { pass=$((pass + 1)); }
ng() { fail=$((fail + 1)); echo "NG: $1"; }

w=$(mktemp -d); mkdir -p "$w/docs/design" "$w/harness"; cp -r "$ROOT/harness/id-design" "$w/harness/"
cat > "$w/docs/design/S-22-001_予約登録.md" <<'MD'
# S-22-001 処理設計書：予約登録

## D-03002 相関チェック

- S-22-001-001 大人人数と子供人数の合計が1人以上であること

## D-04009 例外的な業務判断

- S-22-001-002 10人以上の団体は窓口担当が個別に見積もる

## D-03001 単項目チェック

- S-22-001-003 （廃止）画面設計書へ移した
MD
run() { TAZUNA_ROOT="$w" python3 "$PY" --design "$w/docs/design" --out "$w" "$@" >/dev/null 2>&1; }

run; req="$w/docs/requirements/S-22-001_予約登録.md"
grep -q '^## REQ-22001 予約登録' "$req" && grep -q '合計が1人以上であること（S-22-001-001・相関チェック）' "$req" && ok || ng "要件に転記される"
grep -q '10人以上の団体' "$req" && ok || ng "AIへの条件は要件ファイルの条件に入る"
grep -q 'S-22-001-003' "$req" && ng "廃止の行は転記しない" || ok
run --check && ok || ng "作り直した直後は食い違いがない"
cp "$req" "$w/before"; run; cmp -s "$req" "$w/before" && ok || ng "作り直しても変わらない（冪等）"
printf '\n手で書いたメモ\n' >> "$req"; run; grep -q '手で書いたメモ' "$req" && ok || ng "目印の外の手書きは残る"
sed -i 's/合計が1人以上/合計が2人以上/' "$req"; run --check && ng "目印の中を手で直すと検出する" || ok
run; grep -q '合計が1人以上' "$req" && ok || ng "作り直すと設計書の内容に戻る"
sed -i 's/合計が1人以上であること/合計が1人以上9人以下であること/' "$w/docs/design/S-22-001_予約登録.md"
run --check && ng "設計書を直して転記し忘れると検出する" || ok
cat > "$w/docs/design/S-26-001_予約登録.md" <<'MD'
# S-26-001 テスト仕様書：予約登録

## D-15001 テスト観点・ケース

- S-26-001-001 同じ受付トークンで2回確定しても、予約は1件だけ登録される
MD
printf '| 書類実体ID | 書類 | 名前 | 機能 |\n| --- | --- | --- | --- |\n| S-22-001 | 処理設計書 | 予約登録 | |\n| S-26-001 | テスト仕様書 | 予約登録 | S-22-001 |\n' > "$w/docs/design/書類一覧.md"
run
grep -q '^## REQ-26001 予約登録（テスト仕様書）' "$req" && ok || ng "書類一覧で機能を書いたテスト仕様書の要件は、処理設計書の要件ファイルにまとまる"
[ ! -e "$w/docs/requirements/S-26-001_予約登録.md" ] && ok || ng "テスト仕様書だけの要件ファイルは作らない"
rm -rf "$w"

echo "design-transcribe: ${pass} 件成功 / ${fail} 件失敗"
[ "$fail" -eq 0 ]
