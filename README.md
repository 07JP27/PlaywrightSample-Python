# Playwright Python 全機能サンプル

Playwright for Python の全機能を網羅するサンプルプロジェクトです。

## セットアップ

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# ブラウザバイナリのインストール
playwright install
```

## テスト実行

```bash
# 全テスト実行
pytest

# 特定テストファイルの実行
pytest tests/test_01_browser_launch.py

# ヘッドフルモード（ブラウザ表示）
pytest --headed

# スローモーション付き
pytest --slowmo 500

# 特定ブラウザで実行
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit

# 全ブラウザで実行
pytest --browser chromium --browser firefox --browser webkit

# トレース記録付き
pytest --tracing on

# 動画記録付き
pytest --video on

# 失敗時のみスクリーンショット
pytest --screenshot only-on-failure

# ベースURL指定
pytest --base-url https://www.microsoft.com
```

## プロジェクト構成

```
├── conftest.py                       # 共通フィクスチャ・設定
├── pages/                            # Page Object Model
│   ├── base_page.py                  # 基底ページクラス
│   └── microsoft_page.py            # Microsoft サイト用 POM
├── tests/
│   ├── test_01_browser_launch.py     # ブラウザ起動・管理
│   ├── test_02_browser_context.py    # ブラウザコンテキスト
│   ├── test_03_page_navigation.py    # ページ操作の基本
│   ├── test_04_locators.py           # ロケーター戦略
│   ├── test_05_actions.py            # ユーザーアクション
│   ├── test_06_assertions.py         # アサーション（expect）
│   ├── test_07_network.py            # ネットワーク制御
│   ├── test_08_websocket.py          # WebSocket 制御
│   ├── test_09_file_operations.py    # ファイル操作
│   ├── test_10_dialogs.py            # ダイアログ処理
│   ├── test_11_multi_page.py         # マルチページ・タブ
│   ├── test_12_frames.py            # Frame / iframe
│   ├── test_13_shadow_dom.py        # Shadow DOM
│   ├── test_14_emulation.py          # エミュレーション
│   ├── test_15_auth_storage.py       # 認証・ストレージ状態
│   ├── test_16_screenshots_video.py  # スクリーンショット・動画・PDF
│   ├── test_17_tracing.py            # トレーシング
│   ├── test_18_visual_regression.py  # ビジュアルリグレッション
│   ├── test_19_clock.py              # Clock（時刻制御）
│   ├── test_20_api_testing.py        # API テスト
│   ├── test_21_accessibility.py      # アクセシビリティ
│   ├── test_22_js_evaluation.py      # JavaScript 実行
│   ├── test_23_advanced_config.py    # 高度な接続・設定
│   └── test_24_async_api.py          # 非同期 API サンプル
├── data/                              # テストデータ
└── output/                            # 出力先
    ├── screenshots/
    ├── videos/
    ├── traces/
    └── pdf/
```

## カバーする機能一覧

1. ブラウザ起動・管理（Chromium / Firefox / WebKit）
2. ブラウザコンテキスト（分離・Cookie・認証）
3. ページ操作（ナビゲーション・待機）
4. ロケーター戦略（get_by_role 等 14 種）
5. ユーザーアクション（クリック・入力・D&D 等）
6. アサーション（expect 全メソッド）
7. ネットワーク制御（route / mock / HAR）
8. WebSocket 制御
9. ファイル操作（アップロード・ダウンロード）
10. ダイアログ処理（alert / confirm / prompt）
11. マルチページ・タブ・ポップアップ
12. Frame / iframe 操作
13. Shadow DOM
14. エミュレーション（デバイス・位置情報・ロケール等）
15. 認証・ストレージ状態
16. スクリーンショット・動画・PDF
17. トレーシング
18. ビジュアルリグレッション
19. Clock（時刻制御）
20. API テスト
21. アクセシビリティテスト
22. JavaScript 実行・評価
23. 高度な接続・設定（CDP 等）
24. 非同期 API（async/await）
