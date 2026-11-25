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
├─ scripts/report/report.py     # PR 単位・日次のレポート（読むだけ。CI が PR と issue にコメントする）
├─ scripts/report/gitlab.py     # GitLab で運用するときの MR・issue の読み書き
├─ .gitlab-ci.yml               # GitLab で運用するときの CI（.github/workflows と同じことをする）
├─ scripts/design/review_pack.py # 設計書レビューの材料（同じ設計項目の行・定義の一覧・決定とテスト仕様）
├─ scripts/report/next.py       # 案内役：次に何をするか（読むだけ。base-navigator スキルが使う）
├─ scripts/lint/
│  ├─ run-all.sh                 # 全チェックを実行
│  ├─ lib.sh                     # 「内容・理由・修正・参照」を出す共通関数
│  ├─ common/                    # 汎用チェック（型）。ID 設計書の置き場所・転記漏れ・DDL の説明も検査
│  ├─ tests/                     # Lint・転記ツール・ID 設計のコマンドの自己テスト
│  └─ domain/                    # 業務固有チェック（案件で作る）
├─ db/schema/                    # DDL（テーブル・列の正。全テーブル・全列に説明、範囲は CHECK 制約）
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

### 次に何をするか（案内役）

Copilot のチャットで「次は何をすればいい？」と聞くと、スキル `base-navigator` が `python3 scripts/report/next.py` で状態を読み、止まっているものから順に、誰が・何を・どうやって進めるかを案内して一緒に進める。CI の承認待ち、Copilot の質問、レビュー待ちの PR、転記が要る設計書、issue のない要件、必須の見出しが空の設計書、機能一覧と書類一覧のずれを見る。`--issue REQ-xxxxx` で要件を実装する issue の下書きを出す。業務の決定・承認・マージは人がする。

### 開発期間のレポート

- **PR 単位:** CI が PR にコメントする（`scripts/report/report.py pr`）。対象要件ごとに、テスト仕様の行がテストで確かめられたか（テストに付けた `@Tag("S-26-xxx/D-xxxxx/n")` を数える）、作業一覧の行のうち PR の本文に「未対応: 行ID（理由）」と書いたもの、「設計書から: 行ID（理由）」と書いた設計書の行（転記先にあるか、ないか）、テストと Lint の結果、保護ファイルに触れていないかを出す。
- **日次:** `.github/workflows/tazuna-report.yml` が平日の朝に、統合ブランチごとの issue「日次レポート（ブランチ名）」にコメントする。状態が変わった書類、新しく決まった要件、テストありになった要件、コミットを出す。対象はリポジトリの変数 `TAZUNA_REPORT_BRANCHES`（空白区切り、既定は `develop`）。main を商用リリース版にする運用では main を対象にしない。

### 設計書の書き方の決まり

- 書類の種類の番号（S-xx）は意味を持たない。共通か機能別かは「区分」、機能の中心の書類（処理設計書）とテスト仕様の書類は「役割」の列で決まる。使わなくなった種類は「状態」を「廃止」にする（番号は再利用しない）。
- 図（Mermaid など）や表は、それを説明する行「- [n] 本文」の直下に2文字字下げして書く。行と一緒に転記される。どの行にも付いていない図は Lint（COMMON-007）で止まる。
- テーブル・列の正は DDL（`db/schema/*.sql`）。全テーブル・全列に説明（COMMENT）を書き、値の範囲は CHECK 制約で書く。区分値の列の説明には、値の意味を決めたコード定義書の行（例 `S-15-001/D-05005/1`）を書く（Lint COMMON-010）。エンティティと関連（ER 図）と正規化の方針はデータモデル設計書（S-20）、DDL に書けない決定（保持期間・データ量・索引の理由など）はテーブル設計書（S-16）に書く。

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

### 5'. GitLab で運用するとき
tazuna は GitLab でもそのまま使える。CI は `.gitlab-ci.yml`、MR のテンプレートは `.gitlab/merge_request_templates/Default.md` にある（GitHub 用のファイルと並べて置いてよい。互いに読まない）。

**エージェントは手元で動かす。** Copilot のクラウドエージェントは GitHub 専用なので、作業する人が VS Code の Copilot（エージェントモード）で issue を実装し、MR を出す。`AGENTS.md`・`.github/skills/`・`.github/hooks/` は、リポジトリの置き場所に関係なく VS Code の Copilot が読む（hooks は VS Code ではプレビュー。各自の PC に bash と jq が要る）。

| 設定 | やること |
| --- | --- |
| CI/CD の変数 | `TAZUNA_GITLAB_TOKEN`（プロジェクトのアクセストークン。ロール Reporter 以上・スコープ api・マスクする）。MR の説明の読み取りと、レポートの書き込みに使う。日次レポートの対象を変えるなら `TAZUNA_REPORT_BRANCHES` |
| 日次レポート | Build → Pipeline schedules に平日の朝の予定を作り、変数 `TAZUNA_DAILY_REPORT=1` を付ける |
| ブランチの保護 | main（と develop）を保護し、Merge requests の「Pipelines must succeed」を有効にする |
| 承認者 | `.github/CODEOWNERS` を `.gitlab/CODEOWNERS` に移し、`@your-org/...` を GitLab のグループに置き換える（必須の承認にするには Premium 以上の「Code Owner approval」） |
| Runner | Docker で動く Runner が要る。社内のレジストリを使うなら、`.gitlab-ci.yml` の `python:3.12`・`maven:3.9-eclipse-temurin-17` を差し替える |
| 案内役 | 社内の GitLab の URL に「gitlab」が入らないときは、各自が `git config tazuna.platform gitlab` を実行する。`GITLAB_TOKEN` に read_api のトークンを入れると、MR・issue・CI も見る |

GitHub との違い: MR の説明を直してもパイプラインは動き直さない（「対象要件:」を直したら「Run pipeline」を押す）。CI の承認待ちはない。レポートは MR のメモに書き、同じメモを更新し続ける。

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
