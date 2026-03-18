"""
test_24_async_api.py - 非同期 API（async/await）のサンプル

Playwright は同期 API と非同期 API の両方を提供する。
非同期 API は async/await パターンを使い、
イベントループベースのアプリケーションとの統合に適している。
"""
import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.async_api import async_playwright, expect
from runner import TestRunner


# ---------------------------------------------------------------------------
# 1. 非同期でのブラウザ起動と操作
# ---------------------------------------------------------------------------
async def _async_launch_chromium():
    """非同期で Chromium ブラウザを起動する"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # ブラウザが正常に起動したことを確認
        assert browser.is_connected()
        await browser.close()


def test_async_launch_chromium():
    asyncio.run(_async_launch_chromium())


async def _async_launch_firefox():
    """非同期で Firefox ブラウザを起動する"""
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        assert browser.is_connected()
        await browser.close()


def test_async_launch_firefox():
    asyncio.run(_async_launch_firefox())


async def _async_launch_webkit():
    """非同期で WebKit ブラウザを起動する"""
    async with async_playwright() as p:
        browser = await p.webkit.launch(headless=True)
        assert browser.is_connected()
        await browser.close()


def test_async_launch_webkit():
    asyncio.run(_async_launch_webkit())


async def _async_new_page():
    """非同期でページを作成する"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        assert page is not None
        await browser.close()


def test_async_new_page():
    asyncio.run(_async_new_page())


async def _async_context_and_page():
    """非同期でコンテキストとページを作成する"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # コンテキストを明示的に作成してからページを生成
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="ja-JP",
        )
        page = await context.new_page()
        assert page is not None
        await context.close()
        await browser.close()


def test_async_context_and_page():
    asyncio.run(_async_context_and_page())


# ---------------------------------------------------------------------------
# 2. 非同期でのページ遷移
# ---------------------------------------------------------------------------
async def _async_navigation():
    """非同期でのブラウザ起動とページ遷移"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.microsoft.com/ja-jp")
        title = await page.title()
        assert "Microsoft" in title
        await browser.close()


def test_async_navigation():
    asyncio.run(_async_navigation())


async def _async_navigation_wait_until():
    """非同期でのページ遷移 - wait_until オプション"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # networkidle: ネットワーク接続が 500ms 間アイドルになるまで待機
        response = await page.goto(
            "https://www.microsoft.com/ja-jp",
            wait_until="networkidle",
        )
        assert response is not None
        assert response.ok
        await browser.close()


def test_async_navigation_wait_until():
    asyncio.run(_async_navigation_wait_until())


async def _async_go_back_and_forward():
    """非同期での戻る・進む操作"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.microsoft.com/ja-jp")
        first_url = page.url
        # 別のページに遷移
        await page.goto("https://www.microsoft.com/ja-jp/microsoft-365")
        second_url = page.url
        assert first_url != second_url

        # 戻る
        await page.go_back()
        assert page.url == first_url

        # 進む
        await page.go_forward()
        assert page.url == second_url
        await browser.close()


def test_async_go_back_and_forward():
    asyncio.run(_async_go_back_and_forward())


async def _async_reload():
    """非同期でのページリロード"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.microsoft.com/ja-jp")
        # ページをリロード
        response = await page.reload()
        assert response is not None
        assert response.ok
        await browser.close()


def test_async_reload():
    asyncio.run(_async_reload())


# ---------------------------------------------------------------------------
# 3. 非同期でのロケーター操作
# ---------------------------------------------------------------------------
async def _async_locator():
    """非同期でのロケーター操作"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content('<button id="btn">クリック</button>')
        await page.locator("#btn").click()
        await browser.close()


def test_async_locator():
    asyncio.run(_async_locator())


async def _async_locator_fill():
    """非同期でのテキスト入力"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(
            '<input type="text" id="name" placeholder="名前を入力" />'
        )
        # 非同期でテキストを入力
        await page.locator("#name").fill("テスト太郎")
        value = await page.locator("#name").input_value()
        assert value == "テスト太郎"
        await browser.close()


def test_async_locator_fill():
    asyncio.run(_async_locator_fill())


async def _async_locator_get_by_role():
    """非同期での get_by_role ロケーター"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(
            """
            <form>
                <label for="email">メールアドレス</label>
                <input type="email" id="email" />
                <button type="submit">送信</button>
            </form>
            """
        )
        # ARIA ロールで要素を検索し操作
        await page.get_by_role("textbox").fill("user@example.com")
        await page.get_by_role("button", name="送信").click()
        await browser.close()


def test_async_locator_get_by_role():
    asyncio.run(_async_locator_get_by_role())


async def _async_locator_get_by_text():
    """非同期での get_by_text ロケーター"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(
            """
            <ul>
                <li>りんご</li>
                <li>みかん</li>
                <li>ぶどう</li>
            </ul>
            """
        )
        # テキストで要素を検索
        item = page.get_by_text("みかん")
        text = await item.text_content()
        assert text == "みかん"
        await browser.close()


def test_async_locator_get_by_text():
    asyncio.run(_async_locator_get_by_text())


async def _async_locator_multiple_elements():
    """非同期での複数要素の操作"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(
            """
            <ul>
                <li class="item">項目1</li>
                <li class="item">項目2</li>
                <li class="item">項目3</li>
            </ul>
            """
        )
        items = page.locator(".item")
        count = await items.count()
        assert count == 3

        # 各要素のテキストを取得
        texts = await items.all_text_contents()
        assert texts == ["項目1", "項目2", "項目3"]
        await browser.close()


def test_async_locator_multiple_elements():
    asyncio.run(_async_locator_multiple_elements())


# ---------------------------------------------------------------------------
# 4. 非同期でのアサーション
# ---------------------------------------------------------------------------
async def _async_assertion_to_have_title():
    """非同期でのタイトルアサーション"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.microsoft.com/ja-jp")
        # expect による非同期アサーション（自動リトライ付き）
        await expect(page).to_have_title(r".*Microsoft.*")
        await browser.close()


def test_async_assertion_to_have_title():
    asyncio.run(_async_assertion_to_have_title())


async def _async_assertion_to_have_url():
    """非同期での URL アサーション"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.microsoft.com/ja-jp")
        await expect(page).to_have_url(r".*microsoft\.com.*")
        await browser.close()


def test_async_assertion_to_have_url():
    asyncio.run(_async_assertion_to_have_url())


async def _async_assertion_to_be_visible():
    """非同期での要素表示アサーション"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content('<div id="visible">表示中</div>')
        await expect(page.locator("#visible")).to_be_visible()
        await browser.close()


def test_async_assertion_to_be_visible():
    asyncio.run(_async_assertion_to_be_visible())


async def _async_assertion_to_have_text():
    """非同期でのテキストアサーション"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content('<span id="msg">こんにちは世界</span>')
        await expect(page.locator("#msg")).to_have_text("こんにちは世界")
        await browser.close()


def test_async_assertion_to_have_text():
    asyncio.run(_async_assertion_to_have_text())


async def _async_assertion_to_have_value():
    """非同期での入力値アサーション"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content('<input id="input" value="初期値" />')
        await expect(page.locator("#input")).to_have_value("初期値")
        await browser.close()


def test_async_assertion_to_have_value():
    asyncio.run(_async_assertion_to_have_value())


async def _async_assertion_to_have_attribute():
    """非同期での属性アサーション"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(
            '<a href="https://example.com" target="_blank">リンク</a>'
        )
        await expect(page.locator("a")).to_have_attribute("target", "_blank")
        await browser.close()


def test_async_assertion_to_have_attribute():
    asyncio.run(_async_assertion_to_have_attribute())


async def _async_assertion_not():
    """非同期での否定アサーション"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(
            '<div id="hidden" style="display: none;">非表示</div>'
        )
        # not_ で否定アサーション
        await expect(page.locator("#hidden")).not_to_be_visible()
        await browser.close()


def test_async_assertion_not():
    asyncio.run(_async_assertion_not())


# ---------------------------------------------------------------------------
# 5. 非同期でのネットワーク傍受
# ---------------------------------------------------------------------------
async def _async_route_intercept():
    """非同期でのリクエスト傍受（route）"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        intercepted_urls: list[str] = []

        # 画像リクエストを傍受してアボート
        async def handle_route(route):
            if route.request.resource_type == "image":
                intercepted_urls.append(route.request.url)
                await route.abort()
            else:
                await route.continue_()

        await page.route("**/*", handle_route)
        await page.goto("https://www.microsoft.com/ja-jp")

        # 画像リクエストが傍受されたことを確認
        assert len(intercepted_urls) > 0
        await browser.close()


def test_async_route_intercept():
    asyncio.run(_async_route_intercept())


async def _async_route_mock_response():
    """非同期でのレスポンスモック"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # API レスポンスをモックデータで差し替え
        mock_data = {"users": [{"name": "太郎"}, {"name": "花子"}]}

        async def handle_api(route):
            await route.fulfill(
                status=200,
                content_type="application/json",
                body='{"users": [{"name": "太郎"}, {"name": "花子"}]}',
            )

        await page.route("**/api/users", handle_api)

        # モックされたエンドポイントにアクセス
        response = await page.goto("https://example.com/api/users")
        assert response is not None
        json_body = await response.json()
        assert json_body == mock_data
        await browser.close()


def test_async_route_mock_response():
    asyncio.run(_async_route_mock_response())


async def _async_request_response_events():
    """非同期でのリクエスト・レスポンスイベント監視"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        request_urls: list[str] = []
        response_statuses: list[int] = []

        # リクエストイベントを監視
        page.on("request", lambda req: request_urls.append(req.url))
        page.on(
            "response", lambda res: response_statuses.append(res.status)
        )

        await page.goto("https://www.microsoft.com/ja-jp")

        # イベントが記録されたことを確認
        assert len(request_urls) > 0
        assert len(response_statuses) > 0
        # メインドキュメントのレスポンスに 200 が含まれる
        assert 200 in response_statuses
        await browser.close()


def test_async_request_response_events():
    asyncio.run(_async_request_response_events())


# ---------------------------------------------------------------------------
# 6. 非同期でのスクリーンショット
# ---------------------------------------------------------------------------
async def _async_screenshot_page():
    """非同期でのページ全体スクリーンショット"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.microsoft.com/ja-jp")

        # ページ全体のスクリーンショットをバイト列として取得
        screenshot = await page.screenshot()
        assert len(screenshot) > 0
        assert isinstance(screenshot, bytes)
        await browser.close()


def test_async_screenshot_page():
    asyncio.run(_async_screenshot_page())


async def _async_screenshot_full_page():
    """非同期でのフルページスクリーンショット"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.microsoft.com/ja-jp")

        # full_page=True でスクロール領域を含む全体をキャプチャ
        screenshot = await page.screenshot(full_page=True)
        assert len(screenshot) > 0
        await browser.close()


def test_async_screenshot_full_page():
    asyncio.run(_async_screenshot_full_page())


async def _async_screenshot_element():
    """非同期での要素スクリーンショット"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(
            '<div id="target" style="width:200px;height:100px;background:blue;">'
            "対象要素</div>"
        )

        # 特定要素のみをスクリーンショット
        element = page.locator("#target")
        screenshot = await element.screenshot()
        assert len(screenshot) > 0
        await browser.close()


def test_async_screenshot_element():
    asyncio.run(_async_screenshot_element())


async def _async_screenshot_to_file():
    """非同期でのスクリーンショット保存"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content("<h1>スクリーンショットテスト</h1>")

        # ファイルに保存
        with tempfile.TemporaryDirectory() as tmp_dir:
            filepath = Path(tmp_dir) / "async_screenshot.png"
            await page.screenshot(path=str(filepath))
            assert filepath.exists()
            assert filepath.stat().st_size > 0
        await browser.close()


def test_async_screenshot_to_file():
    asyncio.run(_async_screenshot_to_file())


# ---------------------------------------------------------------------------
# 7. 非同期でのJavaScript評価
# ---------------------------------------------------------------------------
async def _async_evaluate_expression():
    """非同期での JavaScript 式の評価"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 単純な式を評価
        result = await page.evaluate("1 + 2")
        assert result == 3
        await browser.close()


def test_async_evaluate_expression():
    asyncio.run(_async_evaluate_expression())


async def _async_evaluate_function():
    """非同期での JavaScript 関数の評価"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # 関数を評価して結果を取得
        result = await page.evaluate(
            """() => {
                return { width: window.innerWidth, height: window.innerHeight };
            }"""
        )
        assert "width" in result
        assert "height" in result
        await browser.close()


def test_async_evaluate_function():
    asyncio.run(_async_evaluate_function())


async def _async_evaluate_with_args():
    """非同期での引数付き JavaScript 評価"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Python の値を JavaScript に渡して評価
        result = await page.evaluate("(x) => x * 2", 21)
        assert result == 42
        await browser.close()


def test_async_evaluate_with_args():
    asyncio.run(_async_evaluate_with_args())


async def _async_evaluate_dom():
    """非同期での DOM 操作を伴う JavaScript 評価"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(
            """
            <ul id="list">
                <li>アイテム1</li>
                <li>アイテム2</li>
                <li>アイテム3</li>
            </ul>
            """
        )

        # DOM から情報を抽出
        count = await page.evaluate(
            'document.querySelectorAll("#list li").length'
        )
        assert count == 3

        # テキスト内容を配列で取得
        texts = await page.evaluate(
            """() => {
                const items = document.querySelectorAll('#list li');
                return Array.from(items).map(el => el.textContent);
            }"""
        )
        assert texts == ["アイテム1", "アイテム2", "アイテム3"]
        await browser.close()


def test_async_evaluate_dom():
    asyncio.run(_async_evaluate_dom())


async def _async_evaluate_handle():
    """非同期での evaluate_handle による要素ハンドル取得"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content("<h1>見出し</h1>")

        # evaluate_handle で JSHandle を取得
        handle = await page.evaluate_handle("document.querySelector('h1')")
        # JSHandle のプロパティを取得
        tag_name = await handle.evaluate("el => el.tagName")
        assert tag_name == "H1"

        text = await handle.evaluate("el => el.textContent")
        assert text == "見出し"

        await handle.dispose()
        await browser.close()


def test_async_evaluate_handle():
    asyncio.run(_async_evaluate_handle())


# ---------------------------------------------------------------------------
# メイン実行
# ---------------------------------------------------------------------------
def main():
    runner = TestRunner("test_24_async_api")
    tests = [
        test_async_launch_chromium,
        test_async_launch_firefox,
        test_async_launch_webkit,
        test_async_new_page,
        test_async_context_and_page,
        test_async_navigation,
        test_async_navigation_wait_until,
        test_async_go_back_and_forward,
        test_async_reload,
        test_async_locator,
        test_async_locator_fill,
        test_async_locator_get_by_role,
        test_async_locator_get_by_text,
        test_async_locator_multiple_elements,
        test_async_assertion_to_have_title,
        test_async_assertion_to_have_url,
        test_async_assertion_to_be_visible,
        test_async_assertion_to_have_text,
        test_async_assertion_to_have_value,
        test_async_assertion_to_have_attribute,
        test_async_assertion_not,
        test_async_route_intercept,
        test_async_route_mock_response,
        test_async_request_response_events,
        test_async_screenshot_page,
        test_async_screenshot_full_page,
        test_async_screenshot_element,
        test_async_screenshot_to_file,
        test_async_evaluate_expression,
        test_async_evaluate_function,
        test_async_evaluate_with_args,
        test_async_evaluate_dom,
        test_async_evaluate_handle,
    ]
    for t in tests:
        runner.run(t)
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
