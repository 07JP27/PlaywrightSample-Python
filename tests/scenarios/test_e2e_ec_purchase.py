"""
test_e2e_ec_purchase.py - EC購買フロー E2Eシナリオテスト

SauceDemo（https://www.saucedemo.com/）を対象とした
ECサイトの購買フロー全体を検証するエンドツーエンドテスト。

テスト対象:
  - ログイン・認証
  - 商品一覧表示・ソート
  - カート操作（追加・削除・買い物続行）
  - チェックアウト（情報入力・バリデーション・注文確定）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import Page, expect, sync_playwright
from runner import TestRunner
from evidence import Evidence, load_test_users, generate_evidence_report

from pages.saucedemo import (
    SauceDemoLoginPage,
    SauceDemoInventoryPage,
    SauceDemoCartPage,
    SauceDemoCheckoutPage,
)


class TestECPurchaseFlow:
    """EC購買フロー E2Eシナリオテストクラス"""

    def _login_as_standard_user(
        self, page: Page, test_users: dict
    ) -> SauceDemoInventoryPage:
        """standard_user でログインし、商品一覧ページオブジェクトを返すヘルパー"""
        login_page = SauceDemoLoginPage(page)
        login_page.navigate_to_login()
        user = test_users["saucedemo"]["standard_user"]
        login_page.login(user["username"], user["password"])
        return SauceDemoInventoryPage(page)

    # ------------------------------------------------------------------ #
    # 1. ログイン→商品一覧表示確認
    # ------------------------------------------------------------------ #
    def test_login_and_view_products(self, page: Page, test_users: dict, evidence):
        """ログインして商品一覧が正しく表示されることを確認する"""
        # ログインページに遷移し、standard_user でログイン
        inventory_page = self._login_as_standard_user(page, test_users)
        evidence.capture("ログイン完了_商品一覧表示")

        # 商品一覧ページに遷移していることを確認
        expect(page).to_have_url(SauceDemoInventoryPage.URL)

        # 商品が6件表示されていることを確認
        assert inventory_page.get_product_count() == 6
        evidence.capture("商品一覧_6件表示確認")

    # ------------------------------------------------------------------ #
    # 2. 商品ソート（価格順）
    # ------------------------------------------------------------------ #
    def test_sort_products_by_price(self, page: Page, test_users: dict, evidence):
        """商品を価格順にソートし、並び順が正しいことを確認する"""
        inventory_page = self._login_as_standard_user(page, test_users)
        evidence.capture("ログイン完了_商品一覧表示")

        # 価格安い順（lohi）でソート
        inventory_page.sort_products("lohi")
        evidence.capture("価格安い順ソート実行後")
        prices_asc = inventory_page.get_product_prices()
        # "$" を除去して数値に変換
        prices_asc_float = [float(p.replace("$", "")) for p in prices_asc]
        # 最初の商品が最安値であることを確認
        assert prices_asc_float[0] == min(prices_asc_float)
        evidence.capture("価格安い順ソート_最安値確認")

        # 価格高い順（hilo）でソート
        inventory_page.sort_products("hilo")
        evidence.capture("価格高い順ソート実行後")
        prices_desc = inventory_page.get_product_prices()
        prices_desc_float = [float(p.replace("$", "")) for p in prices_desc]
        # 最初の商品が最高値であることを確認
        assert prices_desc_float[0] == max(prices_desc_float)
        evidence.capture("価格高い順ソート_最高値確認")

    # ------------------------------------------------------------------ #
    # 3. 複数商品カート追加
    # ------------------------------------------------------------------ #
    def test_add_multiple_products_to_cart(self, page: Page, test_users: dict, evidence):
        """複数商品をカートに追加し、バッジとカート内容を確認する"""
        inventory_page = self._login_as_standard_user(page, test_users)
        evidence.capture("ログイン完了_商品一覧表示")

        # 2つの商品をカートに追加
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        evidence.capture("商品1_Backpack追加後")
        inventory_page.add_product_to_cart("Sauce Labs Bike Light")
        evidence.capture("商品2_BikeLight追加後")

        # カートバッジが2を表示していることを確認
        assert inventory_page.get_cart_count() == 2
        evidence.capture("カートバッジ_2件表示確認")

        # カートに遷移して2商品が含まれていることを確認
        inventory_page.go_to_cart()
        cart_page = SauceDemoCartPage(page)
        evidence.capture("カート画面遷移後")
        cart_items = cart_page.get_cart_items()
        assert len(cart_items) == 2
        assert "Sauce Labs Backpack" in cart_items
        assert "Sauce Labs Bike Light" in cart_items
        evidence.capture("カート内容_2商品確認")

    # ------------------------------------------------------------------ #
    # 4. カートから商品削除
    # ------------------------------------------------------------------ #
    def test_remove_product_from_cart(self, page: Page, test_users: dict, evidence):
        """カートから商品を削除し、バッジが更新されることを確認する"""
        inventory_page = self._login_as_standard_user(page, test_users)
        evidence.capture("ログイン完了_商品一覧表示")

        # 2つの商品を追加
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        inventory_page.add_product_to_cart("Sauce Labs Bike Light")
        assert inventory_page.get_cart_count() == 2
        evidence.capture("商品2件追加_カートバッジ2確認")

        # 1つを削除
        inventory_page.remove_product_from_cart("Sauce Labs Backpack")
        evidence.capture("Backpack削除後")

        # カートバッジが1に更新されていることを確認
        assert inventory_page.get_cart_count() == 1
        evidence.capture("カートバッジ_1件に更新確認")

    # ------------------------------------------------------------------ #
    # 5. 購買フロー完走（メインシナリオ）
    # ------------------------------------------------------------------ #
    def test_complete_purchase_flow(self, page: Page, test_users: dict, evidence):
        """ログインから注文完了までの購買フロー全体を検証する"""
        # ステップ1: ログイン
        inventory_page = self._login_as_standard_user(page, test_users)
        evidence.capture("ログイン完了_商品一覧表示")

        # ステップ2: 商品2点をカートに追加
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        evidence.capture("商品1_Backpack追加後")
        inventory_page.add_product_to_cart("Sauce Labs Bike Light")
        assert inventory_page.get_cart_count() == 2
        evidence.capture("商品2点追加_カートバッジ2確認")

        # ステップ3: カート確認
        inventory_page.go_to_cart()
        cart_page = SauceDemoCartPage(page)
        assert cart_page.get_item_count() == 2
        evidence.capture("カート画面_2件確認")

        # ステップ4: チェックアウト情報入力
        cart_page.proceed_to_checkout()
        evidence.capture("チェックアウト情報入力画面")
        checkout_page = SauceDemoCheckoutPage(page)
        checkout_page.fill_info("太郎", "田中", "100-0001")
        evidence.capture("チェックアウト情報入力完了")

        # ステップ5: 注文概要確認
        checkout_page.continue_checkout()
        summary_total = checkout_page.get_summary_total()
        assert summary_total  # 合計金額が表示されていること
        evidence.capture("注文概要_合計金額表示確認")

        # ステップ6: 注文確定
        checkout_page.finish_order()
        evidence.capture("注文確定_完了画面表示")

        # 完了画面で "Thank you for your order!" を確認
        complete_text = checkout_page.get_complete_header()
        assert complete_text == "Thank you for your order!"
        evidence.capture("注文完了メッセージ確認")

    # ------------------------------------------------------------------ #
    # 6. チェックアウトバリデーション
    # ------------------------------------------------------------------ #
    def test_checkout_validation_error(self, page: Page, test_users: dict, evidence):
        """チェックアウト時に名前未入力でバリデーションエラーが表示されることを確認する"""
        inventory_page = self._login_as_standard_user(page, test_users)
        evidence.capture("ログイン完了_商品一覧表示")

        # 商品を追加してチェックアウトへ進む
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        evidence.capture("商品追加後_Backpack")
        inventory_page.go_to_cart()

        cart_page = SauceDemoCartPage(page)
        evidence.capture("カート画面遷移後")
        cart_page.proceed_to_checkout()

        # 名前を空のまま Continue をクリック
        checkout_page = SauceDemoCheckoutPage(page)
        evidence.capture("チェックアウト情報入力画面_未入力状態")
        checkout_page.continue_checkout()

        # エラーメッセージが表示されることを確認
        error_msg = checkout_page.get_error_message()
        assert error_msg is not None
        assert len(error_msg) > 0
        evidence.capture("バリデーションエラー表示確認")

    # ------------------------------------------------------------------ #
    # 7. ロックアウトユーザーの拒否
    # ------------------------------------------------------------------ #
    def test_locked_out_user_cannot_login(self, page: Page, test_users: dict, evidence):
        """ロックアウトユーザーがログインできないことを確認する"""
        login_page = SauceDemoLoginPage(page)
        login_page.navigate_to_login()
        evidence.capture("ログイン画面表示")

        # locked_out_user でログイン試行
        user = test_users["saucedemo"]["locked_out_user"]
        login_page.login(user["username"], user["password"])
        evidence.capture("ロックアウトユーザー_ログイン試行後")

        # エラーメッセージが表示されることを確認
        error_msg = login_page.get_error_message()
        assert "locked out" in error_msg.lower()
        evidence.capture("ロックアウトエラーメッセージ確認")

    # ------------------------------------------------------------------ #
    # 8. カートから買い物続行
    # ------------------------------------------------------------------ #
    def test_continue_shopping_from_cart(self, page: Page, test_users: dict, evidence):
        """カートから「買い物を続ける」で商品一覧に戻れることを確認する"""
        inventory_page = self._login_as_standard_user(page, test_users)
        evidence.capture("ログイン完了_商品一覧表示")

        # 商品を追加してカートへ遷移
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        evidence.capture("商品追加後_Backpack")
        inventory_page.go_to_cart()
        evidence.capture("カート画面遷移後")

        # 「買い物を続ける」をクリック
        cart_page = SauceDemoCartPage(page)
        cart_page.continue_shopping()
        evidence.capture("買い物を続ける_商品一覧に戻る")

        # 商品一覧ページに戻ることを確認
        expect(page).to_have_url(SauceDemoInventoryPage.URL)
        evidence.capture("商品一覧ページURL確認")


def main():
    runner = TestRunner("test_e2e_ec_purchase")
    session_id = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    test_users = load_test_users()
    all_evidence = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        instance = TestECPurchaseFlow()

        test_methods = [
            instance.test_login_and_view_products,
            instance.test_sort_products_by_price,
            instance.test_add_multiple_products_to_cart,
            instance.test_remove_product_from_cart,
            instance.test_complete_purchase_flow,
            instance.test_checkout_validation_error,
            instance.test_locked_out_user_cannot_login,
            instance.test_continue_shopping_from_cart,
        ]

        for test_func in test_methods:
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

            runner.run(test_func, page, test_users, ev)
            all_evidence.append(ev.metadata())
            context.close()

        browser.close()

    scenario_name = Path(__file__).stem.replace("test_e2e_", "")
    generate_evidence_report(scenario_name, all_evidence, session_id)
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
