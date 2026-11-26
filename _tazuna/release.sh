#!/usr/bin/env bash
# tazuna の新しいバージョンを出す（tazuna 本体だけで使う。案件では _tazuna/ ごと消える）。
#   _tazuna/release.sh v0.5.0
# harness/tazuna-version の書き換え・Lint と自己テスト・コミット・タグ・push を1回で行う。
# 手で打つと tazuna-version の書き換えが漏れるため（漏れたタグは CI「タグとバージョンの確認」が赤にする）。
set -euo pipefail
TAG="${1:-}"
[[ "$TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "使い方: _tazuna/release.sh vX.Y.Z" >&2; exit 2; }
cd "$(git rev-parse --show-toplevel)"
[ -d _tazuna ] || { echo "tazuna 本体で実行してください" >&2; exit 2; }
[ "$(git rev-parse --abbrev-ref HEAD)" = main ] || { echo "main で実行してください" >&2; exit 2; }
git diff --quiet && git diff --cached --quiet || { echo "未コミットの変更があります" >&2; exit 2; }
git fetch -q origin main && [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "origin/main と揃えてから実行してください" >&2; exit 2; }
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null && { echo "タグ $TAG はもうあります" >&2; exit 2; }

bash scripts/lint/run-all.sh
for t in scripts/lint/tests/test-*.sh .github/hooks/tests/test-*.sh; do [ -f "$t" ] && bash "$t" >/dev/null; done
echo "$TAG" > harness/tazuna-version
git commit -qm "$TAG" -- harness/tazuna-version
git tag "$TAG"
git push -q origin main "refs/tags/$TAG"
echo "$TAG を出しました。案件では scripts/tazuna-update.sh $TAG で取り込めます"
