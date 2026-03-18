"""
test_e2e_cross_system.py - 複合シナリオ（API + UI連携）E2Eテスト

JTC（日本の大企業）システムでよく見られるパターンを模擬:
APIコールによるデータ準備・検証と、UIテストによるユーザー操作フローを
組み合わせたクロスシステム統合テスト。

APIバックエンドとして httpbin.org を使用し、
UIフロントエンドとして SauceDemo を使用する。
"""
import json

import pytest
from playwright.sync_api import Page, sync_playwright

from pages.saucedemo.login_page import SauceDemoLoginPage
from pages.saucedemo.inventory_page import SauceDemoInventoryPage
from pages.saucedemo.cart_page import SauceDemoCartPage
from pages.saucedemo.checkout_page import SauceDemoCheckoutPage


HTTPBIN_BASE_URL = "https://httpbin.org"


@pytest.fixture
def api_context():
    """httpbin.org 向け APIリクエストコンテキストを生成・破棄"""
    pw = sync_playwright().start()
    context = pw.request.new_context(base_url=HTTPBIN_BASE_URL)
    yield context
    context.dispose()
    pw.stop()


@pytest.fixture
def login_to_saucedemo(page: Page, test_users: dict):
    """SauceDemoにログインし、ログイン後のページオブジェクトを返す"""
    creds = test_users["saucedemo"]["standard_user"]
    login_page = SauceDemoLoginPage(page)
    login_page.navigate_to_login()
    login_page.login(creds["username"], creds["password"])
    inventory_page = SauceDemoInventoryPage(page)
    return inventory_page


@pytest.mark.slow
class TestCrossSystemFlow:
    """API + UI 連携のクロスシステム統合テストクラス"""

    # ------------------------------------------------------------------
    # 1. API疎通確認 → UI操作
    # ------------------------------------------------------------------
    def test_api_health_check_then_ui_flow(
        self, api_context, page: Page, test_users: dict, evidence
    ):
        """API疎通確認→UI操作: APIとUIの両方が正常動作することを確認"""

        # --- API: httpbin.org ヘルスチェック ---
        response = api_context.get("/get")
        assert response.status == 200, "httpbin.org へのGETリクエストが失敗"

        body = response.json()
        assert "url" in body, "レスポンスに url フィールドが存在しない"

        # --- UI: SauceDemoにログイン → 商品一覧表示確認 ---
        creds = test_users["saucedemo"]["standard_user"]
        login_page = SauceDemoLoginPage(page)
        login_page.navigate_to_login()
        evidence.capture("ログイン画面表示")
        login_page.login(creds["username"], creds["password"])

        inventory_page = SauceDemoInventoryPage(page)
        product_count = inventory_page.get_product_count()
        assert product_count > 0, "商品一覧に商品が表示されていない"

        evidence.capture("API疎通確認後_商品一覧表示")

    # ------------------------------------------------------------------
    # 2. APIデータ準備 → UI検証
    # ------------------------------------------------------------------
    def test_api_data_preparation_for_ui_verification(
        self, api_context, page: Page, test_users: dict, evidence
    ):
        """APIデータ準備→UI検証: APIとUIが独立して正常動作することを検証"""

        # --- API: ユーザー情報をPOSTで送信 ---
        user_payload = {
            "user_id": "USR-001",
            "name": "テスト太郎",
            "department": "品質管理部",
            "role": "テスター",
        }
        response = api_context.post("/post", data=json.dumps(user_payload), headers={
            "Content-Type": "application/json",
        })
        assert response.status == 200, "POSTリクエストが失敗"

        response_body = response.json()
        sent_data = json.loads(response_body["data"])
        assert sent_data["user_id"] == "USR-001", "送信データが正しく返却されない"
        assert sent_data["name"] == "テスト太郎", "ユーザー名が一致しない"

        # --- UI: SauceDemoにログインして商品データ表示を確認 ---
        creds = test_users["saucedemo"]["standard_user"]
        login_page = SauceDemoLoginPage(page)
        login_page.navigate_to_login()
        evidence.capture("ログイン画面表示")
        login_page.login(creds["username"], creds["password"])

        inventory_page = SauceDemoInventoryPage(page)
        product_names = inventory_page.get_product_names()
        assert len(product_names) > 0, "商品データが表示されていない"

        evidence.capture("APIデータ準備後_商品一覧確認")

    # ------------------------------------------------------------------
    # 3. API承認ワークフロー模擬
    # ------------------------------------------------------------------
    def test_api_mock_workflow_approval(
        self, api_context, page: Page, test_users: dict, evidence
    ):
        """API承認ワークフロー模擬: 申請→承認→結果確認→UI購買操作"""

        # --- Step 1: POST /post — 申請 ---
        application_data = {
            "application_id": "APP-2024-001",
            "type": "購買申請",
            "applicant": "山田太郎",
            "amount": 29990,
            "description": "テスト用備品購入",
        }
        step1_response = api_context.post("/post", data=json.dumps(application_data), headers={
            "Content-Type": "application/json",
        })
        assert step1_response.status == 200, "申請リクエストが失敗"
        step1_body = step1_response.json()
        assert "data" in step1_body, "申請レスポンスに data が存在しない"

        # --- Step 2: PUT /put — 承認 ---
        approval_data = {
            "application_id": "APP-2024-001",
            "status": "approved",
            "approver": "佐藤部長",
            "approved_at": "2024-01-15T10:00:00+09:00",
        }
        step2_response = api_context.put("/put", data=json.dumps(approval_data), headers={
            "Content-Type": "application/json",
        })
        assert step2_response.status == 200, "承認リクエストが失敗"
        step2_body = step2_response.json()
        approved = json.loads(step2_body["data"])
        assert approved["status"] == "approved", "承認ステータスが一致しない"

        # --- Step 3: GET /get — 結果確認 ---
        step3_response = api_context.get("/get", params={
            "application_id": "APP-2024-001",
        })
        assert step3_response.status == 200, "結果確認リクエストが失敗"

        # --- UI: 承認後の購買操作を模擬 ---
        creds = test_users["saucedemo"]["standard_user"]
        login_page = SauceDemoLoginPage(page)
        login_page.navigate_to_login()
        evidence.capture("承認ワークフロー_ログイン画面")
        login_page.login(creds["username"], creds["password"])

        inventory_page = SauceDemoInventoryPage(page)
        evidence.capture("承認後_商品一覧表示")
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        assert inventory_page.get_cart_count() == 1, "カートに商品が追加されていない"

        evidence.capture("承認後_カートに商品追加完了")

    # ------------------------------------------------------------------
    # 4. API/UI並行操作
    # ------------------------------------------------------------------
    def test_parallel_api_and_ui_operations(
        self, api_context, page: Page, test_users: dict, evidence
    ):
        """API/UI並行操作: 同一テスト内でAPIとUIの両方を操作し結果を検証"""

        # --- API: 複数のGETリクエスト ---
        # ヘッダー確認
        headers_response = api_context.get("/headers")
        assert headers_response.status == 200, "ヘッダー確認リクエストが失敗"
        headers_body = headers_response.json()
        assert "headers" in headers_body, "レスポンスに headers が存在しない"

        # IP確認
        ip_response = api_context.get("/ip")
        assert ip_response.status == 200, "IP確認リクエストが失敗"
        ip_body = ip_response.json()
        assert "origin" in ip_body, "レスポンスに origin（IP）が存在しない"

        # User-Agent確認
        ua_response = api_context.get("/user-agent")
        assert ua_response.status == 200, "User-Agent確認リクエストが失敗"
        ua_body = ua_response.json()
        assert "user-agent" in ua_body, "レスポンスに user-agent が存在しない"

        # --- UI: ログイン → 商品操作 ---
        creds = test_users["saucedemo"]["standard_user"]
        login_page = SauceDemoLoginPage(page)
        login_page.navigate_to_login()
        evidence.capture("並行操作_ログイン画面表示")
        login_page.login(creds["username"], creds["password"])

        inventory_page = SauceDemoInventoryPage(page)
        evidence.capture("並行操作_商品一覧表示")
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        inventory_page.add_product_to_cart("Sauce Labs Bike Light")
        assert inventory_page.get_cart_count() == 2, "カートの商品数が期待値と異なる"

        evidence.capture("並行操作_カートに2商品追加完了")

        # --- 最終検証: APIとUIの結果をまとめて確認 ---
        assert headers_response.status == 200
        assert ip_response.status == 200
        assert ua_response.status == 200
        assert inventory_page.get_cart_count() == 2

    # ------------------------------------------------------------------
    # 5. APIレスポンスヘッダー検証
    # ------------------------------------------------------------------
    def test_api_response_headers_verification(self, api_context):
        """APIレスポンスヘッダー検証: カスタムヘッダーおよび基本ヘッダーを確認"""

        # --- カスタムヘッダー付きレスポンスを取得 ---
        response = api_context.get("/response-headers", params={
            "X-Custom-Header": "TestValue",
            "X-Request-Id": "REQ-12345",
        })
        assert response.status == 200, "response-headers リクエストが失敗"

        headers = response.headers
        assert headers.get("x-custom-header") == "TestValue", \
            "カスタムヘッダー X-Custom-Header の値が一致しない"
        assert headers.get("x-request-id") == "REQ-12345", \
            "カスタムヘッダー X-Request-Id の値が一致しない"

        # --- Content-Type 等の基本ヘッダー確認 ---
        content_type = headers.get("content-type", "")
        assert "application/json" in content_type, \
            f"Content-Type が application/json でない: {content_type}"

    # ------------------------------------------------------------------
    # 6. エンドツーエンド統合テスト（メインシナリオ）
    # ------------------------------------------------------------------
    def test_end_to_end_with_api_validation(
        self, api_context, page: Page, test_users: dict, evidence
    ):
        """エンドツーエンド統合テスト: API検証を挟みながらUI購買フローを完遂"""

        # === Step 1: API — 注文データ送信 ===
        order_data = {
            "order_id": "ORD-2024-001",
            "customer": "テスト顧客",
            "items": [],
            "status": "pending",
        }
        step1_response = api_context.post("/post", data=json.dumps(order_data), headers={
            "Content-Type": "application/json",
        })
        assert step1_response.status == 200, "注文データ送信が失敗"
        step1_body = step1_response.json()
        assert "data" in step1_body, "注文レスポンスに data が存在しない"

        evidence.capture("Step1_API注文データ送信完了")

        # === Step 2: UI — SauceDemoにログイン ===
        creds = test_users["saucedemo"]["standard_user"]
        login_page = SauceDemoLoginPage(page)
        login_page.navigate_to_login()
        evidence.capture("Step2_ログイン画面表示")
        login_page.login(creds["username"], creds["password"])

        inventory_page = SauceDemoInventoryPage(page)
        assert inventory_page.get_product_count() > 0, "ログイン後に商品が表示されない"

        evidence.capture("Step2_ログイン後_商品一覧表示")

        # === Step 3: UI — 商品をカートに追加 ===
        inventory_page.add_product_to_cart("Sauce Labs Backpack")
        inventory_page.add_product_to_cart("Sauce Labs Bolt T-Shirt")
        assert inventory_page.get_cart_count() == 2, "カートの商品数が期待値と異なる"

        product_names = inventory_page.get_product_names()

        evidence.capture("Step3_カートに商品追加完了")

        # === Step 4: API — カート内容をAPIで送信（UIで取得した商品名を使用） ===
        cart_data = {
            "order_id": "ORD-2024-001",
            "cart_items": product_names,
            "cart_count": 2,
        }
        step4_response = api_context.post("/post", data=json.dumps(cart_data), headers={
            "Content-Type": "application/json",
        })
        assert step4_response.status == 200, "カート内容送信が失敗"
        step4_body = step4_response.json()
        sent_cart = json.loads(step4_body["data"])
        assert sent_cart["order_id"] == "ORD-2024-001", "注文IDが一致しない"
        assert len(sent_cart["cart_items"]) > 0, "カートアイテムが空"

        # === Step 5: UI — チェックアウト完了 ===
        inventory_page.go_to_cart()
        cart_page = SauceDemoCartPage(page)
        evidence.capture("Step5_カート画面表示")
        cart_page.proceed_to_checkout()

        checkout_page = SauceDemoCheckoutPage(page)
        checkout_page.fill_info("太郎", "テスト", "100-0001")
        evidence.capture("Step5_チェックアウト情報入力完了")
        checkout_page.continue_checkout()
        checkout_page.finish_order()

        complete_header = checkout_page.get_complete_header()
        assert complete_header is not None, "注文完了ヘッダーが表示されない"

        evidence.capture("Step5_チェックアウト完了")

        # === Step 6: API — 注文完了通知送信 ===
        completion_data = {
            "order_id": "ORD-2024-001",
            "status": "completed",
            "confirmation": complete_header,
            "items_ordered": 2,
        }
        step6_response = api_context.post("/post", data=json.dumps(completion_data), headers={
            "Content-Type": "application/json",
        })
        assert step6_response.status == 200, "注文完了通知の送信が失敗"
        step6_body = step6_response.json()
        sent_completion = json.loads(step6_body["data"])
        assert sent_completion["status"] == "completed", "完了ステータスが一致しない"

        evidence.capture("Step6_注文完了通知送信後")
