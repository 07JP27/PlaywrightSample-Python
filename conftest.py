"""
conftest.py - Playwright テスト共通設定

各テストファイルで Playwright のライフサイクルを明示的に管理する。
pytest-playwright プラグインは使用せず、純粋な Playwright API を直接使用する。

標準的なライフサイクルパターン:
  1. sync_playwright().start() で Playwright を起動
  2. playwright.chromium.launch() でブラウザを起動
  3. browser.new_context() でコンテキストを作成
  4. context.new_page() でページを作成
  5. テスト実行後、逆順でクリーンアップ
"""
