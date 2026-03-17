"""
conftest.py - Playwright テスト共通フィクスチャ・設定

pytest-playwright プラグインが提供する標準フィクスチャ:
  - playwright: Playwright インスタンス
  - browser: Browser インスタンス
  - context: BrowserContext インスタンス
  - page: Page インスタンス
"""
import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """ブラウザコンテキストのデフォルト設定をカスタマイズ"""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "ja-JP",
        "timezone_id": "Asia/Tokyo",
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """ブラウザ起動時のデフォルト引数をカスタマイズ"""
    return {
        **browser_type_launch_args,
        # slow_mo を有効にする場合はコメント解除
        # "slow_mo": 100,
    }
