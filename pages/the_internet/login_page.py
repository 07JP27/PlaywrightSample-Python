"""
login_page.py - The Internet ログインページ用 Page Object Model

The Internet (https://the-internet.herokuapp.com/login) の
ログイン・ログアウト操作を行うページオブジェクトクラス。
"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class TheInternetLoginPage(BasePage):
    """The Internet ログインページのページオブジェクト"""

    URL = "https://the-internet.herokuapp.com/login"

    # 有効な認証情報
    VALID_USERNAME = "tomsmith"
    VALID_PASSWORD = "SuperSecretPassword!"

    def __init__(self, page: Page):
        super().__init__(page)
        # ロケーター定義
        self.username = page.locator("#username")
        self.password = page.locator("#password")
        self.login_button = page.locator("button[type='submit']")
        self.flash_message = page.locator("#flash")
        self.logout_button = page.locator(".button")

    def navigate_to_login(self):
        """ログインページに遷移"""
        self.navigate(self.URL)

    def login(self, username: str, password: str):
        """ユーザー名とパスワードでログイン"""
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()
        self.wait_for_page_load()

    def get_flash_message(self) -> str:
        """フラッシュメッセージのテキストを取得"""
        return self.flash_message.inner_text().strip()

    def is_logged_in(self) -> bool:
        """ログイン状態を判定（ログアウトボタンの表示有無で判断）"""
        return self.logout_button.is_visible()

    def logout(self):
        """ログアウトを実行"""
        self.logout_button.click()
        self.wait_for_page_load()
