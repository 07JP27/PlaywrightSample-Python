"""
inventory_page.py - SauceDemo 商品一覧ページ用 Page Object Model

SauceDemo の商品一覧ページ（https://www.saucedemo.com/inventory.html）を
操作するためのページオブジェクトクラス。
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class SauceDemoInventoryPage(BasePage):
    """SauceDemo 商品一覧ページのページオブジェクト"""

    URL = "https://www.saucedemo.com/inventory.html"

    def __init__(self, page: Page):
        super().__init__(page)
        # ロケーター定義
        self.product_list = page.locator("[data-test='inventory-item']")
        self.sort_dropdown = page.locator("[data-test='product-sort-container']")
        self.cart_badge = page.locator("[data-test='shopping-cart-badge']")
        self.cart_link = page.locator("[data-test='shopping-cart-link']")

    def get_product_count(self) -> int:
        """商品一覧に表示されている商品数を取得"""
        return self.product_list.count()

    def add_product_to_cart(self, product_name: str):
        """指定した商品名の商品をカートに追加"""
        # 商品名からdata-test用IDを生成（小文字化・スペースをハイフンに変換）
        product_id = product_name.lower().replace(" ", "-")
        self.page.locator(f"[data-test='add-to-cart-{product_id}']").click()

    def remove_product_from_cart(self, product_name: str):
        """指定した商品名の商品をカートから削除"""
        product_id = product_name.lower().replace(" ", "-")
        self.page.locator(f"[data-test='remove-{product_id}']").click()

    def sort_products(self, option: str):
        """商品の並び替えを実行（az, za, lohi, hilo）"""
        self.sort_dropdown.select_option(option)

    def get_cart_count(self) -> int:
        """カートバッジに表示されている商品数を取得（バッジ非表示の場合は0）"""
        if self.cart_badge.is_visible():
            return int(self.cart_badge.text_content())
        return 0

    def go_to_cart(self):
        """カートページに遷移"""
        self.cart_link.click()

    def get_product_names(self) -> list[str]:
        """全商品名のリストを取得"""
        name_locators = self.page.locator("[data-test='inventory-item-name']")
        return name_locators.all_text_contents()

    def get_product_prices(self) -> list[str]:
        """全商品価格のリストを取得"""
        price_locators = self.page.locator("[data-test='inventory-item-price']")
        return price_locators.all_text_contents()
