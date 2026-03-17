"""
base_page.py - 全ページオブジェクトの基底クラス

Page Object Model (POM) パターンの基底クラス。
共通のナビゲーション・待機メソッドを提供する。
"""
from playwright.sync_api import Page, expect


class BasePage:
    """全ページオブジェクトの基底クラス"""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        """指定URLに遷移し、ロード完了を待機"""
        self.page.goto(url)
        self.page.wait_for_load_state("domcontentloaded")

    def get_title(self) -> str:
        """ページタイトルを取得"""
        return self.page.title()

    def get_url(self) -> str:
        """現在のURLを取得"""
        return self.page.url

    def wait_for_page_load(self, state: str = "load"):
        """ページロード状態を待機"""
        self.page.wait_for_load_state(state)

    def take_screenshot(self, path: str, full_page: bool = False):
        """スクリーンショットを撮影"""
        self.page.screenshot(path=path, full_page=full_page)
