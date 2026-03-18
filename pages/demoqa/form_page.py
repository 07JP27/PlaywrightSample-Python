"""
form_page.py - DemoQA フォームページ用 Page Object Model

DemoQA (https://demoqa.com/automation-practice-form) の
学生登録フォーム操作を行うページオブジェクトクラス。
"""
from playwright.sync_api import Page

from pages.base_page import BasePage


class DemoQAFormPage(BasePage):
    """DemoQA 学生登録フォームのページオブジェクト"""

    URL = "https://demoqa.com/automation-practice-form"

    def __init__(self, page: Page):
        super().__init__(page)
        # 基本情報のロケーター
        self.first_name = page.locator("#firstName")
        self.last_name = page.locator("#lastName")
        self.email = page.locator("#userEmail")
        self.mobile = page.locator("#userNumber")

        # 性別ラジオボタンのロケーター
        self.gender_radios = page.locator("[name='gender']")

        # 科目のロケーター
        self.subjects_input = page.locator("#subjectsInput")

        # 趣味チェックボックスのロケーター
        self.hobbies_checkboxes = page.locator("#hobbiesWrapper .custom-checkbox")

        # 画像アップロードのロケーター
        self.picture_upload = page.locator("#uploadPicture")

        # 住所のロケーター
        self.address = page.locator("#currentAddress")

        # 州・都市ドロップダウンのロケーター
        self.state_dropdown = page.locator("#state")
        self.city_dropdown = page.locator("#city")

        # 送信ボタン
        self.submit_button = page.locator("#submit")

        # 確認モーダルのロケーター
        self.confirmation_modal = page.locator(".modal-content")
        self.modal_title = page.locator("#example-modal-sizes-title-lg")
        self.modal_table = page.locator(".table-responsive table")
        self.modal_close_button = page.locator("#closeLargeModal")

    def navigate_to_form(self):
        """学生登録フォームページに遷移"""
        self.navigate(self.URL)

    def fill_name(self, first: str, last: str):
        """名前を入力（名・姓）"""
        self.first_name.fill(first)
        self.last_name.fill(last)

    def fill_email(self, email: str):
        """メールアドレスを入力"""
        self.email.fill(email)

    def select_gender(self, gender: str):
        """性別を選択（Male / Female / Other）"""
        # ラジオボタンは隠れているため、ラベルをクリック
        self.page.locator(f"#genterWrapper label:text-is('{gender}')").click()

    def fill_mobile(self, number: str):
        """携帯番号を入力"""
        self.mobile.fill(number)

    def add_subject(self, subject: str):
        """科目を追加"""
        self.subjects_input.fill(subject)
        self.page.keyboard.press("Enter")

    def select_hobby(self, hobby: str):
        """趣味を選択（Sports / Reading / Music）"""
        self.page.locator(f"label:has-text('{hobby}')").click()

    def upload_picture(self, file_path: str):
        """画像ファイルをアップロード"""
        self.picture_upload.set_input_files(file_path)

    def fill_address(self, address: str):
        """現住所を入力"""
        self.address.fill(address)

    def select_state(self, state: str):
        """州を選択"""
        self.state_dropdown.click()
        self.page.locator(f"#react-select-3-option-0").locator(
            f"xpath=//div[contains(text(), '{state}')]"
        ).first.click()

    def select_city(self, city: str):
        """都市を選択"""
        self.city_dropdown.click()
        self.page.locator(f"#react-select-4-option-0").locator(
            f"xpath=//div[contains(text(), '{city}')]"
        ).first.click()

    def submit_form(self):
        """フォームを送信"""
        self.submit_button.click()

    def get_confirmation_modal(self) -> dict:
        """送信後の確認モーダル内容を辞書形式で取得"""
        self.confirmation_modal.wait_for(state="visible")
        rows = self.modal_table.locator("tbody tr")
        result = {}
        for i in range(rows.count()):
            label = rows.nth(i).locator("td").first.inner_text()
            value = rows.nth(i).locator("td").last.inner_text()
            result[label] = value
        return result

    def close_modal(self):
        """確認モーダルを閉じる"""
        self.modal_close_button.click()
