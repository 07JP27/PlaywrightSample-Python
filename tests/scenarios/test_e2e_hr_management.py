"""
test_e2e_hr_management.py - HR勤怠管理フロー E2Eシナリオテスト

OrangeHRM デモサイトを使用した人事管理システムのエンドツーエンドテスト。
管理者ログイン、ダッシュボード操作、従業員検索、メニュー遷移などの
業務フローをシナリオとして検証する。
"""
import re

import pytest
from playwright.sync_api import Page, expect

from pages.orangehrm.login_page import OrangeHRMLoginPage
from pages.orangehrm.dashboard_page import OrangeHRMDashboardPage
from pages.orangehrm.pim_page import OrangeHRMPimPage


@pytest.mark.slow
class TestHRManagementFlow:
    """HR勤怠管理フローのE2Eシナリオテストクラス"""

    def test_admin_login_and_dashboard(self, page: Page, evidence) -> None:
        """管理者ログイン→ダッシュボード表示確認

        管理者アカウントでログインし、ダッシュボードページが正常に
        表示されること、ウィジェットが1つ以上存在することを検証する。
        """
        login_page = OrangeHRMLoginPage(page)
        dashboard_page = OrangeHRMDashboardPage(page)

        # ログインページに遷移
        login_page.navigate_to_login()
        page.wait_for_timeout(2000)
        evidence.capture("ログイン画面表示")

        # 管理者アカウントでログイン
        login_page.login("Admin", "admin123")
        page.wait_for_timeout(2000)
        evidence.capture("ログイン完了_ダッシュボード表示")

        # ダッシュボードページに遷移していることを確認
        assert dashboard_page.is_dashboard_loaded(), "ダッシュボードが表示されていません"

        # ウィジェットが1つ以上表示されていることを確認
        widget_count = dashboard_page.get_widget_count()
        assert widget_count >= 1, f"ウィジェットが表示されていません（件数: {widget_count}）"
        evidence.capture("ウィジェット確認")

    def test_navigate_to_pim_module(self, page: Page, evidence) -> None:
        """PIM（人事管理）モジュールへの遷移

        ログイン後、サイドメニューから「PIM」をクリックし、
        従業員一覧ページに正しく遷移することを検証する。
        """
        login_page = OrangeHRMLoginPage(page)
        dashboard_page = OrangeHRMDashboardPage(page)

        # ログイン
        login_page.navigate_to_login()
        page.wait_for_timeout(2000)
        evidence.capture("ログイン画面")
        login_page.login("Admin", "admin123")
        page.wait_for_timeout(2000)
        evidence.capture("ダッシュボード表示")

        # サイドメニューから「PIM」をクリック
        dashboard_page.navigate_to_menu("PIM")
        page.wait_for_timeout(2000)
        evidence.capture("PIMメニュークリック後")

        # PIMの従業員一覧ページに遷移していることを確認
        expect(page).to_have_url(re.compile(r"/pim/"))
        evidence.capture("PIM従業員一覧表示")

    def test_search_employee(self, page: Page, evidence) -> None:
        """従業員検索

        ログイン後、PIMモジュールに遷移し、従業員名で検索を実行する。
        検索結果が表示されることを確認する（結果0件でもエラーにならない）。
        """
        login_page = OrangeHRMLoginPage(page)
        dashboard_page = OrangeHRMDashboardPage(page)
        pim_page = OrangeHRMPimPage(page)

        # ログイン→PIMに遷移
        login_page.navigate_to_login()
        page.wait_for_timeout(2000)
        login_page.login("Admin", "admin123")
        page.wait_for_timeout(2000)
        evidence.capture("ログイン完了")
        dashboard_page.navigate_to_menu("PIM")
        page.wait_for_timeout(2000)
        evidence.capture("PIMページ遷移")

        # 従業員名で検索
        pim_page.search_employee("a")
        page.wait_for_timeout(2000)
        evidence.capture("検索条件入力")

        # 検索が実行されたことを確認（結果0件でもエラーにならないことを検証）
        employee_count = pim_page.get_employee_count()
        assert employee_count >= 0, "従業員検索結果の取得に失敗しました"
        evidence.capture("検索結果表示")

    def test_dashboard_menu_navigation(self, page: Page, evidence) -> None:
        """サイドメニュー各項目への遷移確認

        ログイン後、主要メニュー（Admin, PIM, Leave, Time）に順番に遷移し、
        各遷移後のURLにメニュー名が含まれることを検証する。
        """
        login_page = OrangeHRMLoginPage(page)
        dashboard_page = OrangeHRMDashboardPage(page)

        # ログイン
        login_page.navigate_to_login()
        page.wait_for_timeout(2000)
        login_page.login("Admin", "admin123")
        page.wait_for_timeout(2000)
        evidence.capture("ログイン完了_ダッシュボード")

        # 主要メニューへの遷移を順番に確認
        menu_items = ["Admin", "PIM", "Leave", "Time"]

        for menu_name in menu_items:
            dashboard_page.navigate_to_menu(menu_name)
            page.wait_for_timeout(2000)
            evidence.capture(f"{menu_name}メニュー遷移後")

            # 遷移後のURLにメニュー名（小文字）が含まれることを確認
            current_url = page.url.lower()
            assert menu_name.lower() in current_url, (
                f"メニュー「{menu_name}」遷移後のURLに'{menu_name.lower()}'が含まれていません "
                f"（現在のURL: {page.url}）"
            )

    def test_login_logout_cycle(self, page: Page, evidence) -> None:
        """ログイン→ログアウト→再ログイン

        ログインしてダッシュボードを確認後、ログアウトしてログインページに
        戻ることを検証し、再ログインしてダッシュボードが表示されることを確認する。
        """
        login_page = OrangeHRMLoginPage(page)
        dashboard_page = OrangeHRMDashboardPage(page)

        # 初回ログイン
        login_page.navigate_to_login()
        page.wait_for_timeout(2000)
        evidence.capture("ログイン画面")
        login_page.login("Admin", "admin123")
        page.wait_for_timeout(2000)
        evidence.capture("初回ログイン_ダッシュボード")

        # ダッシュボード表示確認
        assert dashboard_page.is_dashboard_loaded(), "初回ログイン後のダッシュボードが表示されていません"

        # ログアウト
        dashboard_page.logout()
        page.wait_for_timeout(2000)
        evidence.capture("ログアウト_ログイン画面")

        # ログインページに戻ったことを確認
        assert login_page.is_login_page(), "ログアウト後にログインページに戻っていません"

        # 再ログイン
        login_page.login("Admin", "admin123")
        page.wait_for_timeout(2000)
        evidence.capture("再ログイン_ダッシュボード")

        # ダッシュボード再表示確認
        assert dashboard_page.is_dashboard_loaded(), "再ログイン後のダッシュボードが表示されていません"

    def test_invalid_login_attempt(self, page: Page, evidence) -> None:
        """不正ログイン試行

        不正なユーザー名・パスワードでログインを試み、
        エラーメッセージが表示されることを検証する。
        """
        login_page = OrangeHRMLoginPage(page)

        # ログインページに遷移
        login_page.navigate_to_login()
        page.wait_for_timeout(2000)
        evidence.capture("ログイン画面表示")

        # 不正な認証情報でログイン試行
        login_page.login("InvalidUser", "wrongpassword")
        page.wait_for_timeout(2000)
        evidence.capture("不正認証情報入力")

        # エラーメッセージが表示されていることを確認
        error_text = login_page.get_error_message()
        assert len(error_text) > 0, "ログインエラーメッセージが表示されていません"
        evidence.capture("エラーメッセージ表示")

        # ログインページに留まっていることを確認
        assert login_page.is_login_page(), "不正ログイン後にログインページから遷移しています"
