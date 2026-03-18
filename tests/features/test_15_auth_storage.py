"""
test_15_auth_storage.py - 認証・ストレージ状態のサンプル

ストレージ状態（Cookie, localStorage）の保存・復元により、
ログイン状態を複数テスト間で共有する方法を示す。
"""

import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

from runner import TestRunner

SKIP_TESTS = {}


# ---------------------------------------------------------------------------
# 1. Cookie によるセッション設定 (add_cookies)
# ---------------------------------------------------------------------------


def test_add_cookies():
    """Cookie を手動で追加してセッション情報を設定する"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        # add_cookies で任意の Cookie をコンテキストに追加
        context.add_cookies([
            {
                "name": "session_id",
                "value": "user-session-xyz789",
                "domain": "example.com",
                "path": "/",
            },
            {
                "name": "lang",
                "value": "ja",
                "domain": "example.com",
                "path": "/",
            },
        ])

        # 追加した Cookie が取得できることを確認
        cookies = context.cookies()
        names = [c["name"] for c in cookies]
        assert "session_id" in names
        assert "lang" in names

        context.close()
        browser.close()


def test_add_cookies_with_options():
    """有効期限やセキュリティ属性を指定して Cookie を追加する"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        # expires, httpOnly, secure, sameSite など詳細な属性を指定可能
        context.add_cookies([
            {
                "name": "auth_token",
                "value": "secure-token-abc",
                "domain": "example.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "Strict",
            },
        ])

        cookies = context.cookies()
        auth_cookie = next(c for c in cookies if c["name"] == "auth_token")
        assert auth_cookie["value"] == "secure-token-abc"
        assert auth_cookie["httpOnly"] is True
        assert auth_cookie["secure"] is True
        assert auth_cookie["sameSite"] == "Strict"

        context.close()
        browser.close()


# ---------------------------------------------------------------------------
# 2. ストレージ状態の保存 (context.storage_state(path=...))
# 3. ストレージ状態の復元 (new_context(storage_state=...))
# ---------------------------------------------------------------------------


def test_save_and_restore_storage_state():
    """ストレージ状態の保存と復元"""
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # コンテキスト1: Cookie を設定して保存
        context1 = browser.new_context()
        context1.add_cookies([
            {
                "name": "session",
                "value": "abc123",
                "domain": "example.com",
                "path": "/",
            }
        ])

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            state_path = f.name

        context1.storage_state(path=state_path)
        context1.close()

        # コンテキスト2: 保存した状態を復元
        context2 = browser.new_context(storage_state=state_path)
        cookies = context2.cookies()
        assert any(
            c["name"] == "session" and c["value"] == "abc123" for c in cookies
        )
        context2.close()

        browser.close()
        os.unlink(state_path)


def test_storage_state_file_contains_cookies_and_origins():
    """保存したストレージ状態ファイルの構造を確認する"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        context.add_cookies([
            {
                "name": "user",
                "value": "taro",
                "domain": "example.com",
                "path": "/",
            }
        ])

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            state_path = f.name

        context.storage_state(path=state_path)

        # JSON ファイルには cookies と origins が含まれる
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        assert "cookies" in state
        assert "origins" in state
        assert any(c["name"] == "user" for c in state["cookies"])

        context.close()
        browser.close()
        os.unlink(state_path)


def test_restore_storage_state_from_dict():
    """辞書オブジェクトからストレージ状態を復元する"""
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # 辞書で状態を定義し、一時ファイル経由で復元する
        state_dict = {
            "cookies": [
                {
                    "name": "token",
                    "value": "dict-token-123",
                    "domain": "example.com",
                    "path": "/",
                    "expires": -1,
                    "httpOnly": False,
                    "secure": False,
                    "sameSite": "Lax",
                }
            ],
            "origins": [],
        }

        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        ) as f:
            json.dump(state_dict, f)
            state_path = f.name

        context = browser.new_context(storage_state=state_path)
        cookies = context.cookies()
        assert any(
            c["name"] == "token" and c["value"] == "dict-token-123"
            for c in cookies
        )

        context.close()
        browser.close()
        os.unlink(state_path)


# ---------------------------------------------------------------------------
# 4. localStorage の操作 (add_init_script)
# ---------------------------------------------------------------------------


def test_set_local_storage_via_init_script():
    """add_init_script で localStorage に値を設定する"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        # add_init_script はページが読み込まれる前に毎回実行される
        context.add_init_script("""
            window.localStorage.setItem('theme', 'dark');
            window.localStorage.setItem('language', 'ja');
        """)

        page = context.new_page()
        page.goto("https://example.com")

        # localStorage に設定した値が取得できることを確認
        theme = page.evaluate("() => window.localStorage.getItem('theme')")
        language = page.evaluate("() => window.localStorage.getItem('language')")
        assert theme == "dark"
        assert language == "ja"

        context.close()
        browser.close()


def test_set_local_storage_via_evaluate():
    """page.evaluate で localStorage を直接操作する"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://example.com")

        # evaluate を使ってページコンテキスト内で localStorage を操作
        page.evaluate("""
            window.localStorage.setItem('user_id', '12345');
            window.localStorage.setItem('preferences', JSON.stringify({notifications: true}));
        """)

        user_id = page.evaluate("() => window.localStorage.getItem('user_id')")
        assert user_id == "12345"

        prefs = page.evaluate(
            "() => JSON.parse(window.localStorage.getItem('preferences'))"
        )
        assert prefs["notifications"] is True

        context.close()
        browser.close()


# ---------------------------------------------------------------------------
# 5. Cookie 取得と確認 (context.cookies)
# ---------------------------------------------------------------------------


def test_get_cookies_all():
    """コンテキスト内の全 Cookie を取得する"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        context.add_cookies([
            {
                "name": "cookie_a",
                "value": "value_a",
                "domain": "example.com",
                "path": "/",
            },
            {
                "name": "cookie_b",
                "value": "value_b",
                "domain": "test.example.com",
                "path": "/",
            },
        ])

        # 引数なしで全 Cookie を取得
        all_cookies = context.cookies()
        assert len(all_cookies) == 2

        context.close()
        browser.close()


def test_get_cookies_by_url():
    """URL を指定して該当する Cookie のみ取得する"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        context.add_cookies([
            {
                "name": "site_a",
                "value": "a",
                "domain": "example.com",
                "path": "/",
            },
            {
                "name": "site_b",
                "value": "b",
                "domain": "other.com",
                "path": "/",
            },
        ])

        # URL を指定すると、そのドメインに一致する Cookie のみ返る
        example_cookies = context.cookies("https://example.com")
        assert all(c["domain"] == "example.com" for c in example_cookies)
        assert any(c["name"] == "site_a" for c in example_cookies)

        context.close()
        browser.close()


# ---------------------------------------------------------------------------
# 6. Cookie のクリア (context.clear_cookies)
# ---------------------------------------------------------------------------


def test_clear_all_cookies():
    """全ての Cookie をクリアする"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        context.add_cookies([
            {
                "name": "to_clear",
                "value": "123",
                "domain": "example.com",
                "path": "/",
            },
        ])
        assert len(context.cookies()) == 1

        # clear_cookies で全 Cookie を削除
        context.clear_cookies()
        assert len(context.cookies()) == 0

        context.close()
        browser.close()


def test_clear_cookies_by_name():
    """名前を指定して特定の Cookie のみクリアする"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        context.add_cookies([
            {
                "name": "keep_me",
                "value": "stay",
                "domain": "example.com",
                "path": "/",
            },
            {
                "name": "remove_me",
                "value": "gone",
                "domain": "example.com",
                "path": "/",
            },
        ])
        assert len(context.cookies()) == 2

        # name を指定して特定の Cookie のみ削除
        context.clear_cookies(name="remove_me")
        remaining = context.cookies()
        assert len(remaining) == 1
        assert remaining[0]["name"] == "keep_me"

        context.close()
        browser.close()


def test_clear_cookies_by_domain():
    """ドメインを指定して Cookie をクリアする"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        context.add_cookies([
            {
                "name": "cookie1",
                "value": "v1",
                "domain": "example.com",
                "path": "/",
            },
            {
                "name": "cookie2",
                "value": "v2",
                "domain": "other.com",
                "path": "/",
            },
        ])

        # domain を指定してそのドメインの Cookie のみ削除
        context.clear_cookies(domain="example.com")
        remaining = context.cookies()
        assert len(remaining) == 1
        assert remaining[0]["domain"] == "other.com"

        context.close()
        browser.close()


def main():
    runner = TestRunner("test_15_auth_storage")
    all_tests = [
        test_add_cookies,
        test_add_cookies_with_options,
        test_save_and_restore_storage_state,
        test_storage_state_file_contains_cookies_and_origins,
        test_restore_storage_state_from_dict,
        test_set_local_storage_via_init_script,
        test_set_local_storage_via_evaluate,
        test_get_cookies_all,
        test_get_cookies_by_url,
        test_clear_all_cookies,
        test_clear_cookies_by_name,
        test_clear_cookies_by_domain,
    ]
    for t in all_tests:
        runner.run(t, skip_reason=SKIP_TESTS.get(t.__name__))
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
