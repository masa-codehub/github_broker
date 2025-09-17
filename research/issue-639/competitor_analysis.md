## 調査報告書：【Story】競合ポジショニング分析

### 1. 調査サマリー (Executive Summary)
本調査では、主要なAIコーディングアシスタントであるGitHub Copilot、Cursor AI、Tabnine AIの競合分析を実施しました。各プロダクトは、コード補完、生成、デバッグ支援といった共通機能に加え、それぞれ異なるターゲットペルソナと強みを持つことが明らかになりました。GitHub Copilotは幅広い開発者と組織を対象に包括的なAI支援を提供し、Cursor AIはVSCodeベースの統合開発環境でコードベース全体を理解するAIエージェント機能に注力、Tabnine AIはプライバシーとローカル学習を重視するプロフェッショナル開発者および企業に特化しています。

### 2. 調査目的と仮説 (Purpose & Hypothesis)
- **目的:** 主要な競合プロダクトを特定し、それらがどのペルソナの、どの課題（Jobs-to-be-Done）を解決しているかを分析する。この分析を通じて、市場における我々のプロダクトのユニークなポジショニング（独自性）を発見し、戦略的な示唆を得ることを目的とする。
- **仮説:** AIコーディングアシスタント市場は、コード補完や生成といった基本的な機能では差別化が難しくなっており、コードベースの理解度、プライバシー、チーム連携、特定の開発ワークフローへの統合といった点で各社が独自のポジショニングを築いているのではないか。

### 3. 調査プロセス (Methodology)
- **調査期間:** 2025-09-16
- **主な情報源:** Google検索、各プロダクトの公式サイト、技術ブログ、ユーザーレビューサイト（G2など）、SNS（Xなど）
- **主な検索キーワード:** 「(製品名) ターゲットペルソナ」「(製品名) 解決課題」「(製品名) 主要機能」「(製品名) 価格戦略」「(製品名) ユーザーレビュー」

### 4. 調査結果 (Findings)

#### 【競合プロダクトのターゲットユーザー分析】

- **《競合A: GitHub Copilot》**
  - **想定ペルソナ:** 個人開発者、チーム・中小企業、大規模組織・エンタープライズ、学生・教職員。幅広い開発者をターゲットとし、特にGitHubエコシステムとの連携を重視するユーザー。
  - **ユーザーが熱狂している点:**
    - 開発効率の劇的な向上と、反復作業の削減。
    - 実装者が本質的な問題解決に集中できる環境を提供。
    - 包括的なAI支援機能（チャット、編集、PR要約など）。
  - **根拠となる発言/レビュー:**
    - > 「多くのエンジニアがCopilotなしの生活に戻れなくなっていると回答しており、その効果を実感しています。」
    - 出典: https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGMtzkhkfqde1YOWDC4CVWGIdUIApGIGRAUjj7wCjJkIezFWJKxP1B_ckdLdb0W1FKGP1UEAwGoiq-MZHz0ior1V8keszyipoeRoJKglXZQAw4Ic25qLRsx9X8elaGsz1hXCH6SZ4MHDfNU8sung==
  - **解決している課題:** 開発効率の向上、反復作業の削減、デバッグと構文修正、コードの理解と説明、品質と一貫性の維持、学習支援。
  - **主要な機能:** コードの自動補完、Copilot Chat、Copilot Edits、Agent Mode、コードレビュー、コミットメッセージ生成、Pull Requestの要約、Copilot Spaces、Copilot ナレッジベース (Enterpriseのみ)、CLIでの補完、多数の言語とIDEに対応。
  - **価格戦略:** Copilot Free (個人向け、制限付き)、Copilot Pro (個人開発者向け、月額10ドル/年額100ドル)、Copilot Business (チーム・中小企業向け、ユーザーあたり月額19ドル)、Copilot Enterprise (大規模組織・エンタープライズ向け、ユーザーあたり月額39ドル)。学生・教職員は無料。

- **《競合B: Cursor AI》**
  - **想定ペルソナ:** AIを活用してコーディング効率を向上させたい開発者、VSCodeの使い慣れたインターフェースを維持しつつAI機能を統合したいユーザー、大規模なコードベースや複雑なプロジェクトに取り組む開発者、プログラミング初心者から経験豊富なプロ開発者まで、個人開発者からチーム、企業まで。
  - **ユーザーが熱狂している点:**
    - VSCodeベースの使い慣れた環境でAI機能を統合できる点。
    - コードベース全体を深く理解し、複数ファイルにわたる大規模な修正やタスクをAIに任せられるエージェント機能。
    - 自然言語での指示によるコード生成・編集。
  - **根拠となる発言/レビュー:**
    - > 「VSCodeをフォークしているため、使い慣れたインターフェースでAI機能を利用できる点が評価されています。」
    - 出典: https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHP0X5YtcWKVKP09ms-j75RXSicTrTbbMIsRzQUiZwu9KcoUUX34h2CYn-tqmTPBn15I-q86eMKPadIyJFLu-2bJl_-pKAHhfd-69_Or5P2wPJBEyBjfg4WM6RHtCjJPRIh
  - **解決している課題:** コーディング時間の短縮と効率化、バグの検出と修正、コードベースの理解とナビゲーション、複雑なタスクの自動化、学習とスキル向上、反復作業の削減、コンテキスト切り替えの削減。
  - **主要な機能:** AIチャット機能 (Chat)、Composerモード、コード生成・編集 (Command K)、コード自動補完 (Copilot++)、自動デバッグ (Auto-Debug) & エラー修正 (Fit Lints)、ファイル参照 (@Symbols)、コードベース分析 (Codebase Answers)、エージェント機能、ドキュメント管理 (Docs)、Webアクセス対応、ターミナル操作支援、画像参照機能。
  - **価格戦略:** Hobbyプラン (無料、月間200回までのClaude, Gemini, GPT-4oo利用)、Proプラン (月額20ドル程度、無制限のTab補完、Bugbot、最大コンテキストウィンドウ、プレミアムモデル利用)、Ultraプラン (Proより上位の個人向け)、Teams / Enterpriseプラン (チーム・企業向け)。

- **《競合C: Tabnine AI》**
  - **想定ペルソナ:** プロフェッショナルな開発者、開発チーム、セキュリティとプライバシーを重視する企業。特に、コードが外部に送信されることへの懸念を持つユーザー。
  - **ユーザーが熱狂している点:**
    - ローカル学習機能により、個人やチーム固有のコーディングパターンを学習し、コードが外部に送信されないプライベートな環境でのコード処理。
    - 高精度なAI駆動のコード補完と、50以上のプログラミング言語への対応。
    - エンタープライズ向けのオンプレミス、VPC、エアギャップ環境での展開サポート。
  - **根拠となる発言/レビュー:**
    - > 「GitHub Copilotと比較して、より強固なプライバシー保護やエンタープライズ向けのオンプレミス対応、カスタムモデルのトレーニング対応が強みとして挙げられています。」
    - 出典: https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeDEHeMVwgD4QxyC80aEbQAgdIYxzdnN1UHGJj9vkZangEnncF7-FNRae8H2pD8WUJRgZfRzTGOK2u1VdaeGfu7-QH3wcku_2IWeU-zyNXYjzsdscc3pIx4BMzFD7PtYejjfl9hQrnebqELQ==
  - **解決している課題:** 開発速度の向上、コード品質の改善、学習コストの削減、コードレビュー時間の短縮、エラーの検出と修正、セキュリティとプライバシーの確保。
  - **主要な機能:** AI駆動のコード補完、ローカル学習・プライベート機能、Tabnine Chat、AIエージェント機能、主要なIDEに対応。
  - **価格戦略:** 無料プラン、PRO版 (月額12ドル)、Enterprise版。

#### 【ポジショニングマップ】

AIコーディングアシスタント市場における主要競合プロダクトのポジショニングを、以下の軸で視覚化します。

- **横軸: コードベース理解の深さ/コンテキストの広さ (狭 → 広)**
    - 単一ファイル・行レベルの補完から、プロジェクト全体、組織独自のナレッジベース、Web検索まで。
- **縦軸: AIによる自動化の度合い (低 → 高)**
    - コード補完のみから、コード生成・編集、複数ファイルにわたる大規模な修正、エージェント機能まで。

```
高
^
|
|   Cursor AI (プロジェクト全体、エージェント機能、VSCode統合)
|   GitHub Copilot (幅広い開発者、GitHubエコシステム、組織ナレッジ)
|
|
|   Tabnine AI (プライバシー重視、ローカル学習、エンタープライズ対応)
|
+---------------------------------------------------------------------> 広
狭                                                                    (コードベース理解の深さ/コンテキストの広さ)
```

### 5. 分析と洞察 (Analysis & Insights)
- **仮説の検証結果:** 当初の仮説「AIコーディングアシスタント市場は、コード補完や生成といった基本的な機能では差別化が難しくなっており、コードベースの理解度、プライバシー、チーム連携、特定の開発ワークフローへの統合といった点で各社が独自のポジショニングを築いているのではないか」は、本調査結果によって支持されました。各プロダクトは、基本的なAIコーディング支援を提供しつつも、それぞれ異なる強みとターゲット層を持っていることが明確です。
- **顧客が解決したいジョブ(Jobs-to-be-Done):**
    - **開発効率の向上:** コード記述の高速化、反復作業の自動化、デバッグ時間の短縮。
    - **コード品質の維持・向上:** 一貫性のあるコード、バグの少ないコード、リファクタリング支援。
    - **コードベースの理解:** 大規模なプロジェクトや新規参入時のコード理解の促進。
    - **学習支援:** 新しい技術や言語の習得を効率化。
    - **セキュリティとプライバシーの確保:** 機密性の高いコードを安全に扱う。
    - **チーム連携の強化:** チーム内でのコード共有、レビュー、ドキュメント作成の効率化。
- **顧客ロイヤルティへの影響:**
    - **GitHub Copilot:** GitHubエコシステムとのシームレスな連携と、幅広い開発者層への対応がロイヤルティを高めている。特に、GitHub Enterpriseユーザーにとっては、組織ナレッジベースとの連携が大きな価値となる。
    - **Cursor AI:** VSCodeユーザーにとっての移行の容易さと、コードベース全体を深く理解するAIエージェント機能が、生産性向上を求める開発者のロイヤルティを獲得している。
    - **Tabnine AI:** プライバシーとセキュリティを最優先する企業や開発者にとって、コードが外部に送信されないローカル学習機能とオンプレミス対応が決定的な差別化要因となり、高いロイヤルティに繋がっている。
- **競合のSTP分析:**
    - **GitHub Copilot:**
        - **セグメント:** 個人開発者から大規模エンタープライズまで、幅広い開発者。特にGitHubユーザー。
        - **ターゲティング:** 開発者の生産性向上とGitHubエコシステム内での包括的なAI支援。
        - **ポジショニング:** 「GitHubと最も深く統合された、包括的なAIペアプログラマー」。
    - **Cursor AI:**
        - **セグメント:** VSCodeユーザーで、AIによるコードベース全体の深い理解とエージェント機能を求める開発者。
        - **ターゲティング:** VSCodeの使い慣れた環境で、AIによる大規模なコード修正やタスク自動化を実現したい開発者。
        - **ポジショニング:** 「VSCodeベースで、コードベース全体を理解し、複雑なタスクを自動化するAIネイティブな開発環境」。
    - **Tabnine AI:**
        - **セグメント:** セキュリティとプライバシーを重視するプロフェッショナル開発者、開発チーム、企業。
        - **ターゲティング:** コードの機密性を保ちつつ、AIによる高精度なコード補完とチーム固有の学習を求めるユーザー。
        - **ポジショニング:** 「プライバシーとセキュリティを最優先する、オンプレミス対応のAIコーディングアシスタント」。
- **結論と戦略的インサイト:**
    - AIコーディングアシスタント市場は成熟しつつあり、単なるコード補完や生成だけでは差別化が困難。
    - 我々のプロダクトがユニークなポジショニングを築くためには、以下のいずれかの方向性を強化する必要がある。
        1.  **特定の開発ワークフローへの深い統合:** GitHubエコシステムに特化し、Issue管理、PR作成、レビューといった一連のワークフローをAIでシームレスに自動化・最適化する。
        2.  **特定のペルソナへの特化:** 例えば、特定のプログラミング言語やフレームワークに特化し、その分野でのAI支援を極める。
        3.  **セキュリティ・プライバシーの強化:** Tabnine AIのように、コードの機密性を重視するユーザー層にアピールする。
        4.  **コードベース理解の深化とエージェント機能の拡張:** Cursor AIのように、プロジェクト全体のコンテキストを理解し、より複雑なタスクを自律的に解決できるエージェント機能を提供する。
    - 我々のプロダクトはGitHub Task Brokerとして、GitHubのIssue管理と連携し、エージェントにタスクを割り当てることに特化している。この強みを活かし、**「GitHubのIssueを起点とした開発ワークフローをAIで自動化・最適化する」**というポジショニングをさらに強化することが戦略的に有効である。具体的には、Issueの背景や完了条件を深く理解し、適切なブランチ作成、コード生成、テスト生成、PR作成、レビュー依頼までを一貫して支援するAIエージェントの能力を向上させるべきである。

### 6. 参照情報 (References)
- GitHub Copilot:
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQERWFls4ZOo3pIOt2dJ7pHR32iEfBRKAPN-YOq1ErIgFPpHQdRw-QwGJ1ne6Lu-WR2IiJZGlJ676yzmB5O3osju6vI-tO39iNsIgnLRZfqC25acHYwTtoHeJUVVjp-4oHVHApM-Cw==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQErBxsz17wPhY-o9PEXZFvnGE8giir-COViIydV3x3l5_766ZT1hM-dWfzhe1ceoiBCK8S33L8-o40yREpY1CXs3QI0_UH9c2NqL6zF67yDv36DSgam3s9FG3fDSOCRJ877rqQG9XaE)
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGF7FvjZV0vOhFzKqbkvxHFYMMSLv8KOQ-NuzwXvx-NJgCd9W-DxIVPyBSKuc_s1hmioUS5mjBdPS_bF1V53LlWokEwMnscPxhAzFOBN7D0AfjZWKjlIBirso0IAK9Zv1Fa4Ap-x1bte7Ay4Rd3IA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFX9JGtUWpeIupHDDZ5gNuqCiarxlpxm-COB_JCQNAcL2Yr1NGpQUgpAAKsdCsQrawWAa0PGjPvB7f4UOhCvbS2O4BQ9mOWB24Glt26G-n-oyVxx5DgEFoI-Y8jd_MTZwZZEHg-7SA7FQ==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5bqtVVPQivoLgNlPfcKZnXNjK2uYH5D2LXtzXChyzxrvHr9dBRVGEboGgWSgHISaIzdFGhDxhqeToIU9HlIuer43BOGTqhKY2sjHt63kkEiCuGUIm51QtVYZCdvlLPNaTLjdJbWJtVqntDHJpC2bezc=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzz_yp_wRLC0abSgJ4nH6JMCEVxU0VXH9QUfHoyHvntFz78woXiMNN50YWp2dLoLRYQSZAPx-Vt2PByP3SqkpCr7ouhQUt8va3AUweLw06E00T1R6nFEXAXmATheONnacAxiuAFrHLVWVTtk77nXWMkGZb5Q865vQRaxY=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFe-wxdIPi3nbLrh7_tAfI-KWvz_dvDFGNrWzxiTxZaWj7vJhv9hJQBVhlTsDHCzxn1A295TXYNY6lXNgEFkvi-xfGScxFKng2uuMTaLLeqen-qU1eoUUn08mmymVaE6BTxOKh1x83qa1g3aP0kme8=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFpTr-1ZCyXn1lJhTF6_huInbGyW3ET6taqxwhn9gLF4Tej5QZedNoD1dCW83dwzj3llsOHhVQRgmYfzCl-7sVWULXYEYiNp_goyLng_yBeR02n029xRFiasEruPx9HCcT5BhPu4oiqsVfRQekC
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE2sr5inU4x3EUpWeVIPkKQSmSF5QIE8f0e_NwQ_TvmoxeZ52HTjT-A_dyCe7xrsgF4a8cryV8Pn2VPjTIEjf2g2H1z3mCed3YV4m93K-vHg0lsKE6UMzMgxaxR_q89v4I6JTXZNGJ3zjBDYbMF1FJJFfMovZj3QIyBhBfO_7m-9J_cqgjGKcJnLQXi3O5splA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHMIJfb1K02wV5Nb3pLtO_jCaS2zj2_Br5oR8kLvBoSsed7mm7x4Jeu2jydZe-6UFeAAIGoo6cxvRBiymQEE-XKyGWqdcz_nHcfA4xJ6eJvif4tL4VQNpldQaw53qc_EA9m0QGHpg7IhjzjQHGWPWMRuEuWfA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFdFBSu0i61lkWmF1JJB8uaJeJMVAuvQrHWKT8jlholRygg-h2_PTsB_R47Y_OlsYmGXB4Fnz8gx9hLylRsEVbuCfUkemhMK3fyi4bgZS6OdH2PPTgM54apiasDlLIuYeBG4mCwLjbTqaC7RZP7875U8Eq1GgMLKNAL6RNuvPA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFNEpzZ3NrzoyG7MWx_dVapaX3P_tWM2_cnBDtBRvCVgLhVOrFIQYE4cIwx0YaIiBA5RfaHs1A8BNLjYK-2JuSLR3gLwduczOgQQcmuNctoMRWYV3Rn-GjbjUBOyCxyiVYS0fAG0o8qIhKokIwgpvCo_xTmrI1ItHi6KA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEpaBu2pLOv0hM4pPomJq9kaM8Jsv9sv-atupXUpbG9w-lCKjArP8sf4XoNUTAskwARsRfHTiC10rIprUrGN-49BHHHADQWELOeL0IQtDO7UrBwJ2BdeTrMUvXIyRTZpn3A9reoNdO0agnxTOv1u1vKPZiUxehmZvOl9hFxQrPVIc1KQBVimJ-qASBQhBK1
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGMtzkhkfqde1YOWDC4CVWGIdUIApGIGRAUjj7wCjJkIezFWJKxP1B_ckdLdb0W1FKGP1UEAwGoiq-MZHz0ior1V8keszyipoeRoJKglXZQAw4Ic25qLRsx9X8elaGsz1hXCH6SZ4MHDfNU8sung==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG1O4O7om8Q40xcr8kKfMvPs8uu4cHNatO7BrWbiUVy-nWrc9BJVLfyhpFCOKZkOoRkIzlDjA3cwLPT8Cg294VQHI5YKkxm0S4NlJmR8WAFn-l3kyNW6LrsI0ydKTXFa8Dnjw==
- Cursor AI:
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdDi3-Iexw0SwDYCS8ZF7EXdzr_8XtMi6CtsdL29psGdS--qTtElXIUts2YjXDDFoQwBx_nFWzzD1KrX5xieIRYkaYvaxe3snAIKUo7xF-uzrZn4bIx7V2NdgP7I2TlV9K2JUD0YT2XkRi4oLjx6eumMps6euGlvM=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEyJO2Hf_1yf_86Ho3t4DjegaQj15SjvzuiBgLcGQo9to-NoR3f3YEUcB8UIHLts_m_ENdBEW1lADxynauQRRW1DU2-pvqU1qJzr_Rpn1hCbKOW7cyUv_yh
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9tjpTgv7iVWBwpLjDisfeSaqKKxriUcB452c9eQrR5YvOk3_BjKRCmrrW1IqlnmDbvRIfaNN45F_s55jwlAavHvCpf3hSFBo3eiraZrVHgmyi32Et-OAfB1cys8bRYL_sF6aM
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHP0X5YtcWKVKP09ms-j75RXSicTrTbbMIsRzQUiZwu9KcoUUX34h2CYn-tqmTPBn15I-q86eMKPadIyJFLu-2bJl_-pKAHhfd-69_Or5P2wPJBEyBjfg4WM6RHtCjJPRIh
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQET49uBii6QEi8SL2S1uSkQhbUlpDNoUGNaRDfTskdj7PyC4WBaGbGQPVj9WwtCYYNpJ6fBsCVVg1LF1z_RKWVmPbON3HooFY5vMoNznn0_mJpStWI0Jhf8DR566JnQ5UL2oA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE_e_6ukzHbvbpVEooSAPbDuarxVjlyH2wa2zz8JzsTfqrVIHI_HZ9zC8KacBvMilzakfK68DITwkGjhbbr0CbCyzlGTCxUj7kaT5gvpEh_Nf1CV_OqVVItiGoQeyeH5ParR1TJbQmO1SKJKtB2Pe3T149yXeXfSTsKr1SGCRuIEtqvAJR2Hiv-pg1mnCHqSpAH-iRDR_k=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGEHzQRcAPA2aqH0GJC4ELZVqRFpF7-FeeofXhhNROGbNWsWBw9SLl2dtMn4_VP4-vKziCAntVA7d7fm70eeE8M7Q3YqdMeGMG3CqokeIyzY7BlTKjx2P5X71J71wVb5Rq2ZA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGlANKfJa0qBlsWCsFgzHnMMH5IAyKGprgvyjOdZndD6ktfaEZDamRRhXy4U78qYRvuTw51E4bcgv7TJ5zn7IdEWGmBf7dWepSM3omaDeNNs3a4o_f_prMcwtUjijM6NbQqdcpc
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHJq_K_YMZ_1XpVsvifW-fFGlbyTgTVbyMGT2rk1BogdAMBlnuKAgXl0UMY1PsIy8QtzgFbLuD4EoXf6goISv7oeK8dA-_7Jxu8e74R2mjONRwvjMirhyjap0jKPu-1-KYJxKG7Z38Hr_Pj
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHCZXR0m1FewUXt78tL6AfiqI4KpFeryvUJz4u0zcaxZgwggNatpb2BVRMOYz8iMzGiYk9G7E4gY0ZAh0Q1vruBfwyLIcrvn6-3Sd4A4S-fsI2i7bijGrSUx8LAwOFZkBjW_tqHy0DLjcMC8qLlJaI21rRq60dxJrAznXPgrDV0ips5Xwmi3imj8U-USV_Y07N5Msw6R0R7cmwvpiLuaqb9vzu7voW7u5eX-U8agQ==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHA0nJ1nF9XdMvEyG8Zqs0zFkAWK0Wg81_Zw3OuXn2xigrZ5gGiObLkixHflADjzsJSg7OvE_2hCEjkWJfwhgyr1lF1s_TvaOz1jMixXyTUA2jkcqDjmxJy6n6lJrABMkX6KR6BrLraHcORxj5BfHGdExTFJ7N655wJyCm8agCMAA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEh1tCmFQmaaR2fM6dJvUtSPCC4UuNd0A8dHvfCewFu7gAxuTOb86pWCP3PPhjKLeUetHq_AvDJaz5q22U5dxeX13SeGRDV6wkJ8530iX7hVman3OuTr5QZ
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFAWd14TRTt2BfgRmsELUcaCyqWHNDYSMjvW0M5rgXX-rFFMvPDUHvqQdIqA22PaPSHput8krc7cc8ssEbaxuvcOpQZ_WWY8ULA-oSCK1dw1KtCAyW3zAQ_pad-z6XIPQ5R
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHPVGx1s70zqvXIXFijCT7ID_4Hcys0W_LYdTIWWTJUsFJD90P72BdBv45hwKsWfLhZpWSHxlF3FD7EtpxOc0tgx02TUzUkB67tGONCeuOLm-Unn1yLXSfhkLNbTSuLW9qWI_szrfQjoA2vDSl69rLDTA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHs7jpF72cvzf_o47pEKXRfZUvRt8PPHO8iERMM91OLZ_kUC2ml8qxgTKcjJZyVCT2TrIw0BsSgQUdvDORjxJXDWzoEmA36yytw5imNaK-Je3CJRCBd35c5L3bnByhJEASg
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH2IbHWvtM-ymq_gLUkr9qBBbShwq-GFZORacjBsk7lBrOMPePN5GMU8h1id8p0CoRoQb6Z2RV54io5TzD6FnLwz6y_qUwYJV8PKLf1SqPLlLnBeehiM_o-RkDDTNeLnCIdpGvbpKTFHQ==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG6j6Sdj6AYPp2wcYwltwScEaX_Y5hKPXg5eSn1YBzl1eVjrpwiH4PthNtX80Yq6tpGgmty_8l_4t23lpDReJ2bkBC_42B0JJsc2EP57mZMHN78rVQiiVzuHUOrQd67
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGOBpLGt1gpl9DnhtViFOdZy3JmcWrZeSDvj6bW-OUWj6uCOwXFdrXy_Maz3onikcEUEukOK94MxPbG04dmn2YLkqqJO8fl8O5bUn1y7hWqEOj2Im_9eda80liZqxt9Gbbxzw==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGH6daLKJAY2pQLHLA08rEH7ajsi15JIHz_leFetVBtiZtIRB4ubqlLhlZbmB8qGGqwftx074GHhPUNEyP9proodmdV631Z7ZktSewUguT1rYqdTR2UzdFB2AZoEsbyCx6BAa1sz0mOqNUKCcd74hWR9EssNI69i8PXb1fbTTvm8HpWR0p2cdE=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGGM9UjTc5HaJ3N1UhRF7vf7-wQthFqdcAwAJSLDUZHVFOJsC8Y34oZosFxr7bWF2ca-MoWUrJtIQPsWgnphXagRyrHs8wvr0GcBSgHmv9nwVS4uGzNYmZ4DxOCkNisYVVh9GHtTA==
- Tabnine AI:
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGeDEHeMVwgD4QxyC80aEbQAgdIYxzdnN1UHGJj9vkZangEnncF7-FNRae8H2pD8WUJRgZfRzTGOK2u1VdaeGfu7-QH3wcku_2IWeU-zyNXYjzsdscc3pIx4BMzFD7PtYejjfl9hQrnebqELQ==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbqavjOO13IV63YYgTD1Uv4yzduD7HUdtsbnSp2-QyjxKwMF2NphFhRBs8vCHSh1kmRCtcAoTiP5M5-iemrdTINUBZ1CApQB57_QmfQAgmyHz9UizAoYgFgJey_x7WzkKCvy8AeBa_xyH0ZOPULZXF53AuZj4=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHlH0xT-V8q4u-1_8YSw7hJ5pGpWHdxwbvtZKtwg_Sc9_YPa4M3ZxcSLNxoBSKF6BLsdO0TcLP-WPtae5rPLLeIKMz4xEIKgHgtj941cT1TpMLHUIy4hzXcLs-eEfZ4IgR3GW1WqJdmeP8990EijVEMYA==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHrY42UjzZbo2fhBScNhV78hZMYNqfauq6g98Ih_QDvpb9I7dIBSC3w-kZ_yv9sEKk98uA6La4srs1T4wmfd5OKh86posqWgrowYcTGW9sbvfKTWC3kilr4M94=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEaeWQCrEp4kxpPnrP3loMhJ7AVqCfXPshqPA5Haot8JaI157ftEuukC_EpWpCIrfWVazQxqLleufSmNk4zBQSEoD0O92O6LTOhfpwZt__tCk0uxcjJmC2rNM2rF3qe0v-VZMc6_pQCGZ7esz1eyO0=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFMX6zilrdZI0t45UjCgWayItOkFjJqT8DOavKL1o7fr6mc2aIhhmdUSNjqUpRDHQ9ZUBoY9KY2PQZYC9u1xuADHbeI-aqkR8ozzkPPwgQnsJv77Bx71EOkouc5TqUMvSHtTeAzMtbQW6bgWPpO3HkHLSCH2I2axQpugBRYD7LruadBylGlTWLxsuDO-PabHSSfc4inEeVKNczyl-3VT5CY8QVDe2L2L5nRSjwB3Dd0QziN0NthYb5QzVnahHotjaLCMagQh2j4m_u1lv-yAo-r_RAX7M4RSVejRt28CSV33ZBaGT03FzNHe-DPuZ567q4VIG6cPoD-S_FDIwz-Zz7wYxqH5vP1Nc55vlXBWvtCbOy1NH657_tqS3E=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEQDrRNFh3UhhcEc6NLzIEucaqB-Th1zg3gaUL3EV3iF-2R5bRE-s9esrmFyOUhNlvqd0RZl4az2GxjNorY0lGvMIVRd0jOfOFQ1AGSV1NkUsB5-LCBY5l6GikOpScTRXMEp_DOmg==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHQw-VRxsYxYrKllZWXRpJuAQIRyuuJmO-lnvqI68u279gjtlRSTuSdfveCT0HmjnYSTQsgeC13urSfJ_aZBYCSRHne32NmrYzE2q8V71Fgqw_ZE6dfsSMmiVA5dBKUjb_OzZEt1I3IzP-YksrH_RJ9KHqZFhkVAkAnsVvXVZSV82jXEX7Ozo-YSMsVVow8dtE=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF_K-W1WdbBo9EMy1h_I7sxvviFy51f6VTBi5NjMsoioC7jew7TH2ATCTmUoUoZwjxyDin2YHKuX6dNiDDiYXoPE-2RBpcESw-GPszOPyX1X4q_e-W9d0CLXKpZwc_0KF8=
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJ_iIwX_bneCcRBcNZXPq4qQo3eIR5C53O88aohVjg7C44v6KAVRiAoAFLsMgDCQ67Gi4de-R4J2qqiYaGd3WPVFMTQ91hNXyTuWx0T-foraxMUkOIQHk1gq2IJKZKonrlfJMyJr-tGZ1AcBcJ3ZR8p7QwtKvOGRE72xxysQ==
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtUgecokYHEbm1dJ6o4jnxwTyX5fP6ZPzwAmR8JK2F9BQPdQbYIljRex6ljTRhfBt62lintcoig8Uw5jWBNRmqiW9fHhpMvHdaFrPUqSHEEodwWL6v9DC1KY-y9Mq3JIEZjE81FgnwuNFbPoEULO-AoNvR
    - https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEBTktUj37Ww44tHuIpxosD79mK0G8WUNOayAiM_YQCdL80nWSjIJb0eNVDo4sfty6JW01NQSoEeHrb63dLI7fD0ba5aCaAZGCwOj3ZOFSCzzn73NdrTMVHguuFaJFfo2pefzad7Ni-lYNVO_eKRp-aPENeOGa0sS-dbpRIqbL1QOHfOHc4j_3uya1THpzRnIdl
