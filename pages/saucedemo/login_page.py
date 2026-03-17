"""
login_page.py - SauceDemo ログインページ用 Page Object Model

SauceDemo のログインページ（https://www.saucedemo.com/）を操作するための
ページオブジェクトクラス。
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceDemoLoginPage(BasePage):
    """SauceDemo ログインページのページオブジェクト"""

    URL = "https://www.saucedemo.com/"

    def __init__(self, page: Page):
        super().__init__(page)
        # ロケーター定義
        self.username_input = page.locator("[data-test='username']")
        self.password_input = page.locator("[data-test='password']")
        self.login_button = page.locator("[data-test='login-button']")
        self.error_message = page.locator("[data-test='error']")

    def navigate_to_login(self):
        """ログインページに遷移"""
        self.navigate(self.URL)

    def login(self, username: str, password: str):
        """ユーザー名とパスワードでログインを実行"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def get_error_message(self) -> str:
        """ログインエラーメッセージのテキストを取得"""
        return self.error_message.text_content()
