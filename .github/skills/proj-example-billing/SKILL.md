---
name: proj-example-billing
description: 【見本】請求（Invoice・Money）に関わる機能を実装・レビューするときに使う。案件では、このスキルを自分のドメインに合わせて書き換えるか削除する。
---

# 請求ドメインの進め方（見本）

> これは proj- スキルの書き方の見本です。案件では削除するか、自分のドメインのスキルに置き換えてください。

進め方の基本は `base-task-workflow` に従う。ここには請求ドメインに特有のことだけを書く。業務ルールそのものは書かず、`docs/domain/` を参照する。

## 請求ドメインで特に確認すること

- 金額は必ず `com.example.domain.Money` を使う（INV-001）。
- 請求書の状態は `Invoice` の遷移メソッドでだけ変える（INV-002）。新しい状態を追加するときは、遷移表を `docs/domain/feature-map.md` に先に書き、承認を得てから実装する。
- 税計算の端数処理は REQ-001 に従う。端数処理を変える要件が来たら、既存テストを書き換える前にレビュアーに確認する。

## 参照先

- 業務ルール: `docs/domain/invariants.md`
- 用語: `docs/domain/glossary.md`（請求書、確定、支払済）
- 機能一覧: `docs/domain/feature-map.md`
