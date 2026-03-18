"""
web_tables_page.py - DemoQA Web Tables ページ用 Page Object Model

DemoQA (https://demoqa.com/webtables) の
Webテーブル操作（追加・検索・編集・削除）を行うページオブジェクトクラス。
"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class DemoQAWebTablesPage(BasePage):
    """DemoQA Web Tables ページのページオブジェクト"""

    URL = "https://demoqa.com/webtables"

    def __init__(self, page: Page):
        super().__init__(page)
        # テーブル操作のロケーター
        self.add_button = page.locator("#addNewRecordButton")
        self.search_box = page.locator("#searchBox")
        self.data_rows = page.locator("table tbody tr")

        # 登録フォームのロケーター
        self.form_first_name = page.locator("#firstName")
        self.form_last_name = page.locator("#lastName")
        self.form_email = page.locator("#userEmail")
        self.form_age = page.locator("#age")
        self.form_salary = page.locator("#salary")
        self.form_department = page.locator("#department")
        self.form_submit = page.locator("#submit")

    def navigate_to_web_tables(self):
        """Web Tables ページに遷移"""
        self.navigate(self.URL)

    def add_record(
        self,
        first_name: str,
        last_name: str,
        email: str,
        age: int,
        salary: int,
        department: str,
    ):
        """新しいレコードを追加"""
        self.add_button.click()
        self.form_first_name.fill(first_name)
        self.form_last_name.fill(last_name)
        self.form_email.fill(email)
        self.form_age.fill(str(age))
        self.form_salary.fill(str(salary))
        self.form_department.fill(department)
        self.form_submit.click()

    def search(self, query: str):
        """検索ボックスにクエリを入力してテーブルをフィルタリング"""
        self.search_box.fill(query)

    def get_row_count(self) -> int:
        """データが存在する行数を取得"""
        return self.data_rows.count()

    def edit_record(self, row_index: int, **fields):
        """指定行のレコードを編集（キーワード引数で更新フィールドを指定）"""
        edit_button = self.data_rows.nth(row_index).locator("[title='Edit']")
        edit_button.click()

        field_map = {
            "first_name": self.form_first_name,
            "last_name": self.form_last_name,
            "email": self.form_email,
            "age": self.form_age,
            "salary": self.form_salary,
            "department": self.form_department,
        }

        for field_name, value in fields.items():
            if field_name in field_map:
                field_map[field_name].clear()
                field_map[field_name].fill(str(value))

        self.form_submit.click()

    def delete_record(self, row_index: int):
        """指定行のレコードを削除"""
        delete_button = self.data_rows.nth(row_index).locator("[title='Delete']")
        delete_button.click()

    def get_table_data(self) -> list[dict]:
        """テーブル全体のデータを辞書のリストとして取得"""
        headers = ["First Name", "Last Name", "Age", "Email", "Salary", "Department"]
        data = []

        for i in range(self.data_rows.count()):
            row = self.data_rows.nth(i)
            cells = row.locator("td")
            if cells.count() < len(headers):
                continue
            row_data = {}
            for j, header in enumerate(headers):
                row_data[header] = cells.nth(j).inner_text().strip()
            data.append(row_data)

        return data
