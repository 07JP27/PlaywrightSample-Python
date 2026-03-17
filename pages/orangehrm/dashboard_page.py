"""
dashboard_page.py - OrangeHRM ダッシュボードページ用 Page Object Model

OrangeHRM デモサイトのダッシュボードページを操作するためのページオブジェクトクラス。
URL: https://opensource-demo.orangehrmlive.com/web/index.php/dashboard/index
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class OrangeHRMDashboardPage(BasePage):
    """OrangeHRM ダッシュボードページのページオブジェクト"""

    URL = "https://opensource-demo.orangehrmlive.com/web/index.php/dashboard/index"

    def __init__(self, page: Page):
        super().__init__(page)
        # ロケーター定義
        self.dashboard_widgets = page.locator(".oxd-layout")
        self.sidebar_menu = page.locator(".oxd-sidepanel-body")
        self.user_dropdown = page.locator(".oxd-userdropdown")

    def is_dashboard_loaded(self) -> bool:
        """ダッシュボードが正常にロードされたかを判定"""
        self.dashboard_widgets.wait_for(state="visible")
        return "/dashboard" in self.get_url()

    def get_widget_count(self) -> int:
        """ダッシュボード上のウィジェット数を取得"""
        widgets = self.page.locator(".oxd-grid-item")
        widgets.first.wait_for(state="visible")
        return widgets.count()

    def navigate_to_menu(self, menu_name: str):
        """左サイドバーから指定メニュー項目に遷移"""
        menu_item = self.sidebar_menu.locator("a.oxd-main-menu-item").filter(
            has_text=menu_name
        )
        menu_item.click()
        self.page.wait_for_load_state("networkidle")

    def logout(self):
        """ユーザードロップダウンからログアウトを実行"""
        self.user_dropdown.click()
        logout_link = self.page.locator("a", has_text="Logout")
        logout_link.click()
        self.page.wait_for_load_state("networkidle")
