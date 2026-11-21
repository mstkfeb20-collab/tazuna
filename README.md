# tazuna（手綱）

AIコーディングエージェント（GitHub Copilot）と開発を始めるための、ハーネスのテンプレートリポジトリ。

手綱は、馬が自分で走るのを止めずに方向だけを導く道具。tazuna も同じで、エージェントに手順を細かく教えるのではなく、**正しい方向へ探索し、自分で検証・修正できる環境**を用意する。人間は完了条件・不変条件・最終判断を握る。

## 何が入っているか

```
repo-root/
├─ AGENTS.md                     # エージェントが常に読む索引（60行以内）
├─ .github/
│  ├─ CODEOWNERS                 # パスごとの承認者
│  ├─ pull_request_template.md   # 実行結果と証拠の欄
│  ├─ skills/
│  │  ├─ base-task-workflow/     # 調査→実装→検証→PR（型）
│  │  ├─ base-test-design/       # 要件からテストを作る（型）
│  │  ├─ base-code-review/       # レビューの観点と記録（型）
│  │  ├─ base-harness-improvement/ # ミスを防ぐ層を決める（型）
│  │  └─ proj-example-billing/   # proj スキルの見本
│  ├─ hooks/
│  │  ├─ tazuna-guard.json       # Copilot の hooks 設定
│  │  ├─ deny-commands.txt       # 禁止コマンド
│  │  ├─ protected-paths.txt     # エージェントが編集できないパス
│  │  ├─ scripts/                # guard.sh・lint-after-edit.sh
│  │  └─ tests/                  # hooks の自己テスト
│  └─ workflows/verify.yml       # CI（Lint・hooksテスト・mvn verify）
├─ docs/
│  ├─ requirements/              # 要件・完了条件（REQ-xxx）
│  ├─ domain/                    # 不変条件・用語集・機能一覧
│  ├─ architecture.md
│  └─ conventions.md
├─ scripts/lint/
│  ├─ run-all.sh                 # 全チェックを実行
│  ├─ lib.sh                     # 「内容・理由・修正・参照」を出す共通関数
│  ├─ common/                    # 汎用チェック（型）
│  └─ domain/                    # 業務固有チェック（案件で作る）
├─ src/                          # Java の見本（Money・Invoice・ArchUnit）
└─ harness/
   ├─ GUIDE.md                   # 運用ガイド（人向け）
   ├─ rule-log.md                # 違反の記録
   └─ metrics.md                 # 月次の指標
```

考え方と運用のルールは [harness/GUIDE.md](harness/GUIDE.md) を参照。

## 新しいプロジェクトを始める

### 1. リポジトリを作る
GitHub の「Use this template」から案件のリポジトリを作る。使った tazuna のバージョン（タグ）を README に記録しておく。

### 2. テンプレートの印を消す
```bash
git rm .tazuna-template
```
このファイルがあると、hooks が型（base スキル・共通Lintなど）の編集を許可する。案件では必ず削除する。

### 3. 案件に合わせて書き換える
| ファイル | やること | 担当 |
| --- | --- | --- |
| `.github/CODEOWNERS` | `@your-org/...` を実際のチームに置き換える | 案件リーダー |
| `AGENTS.md` | プロジェクト名とコマンドを書く | 案件リーダー |
| `pom.xml`、`src/` | groupId・パッケージ名を変える。見本の `Money`・`Invoice` は必要なら残す | 案件リーダー |
| `ArchitectureTest.java` | パッケージ指定を合わせる | 案件リーダー |
| `docs/requirements/`、`docs/domain/` | 見本を削除し、要件・不変条件・用語・機能一覧を書く | 社員 |
| `scripts/lint/domain/` | 不変条件ごとにチェックを作る（見本: `java-money-no-float.sh`） | 協力会社 |
| `.github/skills/proj-*` | 見本を削除し、ドメインのスキルを作る | 協力会社・社員 |
| `.github/hooks/` | 本番環境のホスト名などを `deny-commands.txt` に追加する | 案件リーダー |

### 4. 動くことを確かめる
```bash
scripts/lint/run-all.sh
bash .github/hooks/tests/test-guard.sh
mvn -B verify
```

### 5. GitHub の設定
- main ブランチを保護し、CI（`verify`）の成功と CODEOWNERS のレビューを必須にする。
- hooks は既定ブランチにある設定だけが Copilot cloud agent に読み込まれる。

## tazuna 自体を改善する

- このリポジトリには `.tazuna-template` があるため、型のファイルも編集できる。
- 案件から上がってきた昇格候補（`proj-*`、`lint/domain`）は、汎用化して `base-*`、`lint/common` に取り込む。
- 変更したらタグを打つ（例: `v0.2.0`）。案件はタグを見て更新を取り込む。
