```markdown
---
name: "🤖 AI Agent Task"
about: "AIエージェントに処理を依頼するためのタスク"
title: "[TASK] Refactor: カスタム例外クラスを導入しエラーハンドリングを改善"
labels: 'refactoring, enhancement'
assignees: ''

---

### 課題 (Problem)
現在、`TaskService`内でロック取得に失敗した場合などに汎用的な`Exception`が送出され、API層で一括して`HTTP 503`として処理されています。この実装では、将来的に他の種類のエラーが発生した場合に、原因を特定し、クライアントへ適切なフィードバックを返すことが困難になります。

### 提案 (Proposal)
アプリケーション固有のカスタム例外クラスを定義し、エラーの種類に応じたきめ細やかなハンドリングを実現します。あるべき姿は以下の通りです。

- `domain`または`application`層に、ビジネスロジック上のエラーを示すカスタム例外クラスが定義されている（例: `LockAcquisitionError`, `NoTaskAvailableError`）。
- `TaskService`は、特定の状況に応じてこれらのカスタム例外を送出する。
- `interface/api.py`のFastAPIエラーハンドラが、これらのカスタム例外を捕捉し、それぞれに対応したHTTPステータスコードとエラーメッセージをクライアントに返却する。
- クライアントは、エラーレスポンスに基づき、リトライすべきか、処理を中断すべきかを判断できる。

### 完了の定義 (Definition of Done)
- [ ] `github_broker/application/exceptions.py` が作成され、カスタム例外クラス（例: `LockAcquisitionError`）が定義されている
- [ ] `TaskService`の`request_task`メソッドが、ロック取得失敗時に`LockAcquisitionError`を送出するよう修正されている
- [ ] FastAPIに`LockAcquisitionError`を捕捉して`HTTP 503`を返すカスタム例外ハンドラが実装されている
- [ ] 例外処理の変更に対応するユニットテストが修正・追加されている

---
--- 
**【重要】ここから下はAIエージェントが利用します。変更しないでください。**
---

## ブランチ名
refactor/issue-xx-custom-exception-handling

## 成果物
- `github_broker/application/exceptions.py`
- `github_broker/application/task_service.py`
- `github_broker/interface/api.py`
- `tests/application/test_task_service.py`
```