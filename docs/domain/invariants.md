# 業務の不変条件

どんな変更でも破ってはいけない業務ルール。管理者は社員（CODEOWNERS: business-team）。エージェントは編集できない（hooks で保護）。

各条件には「防ぐ層」と「担保」を書く（`scripts/lint/common/invariant-coverage.sh` が検査する）。

- 防ぐ層: `設計`（型・APIで書けなくする）／`Lint`／`テスト`／`実行検証`／`文章` のどれか
- 担保: その層で守っている仕組みのパス（`文章` 以外は必須、空白区切りで複数可）

`文章` のままの条件は、月次の見直しで上の層に移せないか検討する。

> 以下は見本です。案件では自分の不変条件に置き換えてください。

## INV-001 金額は double / float で扱わない
- 防ぐ層: 設計
- 担保: src/main/java/com/example/domain/Money.java scripts/lint/domain/java-money-no-float.sh
- 理由: 浮動小数点の丸め誤差で、請求額が1円ずれることがある。
- 補足: 金額は `Money` 型で受け渡す。Lint は `Money` を使わずに書かれた箇所を検出する。

## INV-002 請求書の状態は決められた順にしか進まない
- 防ぐ層: 設計
- 担保: src/main/java/com/example/domain/Invoice.java src/test/java/com/example/domain/InvoiceTest.java
- 理由: 状態が戻ると、入金消込の記録と矛盾する。
- 補足: 状態を直接書き換えるセッターを作らず、遷移は専用メソッドだけで行う。
