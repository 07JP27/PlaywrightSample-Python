"""
form_page.py - The Internet フォーム関連ページ用 Page Object Model

The Internet (https://the-internet.herokuapp.com/) の
チェックボックス、ドロップダウン、入力、ファイルアップロード操作を行う
ページオブジェクトクラス。
"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class TheInternetFormPage(BasePage):
    """The Internet フォーム関連ページのページオブジェクト"""

    BASE_URL = "https://the-internet.herokuapp.com"

    def __init__(self, page: Page):
        super().__init__(page)
        # チェックボックスページのロケーター
        self.checkboxes = page.locator("#checkboxes input[type='checkbox']")

        # ドロップダウンページのロケーター
        self.dropdown = page.locator("#dropdown")

        # ファイルアップロードページのロケーター
        self.file_input = page.locator("#file-upload")
        self.upload_button = page.locator("#file-submit")
        self.uploaded_filename = page.locator("#uploaded-files")

    def navigate_to_checkboxes(self):
        """チェックボックスページに遷移"""
        self.navigate(f"{self.BASE_URL}/checkboxes")

    def toggle_checkbox(self, index: int):
        """指定インデックスのチェックボックスを切り替え"""
        self.checkboxes.nth(index).click()

    def is_checkbox_checked(self, index: int) -> bool:
        """指定インデックスのチェックボックスの選択状態を取得"""
        return self.checkboxes.nth(index).is_checked()

    def navigate_to_dropdown(self):
        """ドロップダウンページに遷移"""
        self.navigate(f"{self.BASE_URL}/dropdown")

    def select_dropdown_option(self, value: str):
        """ドロップダウンで指定された値のオプションを選択"""
        self.dropdown.select_option(value=value)

    def navigate_to_file_upload(self):
        """ファイルアップロードページに遷移"""
        self.navigate(f"{self.BASE_URL}/upload")

    def upload_file(self, file_path: str):
        """ファイルをアップロード"""
        self.file_input.set_input_files(file_path)
        self.upload_button.click()
        self.wait_for_page_load()

    def get_uploaded_filename(self) -> str:
        """アップロードされたファイル名を取得"""
        return self.uploaded_filename.inner_text().strip()
