"""
pim_page.py - OrangeHRM PIM（人事管理）ページ用 Page Object Model

OrangeHRM デモサイトの PIM（Personnel Information Management）ページを
操作するためのページオブジェクトクラス。
URL: https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList
"""
from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class OrangeHRMPimPage(BasePage):
    """OrangeHRM PIM（人事管理）ページのページオブジェクト"""

    URL = "https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList"

    def __init__(self, page: Page):
        super().__init__(page)
        # ロケーター定義
        self.employee_name_input = page.locator(
            ".oxd-autocomplete-text-input > input"
        )
        self.search_button = page.locator("button[type='submit']")
        self.employee_table = page.locator(".oxd-table")
        self.add_employee_button = page.locator("button", has_text="Add")

    def search_employee(self, name: str):
        """従業員名で検索を実行"""
        self.employee_name_input.first.fill(name)
        # オートコンプリートの候補が表示されるまで待機
        self.page.wait_for_timeout(1000)
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")

    def get_employee_count(self) -> int:
        """検索結果の従業員件数を取得"""
        rows = self.employee_table.locator(".oxd-table-body .oxd-table-row")
        rows.first.wait_for(state="visible")
        return rows.count()

    def is_employee_listed(self, name: str) -> bool:
        """指定した名前の従業員が一覧に表示されているかを判定"""
        rows = self.employee_table.locator(".oxd-table-body .oxd-table-row")
        rows.first.wait_for(state="visible")
        # テーブル行内に名前を含む行があるか確認
        matching_row = rows.filter(has_text=name)
        return matching_row.count() > 0

    def click_add_employee(self):
        """「従業員追加」ボタンをクリックして追加画面へ遷移"""
        self.add_employee_button.click()
        self.page.wait_for_load_state("networkidle")
