"""
test_07_network.py - ネットワーク制御のサンプル

リクエストの傍受・モック・修正・ブロック、レスポンス待機、
HAR 記録など、ネットワークレベルの操作を示す。
"""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

from runner import TestRunner

# set_content + fetch が動作するよう HTTP オリジンを確保するためのモック URL
_MOCK_ORIGIN = "https://mock.test/"


def _setup_mock_origin(target):
    """page または context にモック HTTP オリジンを登録する"""
    target.route(
        _MOCK_ORIGIN,
        lambda r: r.fulfill(
            status=200,
            content_type="text/html",
            body="<html><body></body></html>",
        ),
    )



# ---------------------------------------------------------------------------
# 1. リクエスト傍受とレスポンスモック (page.route + route.fulfill)
# ---------------------------------------------------------------------------
def test_route_fulfill(page):
    """リクエスト傍受とレスポンスモック"""

    def handle_route(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"message": "モックレスポンス"}),
        )

    # fetch の相対 URL が解決されるよう HTTP オリジンを確保
    _setup_mock_origin(page)
    page.goto(_MOCK_ORIGIN)

    page.route("**/api/data", handle_route)
    page.set_content(
        '<script>fetch("/api/data").then(r=>r.json()).then(d=>document.title=d.message)</script>'
    )
    page.wait_for_function("document.title === 'モックレスポンス'")


# ---------------------------------------------------------------------------
# 2. リクエスト修正 - ヘッダー追加 (route.continue_)
# ---------------------------------------------------------------------------
def test_route_continue_with_headers(page):
    """リクエストにカスタムヘッダーを追加して実サーバーへ転送する"""
    added_headers: dict = {}

    def add_custom_header(route):
        headers = {**route.request.headers, "x-custom-header": "playwright-test"}
        added_headers.update(headers)
        route.continue_(headers=headers)

    # 実サイトへのリクエストにカスタムヘッダーを追加
    page.route("https://www.microsoft.com/ja-jp", add_custom_header)
    response = page.goto(
        "https://www.microsoft.com/ja-jp", wait_until="domcontentloaded"
    )

    # ハンドラーでヘッダーが設定されたことを確認
    assert added_headers.get("x-custom-header") == "playwright-test"
    # サーバーが正常にレスポンスを返したことを確認
    assert response.ok


# ---------------------------------------------------------------------------
# 3. リクエストブロック (route.abort) - 画像リソースのブロック
# ---------------------------------------------------------------------------
def test_route_abort_images(page):
    """画像リソースへのリクエストをブロックする"""
    aborted_urls: list[str] = []

    def block_images(route):
        aborted_urls.append(route.request.url)
        route.abort()

    # 画像リクエストをすべてブロック
    page.route("**/*.{png,jpg,jpeg,gif,svg,webp,ico}", block_images)
    page.goto("https://www.microsoft.com/ja-jp", wait_until="domcontentloaded")

    # 少なくとも 1 件の画像リクエストがブロックされていることを確認
    assert len(aborted_urls) > 0, "画像リクエストが 1 件もブロックされなかった"


# ---------------------------------------------------------------------------
# 4. レスポンス待機 (page.expect_response)
# ---------------------------------------------------------------------------
def test_expect_response(page):
    """特定のレスポンスを待機する"""
    page.route(
        "**/api/status",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"status": "ok"}),
        ),
    )

    _setup_mock_origin(page)
    page.goto(_MOCK_ORIGIN)

    with page.expect_response("**/api/status") as response_info:
        page.set_content('<script>fetch("/api/status")</script>')

    response = response_info.value
    assert response.status == 200
    assert response.url.endswith("/api/status")


# ---------------------------------------------------------------------------
# 5. リクエスト待機 (page.expect_request)
# ---------------------------------------------------------------------------
def test_expect_request(page):
    """特定のリクエストが発行されるのを待機する"""
    page.route(
        "**/api/submit",
        lambda route: route.fulfill(
            status=201,
            content_type="application/json",
            body=json.dumps({"id": 1}),
        ),
    )

    _setup_mock_origin(page)
    page.goto(_MOCK_ORIGIN)

    with page.expect_request("**/api/submit") as request_info:
        page.set_content(
            """<script>
            fetch("/api/submit", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({name: "テスト"})
            })
            </script>"""
        )

    request = request_info.value
    assert request.method == "POST"
    assert json.loads(request.post_data)["name"] == "テスト"


# ---------------------------------------------------------------------------
# 6. ネットワークイベント監視 (page.on("request"), page.on("response"))
# ---------------------------------------------------------------------------
def test_network_events(page):
    """リクエスト・レスポンスイベントを監視する"""
    request_urls: list[str] = []
    response_statuses: list[int] = []

    page.on("request", lambda req: request_urls.append(req.url))
    page.on("response", lambda res: response_statuses.append(res.status))

    page.goto("https://www.microsoft.com/ja-jp", wait_until="domcontentloaded")

    # ナビゲーションにより複数のリクエストが発生する
    assert len(request_urls) > 0, "リクエストイベントが発火しなかった"
    assert len(response_statuses) > 0, "レスポンスイベントが発火しなかった"

    # メインドキュメントのステータスコードを確認
    assert (
        200 in response_statuses
        or 301 in response_statuses
        or 302 in response_statuses
    )


# ---------------------------------------------------------------------------
# 7. HAR 記録 (record_har_path)
# ---------------------------------------------------------------------------
def test_har_recording(browser):
    """HAR ファイルにネットワークトラフィックを記録する"""
    har_dir = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "output", "traces")
    )
    os.makedirs(har_dir, exist_ok=True)

    # テスト間の衝突を避けるため一意なファイル名を生成
    fd, har_path = tempfile.mkstemp(suffix=".har", dir=har_dir)
    os.close(fd)

    # HAR 記録を有効にしたコンテキストを作成
    context = browser.new_context(record_har_path=har_path)
    har_page = context.new_page()

    har_page.goto("https://www.microsoft.com/ja-jp", wait_until="domcontentloaded")

    # コンテキストを閉じると HAR ファイルが書き出される
    context.close()

    assert os.path.exists(har_path), "HAR ファイルが生成されなかった"
    assert os.path.getsize(har_path) > 0, "HAR ファイルが空"

    # HAR の構造を検証
    with open(har_path, encoding="utf-8") as f:
        har_data = json.load(f)

    assert "log" in har_data
    assert len(har_data["log"]["entries"]) > 0, "HAR エントリが記録されていない"


# ---------------------------------------------------------------------------
# 8. ルートのアンインストール (page.unroute)
# ---------------------------------------------------------------------------
def test_unroute(page):
    """登録したルートを解除する"""
    call_count = 0

    def counting_handler(route):
        nonlocal call_count
        call_count += 1
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"count": call_count}),
        )

    _setup_mock_origin(page)
    page.goto(_MOCK_ORIGIN)

    page.route("**/api/count", counting_handler)

    # 1 回目: ルートが有効
    page.set_content(
        '<script>fetch("/api/count").then(r=>r.json()).then(d=>document.title=String(d.count))</script>'
    )
    page.wait_for_function("document.title === '1'")
    assert call_count == 1

    # ルートを解除
    page.unroute("**/api/count", counting_handler)

    # 解除後に別のルートでフォールバックを確認
    page.route(
        "**/api/count",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"count": "unrouted"}),
        ),
    )

    page.set_content(
        '<script>fetch("/api/count").then(r=>r.json()).then(d=>document.title=d.count)</script>'
    )
    page.wait_for_function("document.title === 'unrouted'")

    # 元のハンドラーは呼ばれていない (カウントは 1 のまま)
    assert call_count == 1


# ---------------------------------------------------------------------------
# 9. コンテキストレベルのルーティング (context.route)
# ---------------------------------------------------------------------------
def test_context_route(context):
    """コンテキストレベルでルートを設定し、複数ページに適用する"""

    def mock_api(route):
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"source": "context-mock"}),
        )

    # コンテキストレベルでルートを登録 (全ページに適用)
    _setup_mock_origin(context)
    context.route("**/api/shared", mock_api)

    # 同一コンテキストの複数ページで同じルートが有効
    page1 = context.new_page()
    page2 = context.new_page()

    for idx, p in enumerate([page1, page2]):
        p.goto(_MOCK_ORIGIN)
        p.set_content(
            '<script>fetch("/api/shared").then(r=>r.json()).then(d=>document.title=d.source)</script>'
        )
        p.wait_for_function("document.title === 'context-mock'")
        assert p.title() == "context-mock", f"ページ {idx + 1} でモックが適用されなかった"

    page1.close()
    page2.close()


# ---------------------------------------------------------------------------
# 10. レスポンスボディの取得 (response.body, response.json, response.text)
# ---------------------------------------------------------------------------
def test_response_body(page):
    """レスポンスボディをさまざまな形式で取得する"""
    mock_data = {"items": [1, 2, 3], "total": 3}

    page.route(
        "**/api/items",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(mock_data),
        ),
    )

    _setup_mock_origin(page)
    page.goto(_MOCK_ORIGIN)

    with page.expect_response("**/api/items") as response_info:
        page.set_content('<script>fetch("/api/items")</script>')

    response = response_info.value

    # バイナリとして取得
    body_bytes = response.body()
    assert isinstance(body_bytes, bytes)

    # テキストとして取得
    body_text = response.text()
    assert "items" in body_text

    # JSON として取得
    body_json = response.json()
    assert body_json["total"] == 3
    assert body_json["items"] == [1, 2, 3]


def main():
    runner = TestRunner("test_07_network")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # --- page テスト ---
        page_tests = [
            test_route_fulfill,
            test_route_continue_with_headers,
            test_route_abort_images,
            test_expect_response,
            test_expect_request,
            test_network_events,
            test_unroute,
            test_response_body,
        ]
        for test_func in page_tests:
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                locale="ja-JP",
                timezone_id="Asia/Tokyo",
            )
            page = context.new_page()
            runner.run(test_func, page)
            context.close()

        # --- browser テスト ---
        runner.run(test_har_recording, browser)

        # --- context テスト ---
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="ja-JP",
            timezone_id="Asia/Tokyo",
        )
        runner.run(test_context_route, context)
        context.close()

        browser.close()
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
