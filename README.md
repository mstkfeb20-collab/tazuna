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
│  │  ├─ base-spec-extraction/   # 既存の設計書から守りたいものを抽出（型）
│  │  ├─ base-design-check/      # ID 設計書の置き場所と属性の例外を確認（型）
│  │  └─ proj-example-reservation/ # proj スキルの見本
│  ├─ hooks/
│  │  ├─ tazuna-guard.json       # Copilot の hooks 設定
│  │  ├─ deny-commands.txt       # 禁止コマンド
│  │  ├─ protected-paths.txt     # エージェントが編集できないパス
│  │  ├─ scripts/                # guard.sh・lint-after-edit.sh
│  │  └─ tests/                  # hooks の自己テスト
│  └─ workflows/verify.yml       # CI（Lint・hooksテスト・mvn verify）
├─ docs/
│  ├─ design/                    # ID 設計
│  │  ├─ ID設計.xlsx             # 原本。機能一覧（人が書く）→ 書類一覧・進捗・網羅状況（自動）、型（書類の種類・記載項目・設計項目）
│  │  ├─ ID設計.md               # Excel の書き出し（PR で差分を読む・ツールが読む）
│  │  └─ S-22-001_予約登録.md など # 設計書（1書類1ファイル。案件で書く）
│  ├─ requirements/              # 要件・完了条件（REQ-xxx）。ID 設計から転記した分も入る
│  ├─ domain/                    # 不変条件・用語集・機能一覧
│  │  └─ candidates/             # 設計書から抽出した候補（承認前）
│  ├─ tasks/                     # ID 設計から転記した作業一覧（実装の issue から参照）
│  ├─ architecture.md
│  └─ conventions.md
├─ scripts/design/
│  ├─ id_design.py               # 書類一覧・ひな形・進捗の作成、Excel の書き出し
│  ├─ transcribe.py              # 設計書を振り分け先（要件・作業一覧など）へ転記する
│  └─ catalog.py                 # Excel と書き出しの読み書き
├─ scripts/lint/
│  ├─ run-all.sh                 # 全チェックを実行
│  ├─ lib.sh                     # 「内容・理由・修正・参照」を出す共通関数
│  ├─ common/                    # 汎用チェック（型）。ID 設計書の置き場所・転記漏れも検査
│  ├─ tests/                     # Lint・転記ツール・ID 設計のコマンドの自己テスト
│  └─ domain/                    # 業務固有チェック（案件で作る）
├─ src/                          # Java の見本（ツアー予約・ArchUnit）
└─ harness/
   ├─ GUIDE.md                   # 運用ガイド（人向け）
   ├─ rule-log.md                # 違反の記録
   └─ metrics.md                 # 月次の指標
```

考え方と運用のルールは [harness/GUIDE.md](harness/GUIDE.md) を参照。

## ID 設計から実装までの進め方

| 段階 | すること | コマンド（人が実行） | 承認 |
| --- | --- | --- | --- |
| 準備 | `ID設計.xlsx` の機能一覧に、機能と画面・ジョブ・IF・帳票・テーブルを書く。書類一覧ができたら、作らない書類に「書かない」を付ける | `id_design.py list` → `id_design.py scaffold` | 社員 |
| ① 設計 | ひな形の見出しの下に1行1決定事項を `- [番号] 本文` で書き（番号は見出しの中で付け、振り直さない）、書類ごとに PR でレビューする | — | 社員 |
| ② 要件を決める | 機能の資料がそろったら転記し、要件とテスト仕様を PR で決める | `transcribe.py` | 社員 |
| ③ 実装 | 要件とテスト仕様からテストと実装を書く。PR に `対象要件: REQ-xxx` を書く | — | 案件リーダー |
| ④ マージ | Lint と CI（対象要件にテストがあるか）を通してマージする | — | — |

進み具合は `git fetch` の後に `python3 scripts/design/id_design.py progress` で（統合先のブランチと比べて「完了」を決める。既定は GitHub の既定のブランチで、`--base origin/develop` や環境変数 `TAZUNA_BASE_BRANCH` で変えられる） `ID設計.xlsx` の進捗・網羅状況シートに出る（未着手・執筆中・レビュー中・完了・要転記、要件ごとの未実装・テストあり）。Excel を直したら `id_design.py export` で書き出し（`ID設計.md`）も作り直し、一緒にコミットする。Excel を読むコマンドには `pip install openpyxl` が要る。

## 指南書（テンプレートの外）

導入の考え方・役割分担・立ち上げ手順をまとめた [新規プロジェクト向け ハーネス導入指南書](_tazuna/guide.md) は `_tazuna/` に置いています。`_tazuna/` は tazuna 本体専用のフォルダで、テンプレートには含めません。

## 新しいプロジェクトを始める

### 1. リポジトリを作る
GitHub の「Use this template」から案件のリポジトリを作る。使った tazuna のバージョン（タグ）を README に記録しておく。

### 2. tazuna 本体専用のフォルダを消す
```bash
git rm -r _tazuna
```
`_tazuna/` には指南書が入っており、tazuna 本体であることを示す印も兼ねている。このフォルダがあると、hooks が型（base スキル・共通Lintなど）の編集を許可する。案件では必ず削除する。

### 3. 案件に合わせて書き換える
| ファイル | やること | 担当 |
| --- | --- | --- |
| `.github/CODEOWNERS` | `@your-org/...` を実際のチームに置き換える | 案件リーダー |
| `AGENTS.md` | プロジェクト名とコマンドを書く | 案件リーダー |
| `pom.xml`、`src/` | groupId・パッケージ名を変える。見本のツアー予約（`Money`・`Tour`・`Reservation` など）は必要なら残す | 案件リーダー |
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

## 型の更新を取り込む

案件リポジトリでは開発ソースとハーネスを一緒に管理する。ただし型のファイル（`harness/tazuna-paths.txt` に載っているもの）は案件で直接直さず、tazuna で直したものを取り込む。

```
tazuna（型）           ──タグ v0.2.0──▶  案件リポジトリ
  base-*、lint/common、hooks など           開発ソース＋案件のハーネス
        ▲                                       │
        └────── 昇格候補・修正依頼 ──────────────┘
```

### 下り：tazuna の新しいバージョンを取り込む（案件リーダー）
```bash
scripts/tazuna-update.sh v0.2.0
```
- 型のファイルだけを指定したタグの内容に置き換え、タグ側で削除されたファイルは消す。案件のファイルには触れない。
- 使っているバージョンは `harness/tazuna-version` に記録される。
- コミットはしないので、差分と Lint を確認してから案件リポジトリでPRを出す。
- 社内の GitLab などから取り込むときは `TAZUNA_REMOTE_URL=<URL>` を付けて実行する。

### 上り：型を直したいとき
1. 案件で型の不具合や改善点に気づいたら、`harness/rule-log.md` に記録する。
2. tazuna リポジトリを別に clone し、そこで直して tazuna にPRを出す（標準化チームが承認）。
3. 標準化チームがタグを打つ。
4. 各案件は上の「下り」の手順で取り込む。

案件リポジトリで型のファイルを直してはいけない。次の取り込みで上書きされ、修正が消える（エージェントの編集は hooks で止まる）。

## tazuna 自体を改善する

- このリポジトリには `_tazuna/` があるため、型のファイルも編集できる。
- 指南書（`_tazuna/guide.md`）を更新するときは、ひな形の中身を複製せず、実ファイルへのリンクで参照する。
- 案件から上がってきた昇格候補（`proj-*`、`lint/domain`）は、汎用化して `base-*`、`lint/common` に取り込む。
- 変更したら `harness/tazuna-version` を新しいバージョンに書き換えてからタグを打つ（例: `v0.2.0`）。案件はタグを指定して更新を取り込む。
- 型のファイルを追加・削除したら、`harness/tazuna-paths.txt` も更新する。取り込みスクリプトは新しいタグ側の一覧を使う。
