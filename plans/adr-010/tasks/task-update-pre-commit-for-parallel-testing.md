# Task: Update pre-commit for parallel testing

## 親Issue (Parent Issue)
- Story: Unify and Accelerate Quality Checks

## As-is (現状)
`.pre-commit-config.yaml`の`pytest`フックは、テストをシーケンシャルに実行します。

## To-be (あるべき姿)
`.pre-commit-config.yaml`の`pytest`フックに`-n auto`フラグが追加され、ローカルでのコミット時にテストが並列実行されます。

## 完了条件 (Acceptance Criteria)
- [ ] `.pre-commit-config.yaml`内の`pytest`フックが以下のように更新され、`args`に`-n auto`が追加されていること。
  ```yaml
  -   id: pytest
      name: pytest
      entry: pytest
      args: [-k, "not trio", -n, "auto"]
      language: system
      types: [python]
      pass_filenames: false
  ```

## 成果物 (Deliverables)
- `.pre-commit-config.yaml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/unify-and-accelerate-checks`
- **作業ブランチ (Feature Branch):** `task/update-pre-commit-for-parallel-testing`
