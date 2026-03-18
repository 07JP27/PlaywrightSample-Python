"""
test_e2e_application_form.py - 申請ワークフロー E2Eシナリオテスト

DemoQA（https://demoqa.com/）を対象とした
申請フォーム送信・Webテーブル操作の業務フロー全体を検証するエンドツーエンドテスト。

テスト対象:
  - 学生登録フォーム送信・バリデーション
  - Webテーブルのレコード追加・検索・編集・削除
  - 統合申請ワークフロー（CRUD操作を通した一連のデータ整合性検証）
"""
import re

import pytest
from playwright.sync_api import Page, expect

from pages.demoqa.form_page import DemoQAFormPage
from pages.demoqa.web_tables_page import DemoQAWebTablesPage


def _block_ads(route):
    """広告リクエストをブロックするルートハンドラ"""
    route.abort()


def _setup_ad_blocker(page: Page):
    """ページに広告ブロッカーを設定する"""
    page.route("**/*doubleclick.net*", _block_ads)
    page.route("**/*googlesyndication.com*", _block_ads)
    page.route("**/*googleadservices.com*", _block_ads)
    page.route("**/*amazon-adsystem.com*", _block_ads)


def _remove_fixed_ban(page: Page):
    """DemoQAの固定バナー・広告オーバーレイを除去する"""
    page.evaluate("""
        () => {
            // 固定フッター広告を除去
            const fixedBan = document.getElementById('fixedban');
            if (fixedBan) fixedBan.remove();
            // iframe広告を除去
            document.querySelectorAll('iframe').forEach(el => el.remove());
            // Google Adsenseコンテナを除去
            document.querySelectorAll('[id^="google_ads"]').forEach(el => el.remove());
            document.querySelectorAll('.ad, .ads, [class*="adsbygoogle"]').forEach(el => el.remove());
        }
    """)


@pytest.mark.slow
class TestApplicationFormFlow:
    """申請ワークフローのE2Eシナリオテストクラス"""

    # ------------------------------------------------------------------ #
    # 1. 申請フォーム送信
    # ------------------------------------------------------------------ #
    def test_submit_practice_form(self, page: Page, test_employees: dict, evidence):
        """申請フォーム送信 — 基本情報を入力してフォームを送信し、確認モーダルを検証する"""
        _setup_ad_blocker(page)
        form_page = DemoQAFormPage(page)
        emp = test_employees["employees"][0]

        # フォームページに遷移
        form_page.navigate_to_form()
        _remove_fixed_ban(page)
        evidence.capture("フォーム画面表示")

        # 従業員データで基本情報を入力
        form_page.fill_name(emp["first_name"], emp["last_name"])
        form_page.fill_email(emp["email"])
        form_page.select_gender("Male")
        form_page.fill_mobile(emp["mobile"])
        evidence.capture("基本情報入力完了")

        # フォーム送信
        form_page.submit_form()

        # 確認モーダルが表示されることを確認
        expect(form_page.confirmation_modal).to_be_visible()
        evidence.capture("フォーム送信後_モーダル表示")

        # モーダル内容に入力した名前が含まれることを確認
        modal_data = form_page.get_confirmation_modal()
        full_name = f"{emp['first_name']} {emp['last_name']}"
        assert "Student Name" in modal_data, "モーダルに Student Name ラベルがありません"
        assert full_name in modal_data["Student Name"], (
            f"モーダルの名前が一致しません: 期待値='{full_name}', 実際='{modal_data['Student Name']}'"
        )
        evidence.capture("モーダル内容確認")

    # ------------------------------------------------------------------ #
    # 2. 必須フィールドバリデーション
    # ------------------------------------------------------------------ #
    def test_form_required_fields_validation(self, page: Page, evidence):
        """必須フィールドバリデーション — 空のまま送信し、バリデーションエラーを確認する"""
        _setup_ad_blocker(page)
        form_page = DemoQAFormPage(page)

        # フォームページに遷移
        form_page.navigate_to_form()
        _remove_fixed_ban(page)
        evidence.capture("フォーム画面表示")

        # 空のまま送信を試行
        form_page.submit_form()

        # 送信後、フォームに was-validated クラスが付与されることを確認
        form_element = page.locator("form#userForm")
        expect(form_element).to_have_class(re.compile(r"was-validated"))

        # 必須フィールド（名前、携帯番号）にバリデーションエラーが適用されることを確認
        for field in [form_page.first_name, form_page.last_name, form_page.mobile]:
            is_invalid = field.evaluate(
                "el => !el.validity.valid"
            )
            assert is_invalid, "必須フィールドがinvalid状態になっていません"
        evidence.capture("空送信後_バリデーションエラー")

    # ------------------------------------------------------------------ #
    # 3. テーブルへのレコード追加
    # ------------------------------------------------------------------ #
    def test_web_table_add_record(self, page: Page, test_employees: dict, evidence):
        """テーブルへのレコード追加 — 新しいレコードを追加し、テーブルに反映されることを確認する"""
        _setup_ad_blocker(page)
        tables_page = DemoQAWebTablesPage(page)
        emp = test_employees["employees"][0]

        # Web Tablesページに遷移
        tables_page.navigate_to_web_tables()
        _remove_fixed_ban(page)
        evidence.capture("テーブル画面_初期状態")

        # 初期レコード数を確認
        initial_count = tables_page.get_row_count()

        # 新しいレコードを追加
        tables_page.add_record(
            first_name=emp["first_name"],
            last_name=emp["last_name"],
            email=emp["email"],
            age=emp["age"],
            salary=emp["salary"],
            department=emp["department"],
        )
        evidence.capture("レコード追加フォーム")

        # レコード数が1増えていることを確認
        new_count = tables_page.get_row_count()
        assert new_count == initial_count + 1, (
            f"レコード数が正しくありません: 期待値={initial_count + 1}, 実際={new_count}"
        )

        # テーブルデータに追加した従業員の名前が含まれることを確認
        table_data = tables_page.get_table_data()
        first_names = [row["First Name"] for row in table_data]
        assert emp["first_name"] in first_names, (
            f"テーブルに追加したレコードが見つかりません: {emp['first_name']}"
        )
        evidence.capture("追加完了後_テーブル表示")

    # ------------------------------------------------------------------ #
    # 4. テーブル検索
    # ------------------------------------------------------------------ #
    def test_web_table_search(self, page: Page, test_employees: dict, evidence):
        """テーブル検索 — レコード追加後に検索し、結果の表示・クリアを確認する"""
        _setup_ad_blocker(page)
        tables_page = DemoQAWebTablesPage(page)
        emp = test_employees["employees"][0]

        # Web Tablesページに遷移
        tables_page.navigate_to_web_tables()
        _remove_fixed_ban(page)
        evidence.capture("テーブル初期状態")

        # テスト用レコードを追加
        tables_page.add_record(
            first_name=emp["first_name"],
            last_name=emp["last_name"],
            email=emp["email"],
            age=emp["age"],
            salary=emp["salary"],
            department=emp["department"],
        )

        # 追加後の全件数を記録
        total_count = tables_page.get_row_count()
        evidence.capture("レコード追加後")

        # 名前で検索
        tables_page.search(emp["first_name"])
        page.wait_for_timeout(500)

        # 検索結果にそのレコードが表示されることを確認
        search_data = tables_page.get_table_data()
        assert len(search_data) >= 1, "検索結果が0件です"
        assert any(
            row["First Name"] == emp["first_name"] for row in search_data
        ), f"検索結果に {emp['first_name']} が含まれていません"
        evidence.capture("検索実行後")

        # 検索クリア後に全件表示に戻ることを確認
        tables_page.search("")
        page.wait_for_timeout(500)
        cleared_count = tables_page.get_row_count()
        assert cleared_count == total_count, (
            f"検索クリア後のレコード数が一致しません: 期待値={total_count}, 実際={cleared_count}"
        )
        evidence.capture("検索クリア後")

    # ------------------------------------------------------------------ #
    # 5. テーブルレコード編集
    # ------------------------------------------------------------------ #
    def test_web_table_edit_record(self, page: Page, evidence):
        """テーブルレコード編集 — 既存レコードの部門を編集し、変更が反映されることを確認する"""
        _setup_ad_blocker(page)
        tables_page = DemoQAWebTablesPage(page)
        new_department = "QA"

        # Web Tablesページに遷移
        tables_page.navigate_to_web_tables()
        _remove_fixed_ban(page)
        evidence.capture("テーブル初期状態")

        # 編集前の最初のレコードの部門を取得
        original_data = tables_page.get_table_data()
        assert len(original_data) >= 1, "編集対象のレコードがありません"
        original_department = original_data[0]["Department"]

        # 最初のレコードの部門を編集
        tables_page.edit_record(0, department=new_department)
        evidence.capture("編集フォーム表示")

        # 編集後のテーブルデータで変更が反映されていることを確認
        updated_data = tables_page.get_table_data()
        assert updated_data[0]["Department"] == new_department, (
            f"部門が更新されていません: 期待値='{new_department}', "
            f"実際='{updated_data[0]['Department']}'"
        )
        assert updated_data[0]["Department"] != original_department, (
            "部門が変更前と同じです"
        )
        evidence.capture("編集完了後_テーブル表示")

    # ------------------------------------------------------------------ #
    # 6. テーブルレコード削除
    # ------------------------------------------------------------------ #
    def test_web_table_delete_record(self, page: Page, evidence):
        """テーブルレコード削除 — レコードを削除し、件数が減少することを確認する"""
        _setup_ad_blocker(page)
        tables_page = DemoQAWebTablesPage(page)

        # Web Tablesページに遷移
        tables_page.navigate_to_web_tables()
        _remove_fixed_ban(page)

        # 初期レコード数を確認
        initial_count = tables_page.get_row_count()
        assert initial_count >= 1, "削除対象のレコードがありません"
        evidence.capture("テーブル初期状態")

        # 最初のレコードを削除
        tables_page.delete_record(0)

        # レコード数が1減っていることを確認
        new_count = tables_page.get_row_count()
        assert new_count == initial_count - 1, (
            f"レコード数が正しくありません: 期待値={initial_count - 1}, 実際={new_count}"
        )
        evidence.capture("削除後_テーブル表示")

    # ------------------------------------------------------------------ #
    # 7. 統合申請ワークフロー（メインシナリオ）
    # ------------------------------------------------------------------ #
    def test_complete_application_workflow(
        self, page: Page, test_employees: dict, evidence
    ):
        """統合申請ワークフロー — レコードの追加→検索→編集→検索確認→削除を一連で検証する

        各ステップでエビデンスを保存し、
        全操作の前後でデータの整合性を確認する。
        """
        _setup_ad_blocker(page)
        tables_page = DemoQAWebTablesPage(page)
        emp = test_employees["employees"][0]
        updated_department = "DevOps"

        # Web Tablesページに遷移
        tables_page.navigate_to_web_tables()
        _remove_fixed_ban(page)

        # 初期状態を記録
        initial_count = tables_page.get_row_count()
        evidence.capture("ワークフロー_初期状態")

        # ステップ1: レコード追加
        tables_page.add_record(
            first_name=emp["first_name"],
            last_name=emp["last_name"],
            email=emp["email"],
            age=emp["age"],
            salary=emp["salary"],
            department=emp["department"],
        )
        after_add_count = tables_page.get_row_count()
        assert after_add_count == initial_count + 1, (
            f"追加後のレコード数が不正: 期待値={initial_count + 1}, 実際={after_add_count}"
        )
        evidence.capture("レコード追加後")

        # ステップ2: 検索で追加したレコードを確認
        tables_page.search(emp["first_name"])
        page.wait_for_timeout(500)
        search_results = tables_page.get_table_data()
        assert any(
            row["First Name"] == emp["first_name"] for row in search_results
        ), f"検索で追加したレコードが見つかりません: {emp['first_name']}"
        evidence.capture("検索結果表示")

        # 検索をクリアして全件表示に戻す
        tables_page.search("")
        page.wait_for_timeout(500)

        # ステップ3: 追加したレコードの部門を編集
        # 追加したレコードの行インデックスを特定
        table_data = tables_page.get_table_data()
        target_index = next(
            i for i, row in enumerate(table_data)
            if row["First Name"] == emp["first_name"]
        )
        tables_page.edit_record(target_index, department=updated_department)

        # 編集結果を確認
        edited_data = tables_page.get_table_data()
        edited_row = next(
            row for row in edited_data
            if row["First Name"] == emp["first_name"]
        )
        assert edited_row["Department"] == updated_department, (
            f"部門の編集が反映されていません: 期待値='{updated_department}', "
            f"実際='{edited_row['Department']}'"
        )
        evidence.capture("編集完了後")

        # ステップ4: 検索で編集後のデータを確認
        tables_page.search(emp["first_name"])
        page.wait_for_timeout(500)
        verify_results = tables_page.get_table_data()
        verified_row = next(
            row for row in verify_results
            if row["First Name"] == emp["first_name"]
        )
        assert verified_row["Department"] == updated_department, (
            "検索結果で編集後の部門が反映されていません"
        )
        evidence.capture("編集後_検索確認")

        # 検索をクリア
        tables_page.search("")
        page.wait_for_timeout(500)

        # ステップ5: 追加したレコードを削除
        table_data_before_delete = tables_page.get_table_data()
        delete_index = next(
            i for i, row in enumerate(table_data_before_delete)
            if row["First Name"] == emp["first_name"]
        )
        count_before_delete = tables_page.get_row_count()
        tables_page.delete_record(delete_index)

        # 削除後の検証
        after_delete_count = tables_page.get_row_count()
        assert after_delete_count == count_before_delete - 1, (
            f"削除後のレコード数が不正: 期待値={count_before_delete - 1}, "
            f"実際={after_delete_count}"
        )

        # 削除したレコードがテーブルに存在しないことを確認
        final_data = tables_page.get_table_data()
        assert not any(
            row["First Name"] == emp["first_name"] for row in final_data
        ), "削除したレコードがまだテーブルに残っています"

        # 最終状態が初期状態と同じレコード数であることを確認
        assert after_delete_count == initial_count, (
            f"最終レコード数が初期状態と一致しません: 初期={initial_count}, "
            f"最終={after_delete_count}"
        )
        evidence.capture("削除後_最終状態")
