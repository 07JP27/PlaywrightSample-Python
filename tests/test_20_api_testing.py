"""
test_20_api_testing.py - API テストのサンプル

ブラウザを使わずに REST API エンドポイントを直接テストする方法を示す。
Playwright の APIRequestContext を使用してHTTPリクエストを送信する。
"""

import pytest
from playwright.sync_api import Playwright, expect


# ─────────────────────────────────────────────
# 1. GET リクエスト
# ─────────────────────────────────────────────

def test_get_request(playwright: Playwright):
    """GET リクエストを送信し、レスポンスを検証する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get("/get")
    assert response.ok
    assert response.status == 200

    data = response.json()
    assert "url" in data
    assert data["url"] == "https://httpbin.org/get"
    api_context.dispose()


def test_get_request_with_query_params(playwright: Playwright):
    """GET リクエストにクエリパラメータを付与する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    # params でクエリパラメータを指定
    response = api_context.get("/get", params={"key": "value", "lang": "ja"})
    assert response.ok

    data = response.json()
    assert data["args"]["key"] == "value"
    assert data["args"]["lang"] == "ja"
    api_context.dispose()


# ─────────────────────────────────────────────
# 2. POST リクエスト
# ─────────────────────────────────────────────

def test_post_request_with_json(playwright: Playwright):
    """POST リクエストで JSON データを送信する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    payload = {"name": "テスト太郎", "age": 30}
    response = api_context.post("/post", data=payload)
    assert response.ok
    assert response.status == 200

    data = response.json()
    # httpbin は送信されたデータを json フィールドで返す
    assert data["json"]["name"] == "テスト太郎"
    assert data["json"]["age"] == 30
    api_context.dispose()


def test_post_request_with_form_data(playwright: Playwright):
    """POST リクエストでフォームデータを送信する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.post(
        "/post",
        form={"username": "user1", "password": "pass123"}
    )
    assert response.ok

    data = response.json()
    assert data["form"]["username"] == "user1"
    assert data["form"]["password"] == "pass123"
    api_context.dispose()


# ─────────────────────────────────────────────
# 3. PUT リクエスト
# ─────────────────────────────────────────────

def test_put_request(playwright: Playwright):
    """PUT リクエストでリソースを更新する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    payload = {"name": "更新太郎", "age": 31}
    response = api_context.put("/put", data=payload)
    assert response.ok
    assert response.status == 200

    data = response.json()
    assert data["json"]["name"] == "更新太郎"
    assert data["json"]["age"] == 31
    api_context.dispose()


# ─────────────────────────────────────────────
# 4. PATCH リクエスト
# ─────────────────────────────────────────────

def test_patch_request(playwright: Playwright):
    """PATCH リクエストでリソースを部分更新する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    payload = {"age": 32}
    response = api_context.patch("/patch", data=payload)
    assert response.ok
    assert response.status == 200

    data = response.json()
    assert data["json"]["age"] == 32
    api_context.dispose()


# ─────────────────────────────────────────────
# 5. DELETE リクエスト
# ─────────────────────────────────────────────

def test_delete_request(playwright: Playwright):
    """DELETE リクエストでリソースを削除する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.delete("/delete")
    assert response.ok
    assert response.status == 200

    data = response.json()
    assert data["url"] == "https://httpbin.org/delete"
    api_context.dispose()


# ─────────────────────────────────────────────
# 6. レスポンスステータスの検証
# ─────────────────────────────────────────────

def test_response_status_ok(playwright: Playwright):
    """response.ok でステータスが 2xx であることを確認する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get("/status/200")
    assert response.ok  # 2xx の場合 True
    assert response.status == 200
    api_context.dispose()


def test_response_status_codes(playwright: Playwright):
    """さまざまなHTTPステータスコードを検証する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    # 404 Not Found
    response_404 = api_context.get("/status/404")
    assert not response_404.ok
    assert response_404.status == 404

    # 500 Internal Server Error
    response_500 = api_context.get("/status/500")
    assert not response_500.ok
    assert response_500.status == 500
    api_context.dispose()


def test_response_status_text(playwright: Playwright):
    """response.status_text でステータステキストを取得する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get("/get")
    assert response.ok
    assert response.status_text == "OK"
    api_context.dispose()


# ─────────────────────────────────────────────
# 7. レスポンスボディの取得
# ─────────────────────────────────────────────

def test_response_json(playwright: Playwright):
    """response.json() で JSON レスポンスをパースする"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get("/get")
    data = response.json()
    assert isinstance(data, dict)
    assert "headers" in data
    assert "url" in data
    api_context.dispose()


def test_response_text(playwright: Playwright):
    """response.text() でレスポンスをテキストとして取得する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get("/html")
    text = response.text()
    assert "Herman Melville" in text
    api_context.dispose()


def test_response_body(playwright: Playwright):
    """response.body() で生のバイトデータを取得する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get("/get")
    body = response.body()
    assert isinstance(body, bytes)
    assert len(body) > 0
    api_context.dispose()


# ─────────────────────────────────────────────
# 8. カスタムヘッダー
# ─────────────────────────────────────────────

def test_custom_headers_on_context(playwright: Playwright):
    """extra_http_headers でコンテキスト全体にカスタムヘッダーを設定する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org",
        extra_http_headers={
            "X-Custom-Header": "custom-value",
            "Accept": "application/json",
        }
    )
    response = api_context.get("/headers")
    assert response.ok

    data = response.json()
    headers = data["headers"]
    assert headers["X-Custom-Header"] == "custom-value"
    assert headers["Accept"] == "application/json"
    api_context.dispose()


def test_custom_headers_per_request(playwright: Playwright):
    """リクエストごとにカスタムヘッダーを指定する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get(
        "/headers",
        headers={"X-Request-Id": "12345"}
    )
    assert response.ok

    data = response.json()
    assert data["headers"]["X-Request-Id"] == "12345"
    api_context.dispose()


def test_authorization_header(playwright: Playwright):
    """Bearer トークンを使った認証ヘッダーを設定する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org",
        extra_http_headers={
            "Authorization": "Bearer test-token-12345",
        }
    )
    response = api_context.get("/headers")
    assert response.ok

    data = response.json()
    assert data["headers"]["Authorization"] == "Bearer test-token-12345"
    api_context.dispose()


# ─────────────────────────────────────────────
# 9. APIRequestContext の作成
# ─────────────────────────────────────────────

def test_new_context_with_base_url(playwright: Playwright):
    """base_url を指定して APIRequestContext を作成する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    # base_url が設定されているので相対パスで指定可能
    response = api_context.get("/get")
    assert response.ok
    assert "httpbin.org" in response.json()["url"]
    api_context.dispose()


def test_new_context_with_timeout(playwright: Playwright):
    """タイムアウトを指定して APIRequestContext を作成する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org",
        timeout=30000  # 30秒
    )
    response = api_context.get("/get")
    assert response.ok
    api_context.dispose()


def test_multiple_contexts(playwright: Playwright):
    """複数の APIRequestContext を同時に使用する"""
    # コンテキスト1: httpbin.org
    context1 = playwright.request.new_context(
        base_url="https://httpbin.org",
        extra_http_headers={"X-Context": "context-1"}
    )
    # コンテキスト2: 別のヘッダー設定
    context2 = playwright.request.new_context(
        base_url="https://httpbin.org",
        extra_http_headers={"X-Context": "context-2"}
    )

    response1 = context1.get("/headers")
    response2 = context2.get("/headers")

    assert response1.json()["headers"]["X-Context"] == "context-1"
    assert response2.json()["headers"]["X-Context"] == "context-2"

    context1.dispose()
    context2.dispose()


def test_context_dispose(playwright: Playwright):
    """dispose() でコンテキストのリソースを解放する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get("/get")
    assert response.ok

    # リソースの解放
    api_context.dispose()


# ─────────────────────────────────────────────
# 10. API Response アサーション
# ─────────────────────────────────────────────

def test_expect_to_be_ok(playwright: Playwright):
    """expect(response).to_be_ok() でレスポンスが成功であることを検証する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get("/get")

    # Playwright の expect を使った API アサーション
    expect(response).to_be_ok()
    api_context.dispose()


def test_expect_to_be_ok_with_post(playwright: Playwright):
    """POST レスポンスに対して expect(response).to_be_ok() を使用する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.post("/post", data={"key": "value"})

    expect(response).to_be_ok()

    data = response.json()
    assert data["json"]["key"] == "value"
    api_context.dispose()


def test_expect_not_to_be_ok(playwright: Playwright):
    """expect(response).not_to_be_ok() でエラーレスポンスを検証する"""
    api_context = playwright.request.new_context(
        base_url="https://httpbin.org"
    )
    response = api_context.get("/status/404")

    # not_to_be_ok で 4xx/5xx レスポンスを検証
    expect(response).not_to_be_ok()
    assert response.status == 404
    api_context.dispose()
