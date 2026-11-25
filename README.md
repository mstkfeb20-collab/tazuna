# tazuna（手綱）

**AI を業務システムに安全に適用するための、設計品質の型。**
ID 設計 → 要件 → AI（GitHub Copilot）による実装 → 単体テストを、設計の1行ごとの ID でつなぐテンプレートリポジトリ。

## なぜ必要か

AI でコードを書く速さは、もう差にならない。差になるのは **業務知識・設計品質・レビュー品質** だ。

「要件を渡して AI が実装し、動いた」で済む開発もある。しかし業務システムでは、**動いたことは正しいことではない。** 正しさは業務ルールどおりかで決まる。そして AI は、

- 書かれていない業務ルールを、もっともらしく補って実装する。もっともらしいので、レビューで止まりにくい。
- 自分が作った文脈のまま、テストを書いて「確かめました」と言う。

設計で決めていないことは、AI がどれだけ速く書いても正しくならない。tazuna は次のことで、この穴をふさぐ。

| 差になるもの | tazuna がすること |
| --- | --- |
| 設計品質 | 決めたことを、設計書に1行1決定・行 ID つきで残す。書くべき項目（約200の設計項目）を型として持ち、抜けを機械で見つける |
| 業務知識 | 決まっていないことを AI に埋めさせない。AI は質問として人に返し、業務の決定は人がする |
| レビュー品質 | 設計の行 → 要件 → テストをたどれるようにし、PR ごとに「どの行を確かめたか」を出す。結合・総合テストは、作る人と試験する人を分けるため、ED・SP から試験チームが別に起こす |

**向いている開発:** 業務ルールが正しさを決めるシステム（SoR）、設計書を書いてレビューする開発
**向かない開発:** PoC・プロトタイプなど、動けば十分なもの

軽くはない。ただし人がやることは、Excel に機能一覧を書く・設計書を書く・AI の質問に答える・PR を承認する、の4つに絞り、残り（転記・追跡・次に何をするかの案内）はツールと案内役が受け持つ。

手綱は、馬が自分で走るのを止めずに方向だけを導く道具。tazuna も同じで、AI に手順を細かく教えるのではなく、**正しい方向へ探索し、自分で検証・修正できる環境**を用意する。人間は業務の決定・完了条件・最終判断を握る。

## 入口はひとつ：「次は何をすればいい？」

使い始めも、途中で迷ったときも、Copilot のチャットで **「次は何をすればいい？」** と聞く（Copilot が使えないときは `python3 scripts/report/next.py`）。案内役（スキル `base-navigator`）がリポジトリと GitHub（または GitLab）の状態を読み、止まっているものから順に、誰が・何を・どうやって進めるかを示し、一緒に進める。このページや `harness/` の資料は、案内の中で必要になったときに開けばよい。

案内する範囲は次のとおり。tazuna の範囲は**単体テストまで**で、結合・総合テストは、作る人と試験する人を分けるため、ED・SP から試験チームが別に起こす。

```
立ち上げ → 機能一覧 → 書類一覧 → 設計書のひな形 → 設計書 → 転記 → issue → 実装 → マージ → 結合テストへ引き渡す
                                     ▲                                                          │
                                     └──────────── 不具合の issue（原因を切り分けて戻す） ◀────────┘
```

## 何が入っているか

```
repo-root/
├─ AGENTS.md                     # エージェントが常に読む索引（60行以内）
├─ .github/
│  ├─ CODEOWNERS                 # パスごとの承認者
│  ├─ pull_request_template.md   # 実行結果と証拠の欄
│  ├─ ISSUE_TEMPLATE/bug.md      # 不具合（結合・総合テストなどから戻す入口）
│  ├─ skills/
│  │  ├─ base-navigator/         # 案内役：次に何をするか（入口）
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
│  │  ├─ ID設計.xlsx             # 原本。機能一覧（人が書く）ともとになる設計書の行 → 書類一覧・進捗・進め方のシート・網羅状況（自動）、型（書類の種類・記載項目・設計項目）
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
   ├─ design-and-transcription.md # 設計書と転記先の違い・1行がどこへ移るか（人向け）
   ├─ rule-log.md                # 違反の記録
   └─ metrics.md                 # 月次の指標
```

考え方と運用のルールは [harness/GUIDE.md](harness/GUIDE.md) を参照。設計書に何を書き、要件・テスト仕様・作業一覧にどう渡るかは [harness/design-and-transcription.md](harness/design-and-transcription.md)。

## ID 設計から実装までの進め方

| 段階 | すること | コマンド（人が実行） | 承認 |
| --- | --- | --- | --- |
| 準備 | `ID設計.xlsx` の「進め方」シートの 1〜5：何を作るか（書類の種類の「状態」と「もと」）と何を書くか（記載項目の「記載」）を決め、機能一覧に外部設計で決まっている範囲を書き、書類一覧を作って書く・書かないを決める。テーブル設計書は、データモデル設計書（S-20）のテーブル一覧に行を書くと1枚ずつできる | `id_design.py list` → `id_design.py scaffold` | 社員 |
| ① 設計 | ひな形の見出しの下に1行1決定事項を `- [番号] 本文` で書き（番号は見出しの中で付け、振り直さない）、書類ごとに PR でレビューする | — | 社員 |
| ② 要件を決める | 機能の資料がそろったら転記し、要件とテスト仕様を PR で決める | `transcribe.py` | 社員 |
| ③ 実装 | 要件とテスト仕様からテストと実装を書く。PR に `対象要件: REQ-xxx` を書く | — | 案件リーダー |
| ④ マージ | Lint と CI（対象要件にテストがあるか）を通してマージする | — | — |
| ⑤ 引き渡し | すべての要件にテストがあれば、単体テストで確かめていないテスト仕様の行（PR で「未対応」とした行）を試験チームに渡す。結合・総合テストはここから先（tazuna の範囲外） | `next.py` | 社員 |
| 不具合 | 結合・総合テストなどで見つかった不具合は、issue のテンプレート「不具合」で書いてもらう。原因区分（設計・転記・実装・ハーネス）を決めて、設計書・転記ツール・実装・ハーネスのどこを直すかを分ける | — | 社員 |

進み具合は `git fetch` の後に `python3 scripts/design/id_design.py progress` で（統合先のブランチと比べて「完了」を決める。既定は GitHub の既定のブランチで、`--base origin/develop` や環境変数 `TAZUNA_BASE_BRANCH` で変えられる） `ID設計.xlsx` の進捗・網羅状況シートに出る（未着手・執筆中・レビュー中・完了・要転記、要件ごとの未実装・テストあり）。Excel を直したら `id_design.py export` で書き出し（`ID設計.md`）も作り直し、一緒にコミットする。Excel を読むコマンドには `pip install openpyxl` が要る。 書類の種類の「もと」は、何が決まるとその書類が1枚ずつできるか（機能一覧の列か、設計書の見出しの行）。手順と書類ができる前後関係は「進め方」シートにある（ツールが作る）。Excel の列は、誰が埋めるかで色を分けている（黄: 人が書く・決める、緑: 型の値だが案件で変えてよい（書類の種類の「状態」、記載項目の「記載」）、灰: ツールが作る、青: 型で変えない）。先頭の「凡例」シートに意味と進め方がある。色が崩れたら `id_design.py paint` で付け直す。

### 次に何をするか（案内役）

Copilot のチャットで「次は何をすればいい？」と聞くと、スキル `base-navigator` が `python3 scripts/report/next.py` で状態を読み、止まっているものから順に、誰が・何を・どうやって進めるかを案内して一緒に進める。立ち上げが済んでいないファイル、CI の承認待ち、Copilot の質問、不具合の issue、レビュー待ちの PR、転記が要る設計書、issue のない要件、必須の見出しが空の設計書、機能一覧と書類一覧のずれを見る。すべての要件にテストがあれば、結合テストへの引き渡しを出す。

PR・MR の「レビュアーに判断してほしいこと」の質問には、上から 1, 2, 3… と番号が付く。答えた人は本文を直さず、コメントに「回答: 1」（いくつかなら「回答: 1, 3」、今は決められないものは「保留: 2」）の行を書く。Copilot が作った PR の本文を人が編集すると、Copilot が本文（対象要件・未対応・設計書から）を書き換えなくなり、CI とレポートがずれるため。`--issue REQ-xxxxx` で要件を実装する issue の下書きを出す。業務の決定・承認・マージは人がする。

### 開発期間のレポート

- **PR 単位:** CI が PR にコメントする（`scripts/report/report.py pr`）。対象要件ごとに、テスト仕様の行がテストで確かめられたか（テストに付けた `@Tag("S-26-xxx/D-xxxxx/n")` を数える）、作業一覧の行のうち PR の本文に「未対応: 行ID（理由）」と書いたもの、「設計書から: 行ID（理由）」と書いた設計書の行（転記先にあるか、ないか）、テストと Lint の結果、保護ファイルに触れていないかを出す。
- **日次:** `.github/workflows/tazuna-report.yml` が平日の朝に、統合ブランチごとの issue「日次レポート（ブランチ名）」にコメントする。状態が変わった書類、新しく決まった要件、テストありになった要件、コミットを出す。対象はリポジトリの変数 `TAZUNA_REPORT_BRANCHES`（空白区切り、既定は `develop`）。main を商用リリース版にする運用では main を対象にしない。

### 設計書の書き方の決まり

- 書類の種類の番号（S-xx）は意味を持たない。共通か機能別かは「区分」、機能の中心の書類（処理設計書）とテスト仕様の書類は「役割」の列で決まる。使わなくなった種類は「状態」を「廃止」にする（番号は再利用しない）。
- 図（Mermaid など）や表は、それを説明する行「- [n] 本文」の直下に2文字字下げして書く。行と一緒に転記される。どの行にも付いていない図は Lint（COMMON-007）で止まる。
- テーブル・列の正は DDL（`db/schema/*.sql`）。全テーブル・全列に説明（COMMENT）を書き、値の範囲は CHECK 制約で書く。区分値の列の説明には、値の意味を決めたコード定義書の行（例 `S-15-001/D-05005/1`）を書く（Lint COMMON-010）。エンティティと関連（ER 図）と正規化の方針はデータモデル設計書（S-20）、DDL に書けない決定（保持期間・データ量・索引の理由など）はテーブル設計書（S-16）に書く。
- どのテーブルを作るかは、データモデル設計書（S-20）の「テーブル一覧」（D-05020）に1行1テーブルで書く（行の先頭に物理名）。テーブル設計書（S-16）はこの行ごとに書類一覧にでき、DDL に書けない決定（インデックスの理由・データ量・保持期間など）だけを書く。DDL は一覧の行ごとに `db/schema/<テーブル>.sql` を書く。一覧にあって DDL がないもの、DDL があって一覧にないもの、処理設計書の CRUD（D-05006）に出てくる名前が一覧にも DDL の列にもないものは Lint（COMMON-007）が警告する。設計書レビューの材料（`review_pack.py`）には、テーブルごとに CRUD の行を逆引きした一覧が出る。

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
要る変数・ツールの一覧は「[必要な環境と設定](#必要な環境と設定)」。
- main ブランチを保護し、CI（`verify`）の成功と CODEOWNERS のレビューを必須にする。
- ラベル「不具合」を作る（issue のテンプレート「不具合」が付ける。案内役はこのラベルか、タイトルの【不具合】で見分ける）。
- hooks は既定ブランチにある設定だけが Copilot cloud agent に読み込まれる。

### 5'. GitLab で運用するとき
tazuna は GitLab でもそのまま使える。CI は `.gitlab-ci.yml`、MR のテンプレートは `.gitlab/merge_request_templates/Default.md` にある（GitHub 用のファイルと並べて置いてよい。互いに読まない）。

**エージェントは手元で動かす。** Copilot のクラウドエージェントは GitHub 専用なので、作業する人が VS Code の Copilot（エージェントモード）で issue を実装し、MR を出す。`AGENTS.md`・`.github/skills/`・`.github/hooks/` は、リポジトリの置き場所に関係なく VS Code の Copilot が読む（hooks は VS Code ではプレビュー。各自の PC に bash と jq が要る）。

| 設定 | やること |
| --- | --- |
| CI/CD の変数 | `TAZUNA_GITLAB_TOKEN`（プロジェクトのアクセストークン。ロール Reporter 以上・スコープ api・マスクする）。MR の説明の読み取りと、レポートの書き込みに使う。日次レポートの対象を変えるなら `TAZUNA_REPORT_BRANCHES` |
| 日次レポート | Build → Pipeline schedules に平日の朝の予定を作り、変数 `TAZUNA_DAILY_REPORT=1` を付ける |
| ブランチの保護 | main（と develop）を保護し、Merge requests の「Pipelines must succeed」を有効にする |
| ラベル | 「不具合」を作る（issue のテンプレート「不具合」が付ける） |
| 承認者 | `.github/CODEOWNERS` を `.gitlab/CODEOWNERS` に移し、`@your-org/...` を GitLab のグループに置き換える（必須の承認にするには Premium 以上の「Code Owner approval」） |
| Runner | Docker で動く Runner が要る。社内のレジストリを使うなら、`.gitlab-ci.yml` の `python:3.12`・`maven:3.9-eclipse-temurin-17` を差し替える |
| 案内役 | 社内の GitLab の URL に「gitlab」が入らないときは、各自が `git config tazuna.platform gitlab` を実行する。`GITLAB_TOKEN` に read_api のトークンを入れると、MR・issue・CI も見る |

GitHub との違い: MR の説明を直してもパイプラインは動き直さない（「対象要件:」を直したら「Run pipeline」を押す）。CI の承認待ちはない。レポートは MR のメモに書き、同じメモを更新し続ける。

## 必要な環境と設定

### 手元（人のPC）に要るもの

| もの | 使うところ | 備考 |
| --- | --- | --- |
| git・bash | すべて | Windows は Git Bash か WSL |
| Python 3（CI は 3.12） | Lint・ID 設計・転記・案内役・レポート | |
| `openpyxl`（`pip install openpyxl`） | Excel を読み書きするコマンド（`id_design.py`） | Lint と案内役は書き出し（`ID設計.md`）を読むので要らない |
| Java 17・Maven | `mvn -B verify` | `pom.xml` の `maven.compiler.release` と合わせる |
| `gh`（GitHub CLI）と `gh auth login` | 案内役が PR・issue・CI を見るとき（GitHub） | なければ `next.py --local` で、手元のファイルだけを見る |
| `jq` | hooks（VS Code の Copilot で動かすとき） | GitHub 上の Copilot では用意されている |

### GitHub の設定

ワークフローは GitHub が渡すトークン（`github.token`）を使うので、シークレットの登録は要らない。

| 種類 | 名前 | 内容 | 既定 |
| --- | --- | --- | --- |
| リポジトリの変数（Actions → Variables） | `TAZUNA_REPORT_BRANCHES` | 日次レポートの対象のブランチ（空白区切り） | `develop` |
| ラベル | `不具合` | issue のテンプレート「不具合」が付け、案内役が見分ける | — |
| ブランチの保護 | main（と develop） | CI（`verify`）の成功と CODEOWNERS のレビューを必須にする | — |

### GitLab の設定

| 種類 | 名前 | 内容 | 既定 |
| --- | --- | --- | --- |
| CI/CD の変数 | `TAZUNA_GITLAB_TOKEN` | プロジェクトのアクセストークン（ロール Reporter 以上・スコープ api）。「マスクする」で登録。MR の説明を読み、レポートを書く | 必須 |
| CI/CD の変数 | `TAZUNA_REPORT_BRANCHES` | 日次レポートの対象のブランチ（空白区切り） | `develop` |
| パイプラインのスケジュールの変数 | `TAZUNA_DAILY_REPORT=1` | 平日の朝のスケジュールに付けると、日次レポートだけを動かす | — |
| ラベル | `不具合` | issue のテンプレート「不具合」が付ける | — |

### 手元で使う環境変数・設定（必要なときだけ）

| 名前 | 使うところ | 内容 |
| --- | --- | --- |
| `GITLAB_TOKEN`（または `TAZUNA_GITLAB_TOKEN`） | 案内役（GitLab） | read_api のトークン。入れると MR・issue・CI も見る |
| `git config tazuna.platform gitlab`（または `TAZUNA_PLATFORM`） | 案内役 | origin の URL に「gitlab」が入らない社内の GitLab で、GitLab だと教える |
| `TAZUNA_GITLAB_URL` | 案内役・レポート（GitLab） | GitLab の URL が origin のホストと違うとき（ポートやパスがあるときなど）に、`https://gitlab.example.co.jp` の形で指定する |
| `TAZUNA_GITLAB_CA_FILE` | 案内役（GitLab） | 社内の認証局の証明書のファイル。CI では Runner が渡す `CI_SERVER_TLS_CA_FILE` を読む |
| `TAZUNA_BASE_BRANCH` | 進捗（`id_design.py progress`） | 「完了」を決めるときに比べるブランチ（例 `origin/develop`）。既定は既定のブランチ |
| `TAZUNA_REMOTE_URL` | 型の取り込み（`tazuna-update.sh`） | tazuna の取り込み元（社内の GitLab のミラーなど） |
| `TAZUNA_TEST_DIRS` | Lint・レポート | テストのフォルダ（空白区切り）。既定は `src/test tests` |

`TAZUNA_ROOT`・`TAZUNA_PR_BODY`・`TAZUNA_IS_PR`・`TAZUNA_TARGET_REQS` などは、CI と自己テストがツールに渡すためのもので、設定しなくてよい。

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
- **ID 設計の Excel（`docs/design/ID設計.xlsx`）と書き出し（`ID設計.md`）は上書きしない。** 型（書類の種類・記載項目・設計項目）と、案件が書いたもの（機能一覧・書類一覧・状態・記載）が1つのファイルにあるため。型が変わったタグでは、新しい Excel と、前のバージョンからの型の差分を `.tazuna-download/`（コミットされない）に取り出すので、必要な行を案件の Excel に手で反映し、`id_design.py export` と `paint` を実行する。新しいツールが型の新しい列や項目を前提にしていることがあるので、取り込みの PR で一緒に反映する。
- Excel だけを見たいときは `scripts/tazuna-update.sh --id-design v0.2.0`（何も上書きしない）。
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
