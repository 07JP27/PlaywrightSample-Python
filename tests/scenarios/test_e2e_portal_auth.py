"""
test_e2e_portal_auth.py - 社内ポータル認証・フォーム操作フロー E2Eシナリオテスト

The Internet (https://the-internet.herokuapp.com/) を対象に、
ログイン認証、フォーム操作（チェックボックス・ドロップダウン・ファイルアップロード）を
一連のポータル業務フローとして検証するシナリオテスト。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import Page, expect, sync_playwright
from runner import TestRunner
from evidence import Evidence, load_test_users, generate_evidence_report

from pages.the_internet.login_page import TheInternetLoginPage
from pages.the_internet.form_page import TheInternetFormPage


class TestPortalAuthFlow:
    """社内ポータル認証・フォーム操作フローのE2Eシナリオテスト"""

    # -----------------------------------------------------------------------
    # 1. 正常ログイン
    # -----------------------------------------------------------------------
    def test_login_success(self, page: Page, test_users: dict, evidence):
        """正常ログイン — 有効な認証情報でログインし、セキュアエリアに遷移できることを確認"""
        login_page = TheInternetLoginPage(page)
        creds = test_users["the_internet"]["valid_user"]

        login_page.navigate_to_login()
        evidence.capture("ログイン画面表示")
        login_page.login(creds["username"], creds["password"])

        # ログイン成功メッセージを確認
        flash = login_page.get_flash_message()
        assert "You logged into a secure area!" in flash

        # セキュアエリアにいることを確認
        assert login_page.is_logged_in()
        evidence.capture("ログイン成功_セキュアエリア")

    # -----------------------------------------------------------------------
    # 2. ログイン失敗
    # -----------------------------------------------------------------------
    def test_login_failure(self, page: Page, evidence):
        """ログイン失敗 — 不正な認証情報でエラーメッセージが表示されることを確認"""
        login_page = TheInternetLoginPage(page)

        login_page.navigate_to_login()
        evidence.capture("ログイン画面表示")
        login_page.login("invalid_user", "invalid_pass")
        evidence.capture("不正認証入力")

        # エラーメッセージを確認
        flash = login_page.get_flash_message()
        assert "Your username is invalid!" in flash
        evidence.capture("エラーメッセージ表示")

    # -----------------------------------------------------------------------
    # 3. ログイン→ログアウト→再ログイン
    # -----------------------------------------------------------------------
    def test_login_logout_relogin_cycle(
        self, page: Page, test_users: dict, evidence
    ):
        """ログイン→ログアウト→再ログインサイクル — セッション管理が正常に動作することを確認"""
        login_page = TheInternetLoginPage(page)
        creds = test_users["the_internet"]["valid_user"]

        # ステップ1: ログイン
        login_page.navigate_to_login()
        login_page.login(creds["username"], creds["password"])
        assert login_page.is_logged_in()
        evidence.capture("ログイン完了")

        # ステップ2: ログアウト
        login_page.logout()
        flash = login_page.get_flash_message()
        assert "You logged out" in flash
        evidence.capture("ログアウト完了")

        # ステップ3: 再ログイン
        login_page.login(creds["username"], creds["password"])
        assert login_page.is_logged_in()
        evidence.capture("再ログイン完了")

    # -----------------------------------------------------------------------
    # 4. チェックボックス操作
    # -----------------------------------------------------------------------
    def test_checkbox_operations(self, page: Page, evidence):
        """チェックボックス操作 — トグルにより選択状態が正しく反転することを確認"""
        form_page = TheInternetFormPage(page)

        form_page.navigate_to_checkboxes()
        evidence.capture("チェックボックス画面_初期状態")

        # 初期状態を確認（checkbox 1: 未選択, checkbox 2: 選択済み）
        assert not form_page.is_checkbox_checked(0)
        assert form_page.is_checkbox_checked(1)

        # 両方をトグル
        form_page.toggle_checkbox(0)
        form_page.toggle_checkbox(1)

        # 状態が反転していることを確認
        assert form_page.is_checkbox_checked(0)
        assert not form_page.is_checkbox_checked(1)
        evidence.capture("トグル操作後")

    # -----------------------------------------------------------------------
    # 5. ドロップダウン選択
    # -----------------------------------------------------------------------
    def test_dropdown_selection(self, page: Page, evidence):
        """ドロップダウン選択 — オプションの選択・変更が正しく反映されることを確認"""
        form_page = TheInternetFormPage(page)

        form_page.navigate_to_dropdown()
        evidence.capture("ドロップダウン画面表示")

        # Option 1 を選択して確認
        form_page.select_dropdown_option("1")
        expect(form_page.dropdown).to_have_value("1")
        evidence.capture("Option1選択")

        # Option 2 に変更して確認
        form_page.select_dropdown_option("2")
        expect(form_page.dropdown).to_have_value("2")
        evidence.capture("Option2選択")

    # -----------------------------------------------------------------------
    # 6. ファイルアップロード
    # -----------------------------------------------------------------------
    def test_file_upload(self, page: Page, evidence):
        """ファイルアップロード — ファイルが正常にアップロードされ、ファイル名が表示されることを確認"""
        form_page = TheInternetFormPage(page)
        upload_file = Path(__file__).resolve().parent.parent.parent / "data" / "upload_sample.txt"

        form_page.navigate_to_file_upload()
        evidence.capture("アップロード画面表示")
        form_page.upload_file(str(upload_file))
        evidence.capture("ファイル選択後")

        # アップロード成功画面でファイル名を確認
        assert form_page.get_uploaded_filename() == "upload_sample.txt"
        evidence.capture("アップロード完了")

    # -----------------------------------------------------------------------
    # 7. 統合ポータルワークフロー（メインシナリオ）
    # -----------------------------------------------------------------------
    def test_complete_portal_workflow(
        self, page: Page, test_users: dict, evidence
    ):
        """統合ポータルワークフロー — 認証からフォーム操作まで一連の業務フローが正常に完了することを確認"""
        login_page = TheInternetLoginPage(page)
        form_page = TheInternetFormPage(page)
        creds = test_users["the_internet"]["valid_user"]
        upload_file = Path(__file__).resolve().parent.parent.parent / "data" / "upload_sample.txt"

        # ステップ1: ログイン
        login_page.navigate_to_login()
        login_page.login(creds["username"], creds["password"])
        assert login_page.is_logged_in()
        evidence.capture("ログイン完了")

        # ステップ2: セキュアエリア確認
        flash = login_page.get_flash_message()
        assert "You logged into a secure area!" in flash
        evidence.capture("セキュアエリア確認")

        # ステップ3: ログアウト
        login_page.logout()
        assert "You logged out" in login_page.get_flash_message()
        evidence.capture("ログアウト完了")

        # ステップ4: チェックボックス操作
        form_page.navigate_to_checkboxes()
        form_page.toggle_checkbox(0)
        assert form_page.is_checkbox_checked(0)
        evidence.capture("チェックボックス操作")

        # ステップ5: ドロップダウン操作
        form_page.navigate_to_dropdown()
        form_page.select_dropdown_option("1")
        expect(form_page.dropdown).to_have_value("1")
        evidence.capture("ドロップダウン操作")

        # ステップ6: ファイルアップロード
        form_page.navigate_to_file_upload()
        form_page.upload_file(str(upload_file))
        assert form_page.get_uploaded_filename() == "upload_sample.txt"
        evidence.capture("ファイルアップロード完了")


def main():
    runner = TestRunner("test_e2e_portal_auth")
    session_id = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    test_users = load_test_users()
    all_evidence = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        instance = TestPortalAuthFlow()

        # (test_method, needs_test_users)
        test_specs = [
            (instance.test_login_success, True),
            (instance.test_login_failure, False),
            (instance.test_login_logout_relogin_cycle, True),
            (instance.test_checkbox_operations, False),
            (instance.test_dropdown_selection, False),
            (instance.test_file_upload, False),
            (instance.test_complete_portal_workflow, True),
        ]

        for test_func, needs_users in test_specs:
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                locale="ja-JP",
                timezone_id="Asia/Tokyo",
            )
            page = context.new_page()

            output_dir = Path(__file__).resolve().parent.parent.parent / "output"
            scenario_name = Path(__file__).stem.replace("test_e2e_", "")
            evidence_dir = output_dir / "evidence" / "scenarios" / scenario_name / session_id
            ev = Evidence(test_func.__name__, evidence_dir, page)

            if needs_users:
                runner.run(test_func, page, test_users, ev)
            else:
                runner.run(test_func, page, ev)

            all_evidence.append(ev.metadata())
            context.close()

        browser.close()

    scenario_name = Path(__file__).stem.replace("test_e2e_", "")
    generate_evidence_report(scenario_name, all_evidence, session_id)
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
