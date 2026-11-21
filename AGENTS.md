# [プロジェクト名]

<!-- 案件では [ ] の部分を書き換える。60行以内に保つ（scripts/lint/common/agents-md-size.sh） -->

## 原則
1. 設計前に `docs/domain/invariants.md` を読み、業務の不変条件を破らない。
2. 完了条件は `docs/requirements/` の要件ID（REQ-xxx）で判断する。
3. 提出前に Lint とテストを通す。テストを消したり止めたりして通さない。
4. 既存コードと同じ書き方を優先する。用語は `docs/domain/glossary.md` に合わせる。
5. PRには実行したコマンドと結果を証拠として書く。要約だけで済ませない。

## コマンド
- Lint: `scripts/lint/run-all.sh`
- ビルドとテスト: `mvn -B verify`

## 参照先
| 知りたいこと | 場所 |
| --- | --- |
| 作業の進め方 | `.github/skills/base-task-workflow/` |
| テストの作り方 | `.github/skills/base-test-design/` |
| 既存の設計書から業務ルールを抽出 | `.github/skills/base-spec-extraction/` |
| 業務ルール・用語・機能一覧 | `docs/domain/` |
| レイヤーと依存方向 | `docs/architecture.md` |
| 命名・作法 | `docs/conventions.md` |

## 編集できないファイル
`docs/requirements/`、`docs/domain/invariants.md`、`base-*` スキル、共通Lint、hooks、CI は hooks で保護されている。変更が必要なときはPRの説明に変更案を書く。
