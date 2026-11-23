#!/usr/bin/env bash
# design_docs.py（COMMON-007）の自己テスト。壊した設計書を1つずつ置き、期待どおり止まるかを確かめる。
set -u
cd "$(dirname "$0")/../../.." || exit 2
ROOT="$PWD"
PY="$ROOT/scripts/lint/common/design_docs.py"
pass=0; fail=0

good='# S-21-002 画面設計書：予約入力

## D-02002 画面項目定義

- S-21-002-001 大人人数: プルダウン
- S-21-002-002 備考: テキストエリア、最大80文字
'

# case <名前> <期待（ok|ng）> <ファイル名> <本文> [期待するメッセージの一部]
case_() {
  local name="$1" expect="$2" file="$3" body="$4" needle="${5:-}"
  local dir; dir=$(mktemp -d)
  printf '%s' "$body" > "$dir/$file"
  local out rc
  out=$(TAZUNA_ROOT="$ROOT" python3 "$PY" "$dir" 2>&1); rc=$?
  out=$(grep -v '^WARN' <<<"$out")
  local got=ok; [ "$rc" -ne 0 ] && got=ng
  if [ "$got" = "$expect" ] && { [ -z "$needle" ] || grep -qF -- "$needle" <<<"$out"; }; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "NG: $name（期待 $expect、結果 $got）"; echo "$out" | head -5
  fi
  rm -rf "$dir"
}

case_ "正しい設計書" ok "S-21-002_予約入力.md" "$good"
case_ "ファイル名に書類実体IDがない" ng "予約入力.md" "$good" "書類実体ID_名前.md"
case_ "ドキュメント体系にない書類ID" ng "S-99-001_何か.md" "${good//S-21-002/S-99-001}" "S-99 がドキュメント体系にありません"
case_ "見出しの形が違う" ng "S-21-002_予約入力.md" "${good/\#\# D-02002 画面項目定義/## 画面項目定義}" "D-ccsss 設計項目名"
case_ "カタログにない項番" ng "S-21-002_予約入力.md" "${good/D-02002/D-02999}" "D-02999 がカタログにありません"
case_ "項番と名前が合わない" ng "S-21-002_予約入力.md" "${good/画面項目定義/画面遷移}" "名前が違います"
case_ "その書類に書かない項目" ng "S-21-002_予約入力.md" "${good/D-02002 画面項目定義/D-05001 テーブル定義}" "S-16"
case_ "行IDが別の書類実体" ng "S-21-002_予約入力.md" "${good/S-21-002-002/S-21-003-002}" "S-21-002-通し番号3桁"
case_ "行IDの重複" ng "S-21-002_予約入力.md" "${good/S-21-002-002/S-21-002-001}" "重複しています"
case_ "見出しより前の行" ng "S-21-002_予約入力.md" "# S-21-002 画面設計書

- S-21-002-001 大人人数: プルダウン
" "どの見出しの下にもありません"

# base から行IDが消えたら止まる（一時的な git リポジトリで確かめる）
repo=$(mktemp -d)
( cd "$repo" && git init -q && mkdir -p docs/design && printf '%s' "$good" > docs/design/S-21-002_予約入力.md \
  && git add -A && git -c user.email=t@t -c user.name=t commit -qm base \
  && printf '%s' "$good" | grep -v 'S-21-002-002' > docs/design/S-21-002_予約入力.md )
mkdir -p "$repo/harness" && cp -r "$ROOT/harness/id-design" "$repo/harness/"
out=$(TAZUNA_ROOT="$repo" python3 "$PY" "$repo/docs/design" --base HEAD 2>&1); rc=$?
if [ "$rc" -ne 0 ] && grep -qF "S-21-002-002 が HEAD から消えています" <<<"$out"; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "NG: 消えた行ID"; echo "$out" | head -5; fi
printf '%s' "${good/最大80文字/（廃止）80文字の制限は要件から外れた}" > "$repo/docs/design/S-21-002_予約入力.md"
out=$(TAZUNA_ROOT="$repo" python3 "$PY" "$repo/docs/design" --base HEAD 2>&1); rc=$?
if [ "$rc" -eq 0 ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "NG: 廃止にした行は通る"; echo "$out" | head -5; fi
rm -rf "$repo"

echo "design-docs: ${pass} 件成功 / ${fail} 件失敗"
[ "$fail" -eq 0 ]
