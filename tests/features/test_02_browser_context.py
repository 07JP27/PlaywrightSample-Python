"""
test_02_browser_context.py - ブラウザコンテキストのサンプル

BrowserContext はブラウザ内の独立したセッションを表す。
コンテキスト間は完全に分離され、Cookie やストレージを共有しない。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

from runner import TestRunner

SKIP_TESTS = {
    "test_http_credentials": "Basic 認証が必要なテストサーバーが無いためスキップ",
    "test_proxy_context": "プロキシサーバーが利用できない環境ではスキップ",
}

TARGET_URL = "https://www.microsoft.com/ja-jp"


# ---------------------------------------------------------------------------
# 1. 基本コンテキスト作成
# ---------------------------------------------------------------------------
class TestBasicContext:
    """browser.new_context() による基本的なコンテキスト作成"""

    def test_create_context(self):
        """コンテキストを作成し、ページを開けることを確認"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # 新しいコンテキストを作成
            context = browser.new_context()
            assert context is not None

            # コンテキストからページを作成
            page = context.new_page()
            page.goto(TARGET_URL)
            assert page.title() != ""

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 2. 複数コンテキストの作成（マルチユーザーシミュレーション）
# ---------------------------------------------------------------------------
class TestMultipleContexts:
    """複数コンテキストを同時に使い、独立したセッションを再現"""

    def test_multiple_contexts(self):
        """2 つのコンテキストが独立して動作することを確認"""
        with sync_playwright() as p:
            browser = p.chromium.launch()

            # ユーザー A 用コンテキスト
            context_a = browser.new_context()
            page_a = context_a.new_page()
            page_a.goto(TARGET_URL)

            # ユーザー B 用コンテキスト
            context_b = browser.new_context()
            page_b = context_b.new_page()
            page_b.goto(TARGET_URL)

            # 両方のページが独立して存在していることを確認
            assert len(context_a.pages) == 1
            assert len(context_b.pages) == 1
            assert page_a != page_b

            context_a.close()
            context_b.close()
            browser.close()


# ---------------------------------------------------------------------------
# 3. Cookie の追加・取得・削除
# ---------------------------------------------------------------------------
class TestCookieManagement:
    """add_cookies / cookies / clear_cookies による Cookie 操作"""

    def test_add_and_get_cookies(self):
        """Cookie を追加し、取得できることを確認"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto(TARGET_URL)

            # Cookie を追加
            context.add_cookies([
                {
                    "name": "test_cookie",
                    "value": "hello_playwright",
                    "domain": ".microsoft.com",
                    "path": "/",
                },
            ])

            # Cookie を取得して検証
            cookies = context.cookies()
            test_cookie = next(
                (c for c in cookies if c["name"] == "test_cookie"), None
            )
            assert test_cookie is not None
            assert test_cookie["value"] == "hello_playwright"

            context.close()
            browser.close()

    def test_clear_cookies(self):
        """clear_cookies で Cookie を削除できることを確認"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto(TARGET_URL)

            # Cookie を追加してからクリア
            context.add_cookies([
                {
                    "name": "temp_cookie",
                    "value": "temporary",
                    "domain": ".microsoft.com",
                    "path": "/",
                },
            ])
            context.clear_cookies()

            # クリア後は Cookie が空になっていることを確認
            cookies = context.cookies()
            temp_cookie = next(
                (c for c in cookies if c["name"] == "temp_cookie"), None
            )
            assert temp_cookie is None

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 4. ビューポート設定付きコンテキスト
# ---------------------------------------------------------------------------
class TestViewport:
    """viewport オプションでブラウザの表示領域を指定"""

    def test_custom_viewport(self):
        """カスタムビューポートサイズを設定できることを確認"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # モバイルサイズのビューポートを指定
            context = browser.new_context(
                viewport={"width": 375, "height": 812}
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            # ビューポートサイズを JavaScript で確認
            width = page.evaluate("window.innerWidth")
            height = page.evaluate("window.innerHeight")
            assert width == 375
            assert height == 812

            context.close()
            browser.close()

    def test_desktop_viewport(self):
        """デスクトップサイズのビューポートを確認"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            width = page.evaluate("window.innerWidth")
            assert width == 1920

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 5. HTTP Basic 認証情報付きコンテキスト
# ---------------------------------------------------------------------------
class TestHttpCredentials:
    """http_credentials でBasic 認証を事前設定"""

    def test_http_credentials(self):
        """http_credentials を設定したコンテキストを作成"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # Basic 認証情報をコンテキストに設定
            context = browser.new_context(
                http_credentials={
                    "username": "user",
                    "password": "pass",
                }
            )
            page = context.new_page()
            # 認証付きサイトへアクセス（ダイアログなしで認証される）
            page.goto("https://httpbin.org/basic-auth/user/pass")

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 6. Proxy 設定付きコンテキスト
# ---------------------------------------------------------------------------
class TestProxy:
    """proxy オプションでプロキシを設定"""

    def test_proxy_context(self):
        """プロキシ設定を指定してコンテキストを作成"""
        with sync_playwright() as p:
            # プロキシはブラウザ起動時に設定する
            browser = p.chromium.launch(
                proxy={
                    "server": "http://proxy.example.com:8080",
                    "username": "proxy_user",
                    "password": "proxy_pass",
                }
            )
            context = browser.new_context()
            page = context.new_page()
            page.goto(TARGET_URL)

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 7. パーミッション制御
# ---------------------------------------------------------------------------
class TestPermissions:
    """grant_permissions / clear_permissions によるブラウザ権限制御"""

    def test_grant_permissions(self):
        """geolocation パーミッションを許可"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()

            # geolocation パーミッションを付与
            context.grant_permissions(["geolocation"])

            page = context.new_page()
            page.goto(TARGET_URL)

            # パーミッションが付与されていることを Permissions API で確認
            state = page.evaluate(
                """async () => {
                    const result = await navigator.permissions.query(
                        { name: 'geolocation' }
                    );
                    return result.state;
                }"""
            )
            assert state == "granted"

            context.close()
            browser.close()

    def test_clear_permissions(self):
        """付与したパーミッションをクリア"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()

            # パーミッションを付与してからクリア
            context.grant_permissions(["geolocation"])
            context.clear_permissions()

            page = context.new_page()
            page.goto(TARGET_URL)

            # クリア後はデフォルト状態（prompt）に戻ることを確認
            state = page.evaluate(
                """async () => {
                    const result = await navigator.permissions.query(
                        { name: 'geolocation' }
                    );
                    return result.state;
                }"""
            )
            assert state == "prompt"

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 8. ユーザーエージェント設定
# ---------------------------------------------------------------------------
class TestUserAgent:
    """user_agent オプションでカスタム UA を設定"""

    def test_custom_user_agent(self):
        """カスタムユーザーエージェントが反映されることを確認"""
        custom_ua = "PlaywrightSample/1.0 (TestBot)"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(user_agent=custom_ua)
            page = context.new_page()
            page.goto(TARGET_URL)

            # navigator.userAgent で確認
            actual_ua = page.evaluate("navigator.userAgent")
            assert actual_ua == custom_ua

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 9. コンテキスト間の分離確認
# ---------------------------------------------------------------------------
class TestContextIsolation:
    """コンテキスト間で Cookie が共有されないことを検証"""

    def test_cookies_not_shared_between_contexts(self):
        """一方のコンテキストに追加した Cookie が他方に見えないこと"""
        with sync_playwright() as p:
            browser = p.chromium.launch()

            # コンテキスト A に Cookie を設定
            context_a = browser.new_context()
            page_a = context_a.new_page()
            page_a.goto(TARGET_URL)
            context_a.add_cookies([
                {
                    "name": "isolation_test",
                    "value": "context_a_only",
                    "domain": ".microsoft.com",
                    "path": "/",
                },
            ])

            # コンテキスト B からは見えないことを確認
            context_b = browser.new_context()
            page_b = context_b.new_page()
            page_b.goto(TARGET_URL)
            cookies_b = context_b.cookies()
            isolation_cookie = next(
                (c for c in cookies_b if c["name"] == "isolation_test"), None
            )
            assert isolation_cookie is None, "Cookie がコンテキスト間で漏洩している"

            # コンテキスト A には存在することを再確認
            cookies_a = context_a.cookies()
            isolation_cookie_a = next(
                (c for c in cookies_a if c["name"] == "isolation_test"), None
            )
            assert isolation_cookie_a is not None
            assert isolation_cookie_a["value"] == "context_a_only"

            context_a.close()
            context_b.close()
            browser.close()


# ---------------------------------------------------------------------------
# 10. コンテキストのクローズ
# ---------------------------------------------------------------------------
class TestContextClose:
    """コンテキストの適切なクローズを確認"""

    def test_close_context(self):
        """コンテキストをクローズするとページも閉じられること"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto(TARGET_URL)

            # クローズ前のコンテキスト数を記録
            contexts_before = len(browser.contexts)

            # コンテキストをクローズ
            context.close()

            # クローズ後はコンテキストが減っていることを確認
            contexts_after = len(browser.contexts)
            assert contexts_after == contexts_before - 1

            browser.close()

    def test_close_does_not_affect_other_contexts(self):
        """一方のコンテキストを閉じても他方に影響しないこと"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context_1 = browser.new_context()
            context_2 = browser.new_context()

            page_1 = context_1.new_page()
            page_1.goto(TARGET_URL)
            page_2 = context_2.new_page()
            page_2.goto(TARGET_URL)

            # コンテキスト 1 をクローズ
            context_1.close()

            # コンテキスト 2 は引き続き利用可能
            assert len(context_2.pages) == 1
            title = page_2.title()
            assert title != ""

            context_2.close()
            browser.close()


def main():
    runner = TestRunner("test_02_browser_context")
    test_classes = [
        TestBasicContext,
        TestMultipleContexts,
        TestCookieManagement,
        TestViewport,
        TestHttpCredentials,
        TestProxy,
        TestPermissions,
        TestUserAgent,
        TestContextIsolation,
        TestContextClose,
    ]
    for cls in test_classes:
        obj = cls()
        for method_name in [m for m in dir(obj) if m.startswith("test_")]:
            method = getattr(obj, method_name)
            runner.run(method, skip_reason=SKIP_TESTS.get(method_name))
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
