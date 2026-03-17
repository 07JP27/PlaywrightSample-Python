"""
login_page.py - OrangeHRM ログインページ用 Page Object Model

OrangeHRM デモサイトのログインページを操作するためのページオブジェクトクラス。
URL: https://opensource-demo.orangehrmlive.com/web/index.php/auth/login
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class OrangeHRMLoginPage(BasePage):
    """OrangeHRM ログインページのページオブジェクト"""

    URL = "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"

    def __init__(self, page: Page):
        super().__init__(page)
        # ロケーター定義
        self.username_input = page.locator("input[name='username']")
        self.password_input = page.locator("input[name='password']")
        self.login_button = page.locator("button[type='submit']")
        self.error_message = page.locator(".oxd-alert")

    def navigate_to_login(self):
        """ログインページに遷移"""
        self.navigate(self.URL)

    def login(self, username: str, password: str):
        """ユーザー名とパスワードを入力してログインを実行"""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        self.page.wait_for_load_state("networkidle")

    def get_error_message(self) -> str:
        """ログインエラーメッセージのテキストを取得"""
        self.error_message.wait_for(state="visible")
        return self.error_message.text_content().strip()

    def is_login_page(self) -> bool:
        """現在のページがログインページかどうかを判定"""
        return "/auth/login" in self.get_url()
