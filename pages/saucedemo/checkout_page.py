"""
checkout_page.py - SauceDemo チェックアウトページ用 Page Object Model

SauceDemo のチェックアウトページ群を操作するためのページオブジェクトクラス。
  - Step 1: https://www.saucedemo.com/checkout-step-one.html（お客様情報入力）
  - Step 2: https://www.saucedemo.com/checkout-step-two.html（注文概要）
  - Complete: https://www.saucedemo.com/checkout-complete.html（注文完了）
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceDemoCheckoutPage(BasePage):
    """SauceDemo チェックアウトページのページオブジェクト"""

    STEP_ONE_URL = "https://www.saucedemo.com/checkout-step-one.html"
    STEP_TWO_URL = "https://www.saucedemo.com/checkout-step-two.html"
    COMPLETE_URL = "https://www.saucedemo.com/checkout-complete.html"

    def __init__(self, page: Page):
        super().__init__(page)
        # Step 1: お客様情報入力フォームのロケーター
        self.first_name = page.locator("[data-test='firstName']")
        self.last_name = page.locator("[data-test='lastName']")
        self.zip_code = page.locator("[data-test='postalCode']")
        self.continue_button = page.locator("[data-test='continue']")
        self.cancel_button = page.locator("[data-test='cancel']")
        self.error_message = page.locator("[data-test='error']")

        # Step 2: 注文概要のロケーター
        self.finish_button = page.locator("[data-test='finish']")
        self.summary_total = page.locator("[data-test='total-label']")

        # Complete: 注文完了のロケーター
        self.complete_header = page.locator("[data-test='complete-header']")

    def fill_info(self, first_name: str, last_name: str, zip_code: str):
        """お客様情報（名前・姓・郵便番号）を入力"""
        self.first_name.fill(first_name)
        self.last_name.fill(last_name)
        self.zip_code.fill(zip_code)

    def continue_checkout(self):
        """「Continue」ボタンをクリックして注文概要に進む"""
        self.continue_button.click()

    def cancel(self):
        """「Cancel」ボタンをクリックしてチェックアウトをキャンセル"""
        self.cancel_button.click()

    def finish_order(self):
        """「Finish」ボタンをクリックして注文を確定"""
        self.finish_button.click()

    def get_complete_header(self) -> str:
        """注文完了ヘッダーのテキストを取得"""
        return self.complete_header.text_content()

    def get_error_message(self) -> str:
        """チェックアウトエラーメッセージのテキストを取得"""
        return self.error_message.text_content()

    def get_summary_total(self) -> str:
        """注文概要の合計金額テキストを取得"""
        return self.summary_total.text_content()
