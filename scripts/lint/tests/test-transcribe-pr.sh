#!/usr/bin/env bash
# scripts/design/transcribe_pr.py（転記の PR の本文）の自己テスト。
set -u
cd "$(dirname "$0")/../../.." || exit 2
ROOT="$PWD"; pass=0; fail=0
check() { if grep -qF -- "$2" <<<"$3"; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "NG: $1（「$2」がない）"; echo "$3" | sed 's/^/    /'; fi; }
nocheck() { if grep -qF -- "$2" <<<"$3"; then fail=$((fail + 1)); echo "NG: $1（「$2」がある）"; else pass=$((pass + 1)); fi; }
w=$(mktemp -d); trap 'rm -rf "$w"' EXIT
g() { git -C "$w" -c user.name=t -c user.email=t@t "$@"; }
g init -q; mkdir -p "$w/docs/design" "$w/docs/requirements"
echo "- [1] 予約を取り消す" > "$w/docs/design/S-22-002_予約取消.md"; g add -A; g commit -qm "設計: 取消料を請求する (#19)"
before=$(g rev-parse HEAD)
echo "- [2] 請求する" >> "$w/docs/design/S-22-002_予約取消.md"; g commit -qam "設計: 請求番号 (#21)"
printf -- '- 未決: 認可（S-22-001/D-11002）\n- 未決（案）: 判定（S-22-002/D-04003/5）: 21日前は0%%\n' > "$w/docs/requirements/S-22-002_予約取消.md"
out=$(TAZUNA_ROOT="$w" python3 "$ROOT/scripts/design/transcribe_pr.py" --base main --range "$before..HEAD")
check "テンプレートどおり対象要件の行を入れる" "対象要件: なし" "$out"
check "もとになった設計の変更を出す" "設計: 請求番号 (#21)" "$out"
nocheck "範囲の外の変更は出さない" "設計: 取消料を請求する (#19)" "$out"
check "関連の番号を出す" "関連: #21" "$out"
check "変わった転記先を出す" '- `docs/requirements/S-22-002_予約取消.md`' "$out"
check "未決と（案）の件数を出す" "転記先にある未決: 2 件（うち「（案）」のまま 1 件）" "$out"
check "標準の権限では CI が動かないことを伝える" "この PR の CI は動いていません" "$out"
out=$(TAZUNA_ROOT="$w" python3 "$ROOT/scripts/design/transcribe_pr.py" --base main --range "0000000..HEAD" --no-ci-note)
nocheck "CI が動くときは注意を出さない" "この PR の CI は動いていません" "$out"
check "範囲が読めなければ最後のコミットを出す" "設計: 請求番号 (#21)" "$out"
echo "transcribe-pr: ${pass} 件成功 / ${fail} 件失敗"
[ "$fail" -eq 0 ]
