# Task: Add pytest-xdist dependency

## 親Issue (Parent Issue)
- Story: Unify and Accelerate Quality Checks

## As-is (現状)
プロジェクトのテストは並列実行されておらず、テストスイートの実行に時間がかかっています。

## To-be (あるべき姿)
`pytest-xdist`が依存関係に追加され、テストを並列で実行する準備が整っています。

## 完了条件 (Acceptance Criteria)
- [ ] `pytest-xdist`が`pyproject.toml`の`[tool.poetry.group.dev.dependencies]`セクションに追加されていること。

## 成果物 (Deliverables)
- `pyproject.toml`

## ブランチ戦略 (Branching Strategy)
- **ベースブランチ (Base Branch):** `story/unify-and-accelerate-checks`
- **作業ブランチ (Feature Branch):** `task/add-pytest-xdist-dependency`

## 担当エージェント (Agent)
- BACKENDCODER

## 優先度 (Priority)
- P0

# Issue: #1458
