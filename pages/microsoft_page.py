"""
microsoft_page.py - Microsoft サイト用 Page Object Model

Microsoft のサイト（https://www.microsoft.com）を操作するための
ページオブジェクトクラス。
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class MicrosoftHomePage(BasePage):
    """Microsoft ホームページのページオブジェクト"""

    URL = "https://www.microsoft.com/ja-jp"

    def __init__(self, page: Page):
        super().__init__(page)
        # ロケーター定義
        self.search_button = page.get_by_role("button", name="検索")
        self.nav_links = page.get_by_role("navigation")

    def navigate_to_home(self):
        """Microsoft ホームページに遷移"""
        self.navigate(self.URL)

    def get_page_heading(self):
        """ページの見出しを取得"""
        return self.page.locator("h1").first

    def click_search(self):
        """検索ボタンをクリック"""
        self.search_button.click()


class MicrosoftSearchPage(BasePage):
    """Microsoft 検索結果ページのページオブジェクト"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.get_by_role("searchbox")

    def search(self, query: str):
        """検索を実行"""
        self.search_input.fill(query)
        self.search_input.press("Enter")
