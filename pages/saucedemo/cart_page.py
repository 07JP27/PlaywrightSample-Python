"""
cart_page.py - SauceDemo カートページ用 Page Object Model

SauceDemo のカートページ（https://www.saucedemo.com/cart.html）を
操作するためのページオブジェクトクラス。
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceDemoCartPage(BasePage):
    """SauceDemo カートページのページオブジェクト"""

    URL = "https://www.saucedemo.com/cart.html"

    def __init__(self, page: Page):
        super().__init__(page)
        # ロケーター定義
        self.cart_items = page.locator("[data-test='inventory-item']")
        self.continue_shopping_button = page.locator("[data-test='continue-shopping']")
        self.checkout_button = page.locator("[data-test='checkout']")

    def get_cart_items(self) -> list[str]:
        """カート内の全商品名をリストで取得"""
        name_locators = self.page.locator("[data-test='inventory-item-name']")
        return name_locators.all_text_contents()

    def remove_item(self, name: str):
        """指定した商品名の商品をカートから削除"""
        product_id = name.lower().replace(" ", "-")
        self.page.locator(f"[data-test='remove-{product_id}']").click()

    def continue_shopping(self):
        """「買い物を続ける」ボタンをクリックして商品一覧に戻る"""
        self.continue_shopping_button.click()

    def proceed_to_checkout(self):
        """「チェックアウト」ボタンをクリックしてチェックアウトに進む"""
        self.checkout_button.click()

    def get_item_count(self) -> int:
        """カート内の商品数を取得"""
        return self.cart_items.count()
