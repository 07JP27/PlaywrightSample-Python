"""
saucedemo - SauceDemo サイト用 Page Object Model パッケージ

SauceDemo（https://www.saucedemo.com/）の各ページを操作するための
ページオブジェクトクラスを提供する。
"""
from pages.saucedemo.login_page import SauceDemoLoginPage
from pages.saucedemo.inventory_page import SauceDemoInventoryPage
from pages.saucedemo.cart_page import SauceDemoCartPage
from pages.saucedemo.checkout_page import SauceDemoCheckoutPage

__all__ = [
    "SauceDemoLoginPage",
    "SauceDemoInventoryPage",
    "SauceDemoCartPage",
    "SauceDemoCheckoutPage",
]
