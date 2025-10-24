# 【Epic】ADR-014: ドキュメント検証規約の改善を実装する

## 親Issue (Parent Issue)
- (なし)

## 子Issue (Sub-Issues)
- (起票後に追記)

## 参照元の意思決定 (Source Decision Document)
- `docs/adr/014-improve-adr-validation-rules.md`

## 実装の参照資料 (Implementation Reference Documents)
- `scripts/validate_docs.py`

# 目的とゴール / Purpose and Goals
ADRとDesign Docの検証規約を改善し、`scripts/validate_docs.py`を修正することで、ドキュメントの品質と一貫性を向上させる。

## As-is (現状)
現在のドキュメント検証スクリプトは基本的なセクションチェックのみで、ドキュメントの品質保証には不十分。

## To-be (あるべき姿)
ADRとDesign Docの公式テンプレートに準拠した、より厳格な検証ロジックが`scripts/validate_docs.py`に実装され、ドキュメントの品質が標準化されている。

## 目標達成までの手順 (Steps to Achieve Goal)

本Epicにおけるタスクの優先度は、Epic > Story > Task の階層で定義されます。数値が小さいほど優先度が高く、EpicはP4、StoryはP1〜P3、TaskはP0〜P2となります。ガントチャートは、この階層と依存関係を視覚的に示しています。

```mermaid
gantt
    title ADR-014 実装計画ガントチャート
    dateFormat  YYYY-MM-DD
    axisFormat  %m/%d

    %% --- Epic: ADR-014 ドキュメント検証規約の改善を実装する (P4) ---
    section Epic: ADR-014 ドキュメント検証規約の改善を実装する (P4)
    全体計画 :crit, 2025-10-27, 7d

    %% --- Story 1: ADR検証ロジックを更新する (P1) ---
    section Story 1: Update ADR Validation Logic (P1)
    ADR必須セクション検証追加      :active, task-1.1, 2025-10-27, 1d, priority 0
    ADR概要正規表現検証追加         :active, task-1.2, after task-1.1, 1d, priority 0

    %% --- Story 2: Design Doc検証ロジックを更新する (P2) ---
    section Story 2: Update Design Doc Validation Logic (P2)
    Design Doc必須セクション検証追加: task-2.1, after task-1.2, 1d, priority 1
    Design Doc概要正規表現検証追加 : task-2.2, after task-2.1, 1d, priority 1

    %% --- Story 3: ドキュメント検証スクリプトのテストを強化する (P3) ---
    section Story 3: Strengthen Doc Validation Tests (P3)
    ADR検証テスト追加  : task-3.1, after task-2.2, 1d, priority 2
    Design Doc検証テスト追加      : task-3.2, after task-3.1, 1d, priority 2
```

1. `Story: ADR検証ロジックを更新する` を行い、ADRの新しい検証ルールを実装する。
2. `Story: Design Doc検証ロジックを更新する` を行い、Design Docの新しい検証ルールを実装する。
3. `Story: ドキュメント検証スクリプトのテストを強化する` を行い、新しい検証ルールが正しく機能することを保証する。

## 完了条件 (Acceptance Criteria)
- このEpicを構成する全てのStoryの実装が完了していること。
- 各Storyの成果物を組み合わせた統合テストが成功し、関連する意思決定ドキュメント（ADR-014）の要求事項をすべて満たしていることが確認されること。

## 成果物 (Deliverables)
- `scripts/validate_docs.py` (更新)
- `tests/scripts/test_validate_docs.py` (更新)

## 実施内容 / Implementation
(子Issueに記載)

## 検証結果 / Validation Results
(子Issueに記載)

## 影響範囲と今後の課題 / Impact and Future Issues
(子Issueに記載)

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `main`
- **作業ブランチ (Feature Branch):** `epic/implement-adr-014`

## Status
Not Created