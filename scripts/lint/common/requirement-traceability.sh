#!/usr/bin/env bash
# 要件ID（REQ-xxx）とテストを双方向に対応させる。
#   - docs/requirements/ で定義した要件には、必ずテストがある
#   - テストが参照する要件IDは、必ず docs/requirements/ に定義されている
# 要件の定義は見出し「## REQ-001 タイトル」の形式で書く。
# テストからの参照は、テストコード中に REQ-001 の文字列を含める（例: @Tag("REQ-001")）。
source "$(dirname "$0")/../lib.sh"

REQ_DIR="$TAZUNA_ROOT/docs/requirements"
TEST_DIRS="${TAZUNA_TEST_DIRS:-src/test tests}"

[ -d "$REQ_DIR" ] || lint_finish

defined=$(grep -rhoE '^##[[:space:]]+REQ-[0-9]+' "$REQ_DIR" 2>/dev/null | grep -oE 'REQ-[0-9]+' | sort -u)

referenced=""
for d in $TEST_DIRS; do
  [ -d "$TAZUNA_ROOT/$d" ] || continue
  referenced+=$'\n'$(grep -rhoE 'REQ-[0-9]+' "$TAZUNA_ROOT/$d" 2>/dev/null)
done
referenced=$(echo "$referenced" | grep -E 'REQ-' | sort -u)

for id in $defined; do
  if ! grep -qx "$id" <<< "$referenced"; then
    lint_error "COMMON-003" "docs/requirements ($id)" \
      "要件 $id に対応するテストがありません" \
      "完了条件をテストで確かめられないと、エージェントも人も『終わった』と判断できません" \
      "テスト作成エージェントに要件 $id からテストを作らせ、テストに @Tag(\"$id\") を付けてください" \
      ".github/skills/base-test-design/SKILL.md"
  fi
done

for id in $referenced; do
  if ! grep -qx "$id" <<< "$defined"; then
    lint_error "COMMON-003" "テストコード ($id)" \
      "テストが参照する $id が docs/requirements/ に定義されていません" \
      "要件の正本にない ID は、削除された要件か誤記です。テストが何を保証しているか追えなくなります" \
      "docs/requirements/ に '## $id' を定義するか、テストの ID を正しいものに直してください" \
      "docs/requirements/README.md"
  fi
done
lint_finish
