"""
search_page.py - Google 検索ページ用 Page Object Model

Google 検索（https://www.google.com/）の
検索操作と結果取得を行うページオブジェクトクラス。
"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class GoogleSearchPage(BasePage):
    """Google 検索ページのページオブジェクト"""

    URL = "https://www.google.com"

    def __init__(self, page: Page):
        super().__init__(page)
        # 検索ボックス（textarea）
        self.search_input = page.locator("textarea[name='q']")
        # 検索結果の見出し
        self.result_headings = page.locator("h3")

    def navigate_to_google(self):
        """Google トップページに遷移"""
        self.navigate(self.URL)

    def search(self, query: str):
        """検索クエリを入力して検索を実行"""
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.page.wait_for_load_state("domcontentloaded")

    def get_result_titles(self) -> list[str]:
        """検索結果の見出しテキストをリストで取得"""
        self.result_headings.first.wait_for(state="visible", timeout=10000)
        return self.result_headings.all_text_contents()

    def get_result_count(self) -> int:
        """検索結果の見出し数を取得"""
        self.result_headings.first.wait_for(state="visible", timeout=10000)
        return self.result_headings.count()

    def has_results(self) -> bool:
        """検索結果が存在するかを判定"""
        try:
            self.result_headings.first.wait_for(state="visible", timeout=10000)
            return self.result_headings.count() > 0
        except Exception:
            return False
