"""
test_01_browser_launch.py - ブラウザ起動・管理のサンプル

Playwright がサポートする3つのブラウザエンジン（Chromium, Firefox, WebKit）の
起動方法と各種オプションを示す。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

from runner import TestRunner

SKIP_TESTS = {
    "test_launch_headful": "ヘッドフルモードはCI環境では実行不可",
    "test_launch_with_channel_chrome": "channel はインストール済みブラウザが必要",
    "test_launch_with_channel_msedge": "channel はインストール済みブラウザが必要",
}


def test_launch_chromium():
    """Chromium ブラウザを起動してページを開く"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()
        browser.close()


def test_launch_firefox():
    """Firefox ブラウザを起動してページを開く"""
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()
        browser.close()


def test_launch_webkit():
    """WebKit ブラウザを起動してページを開く"""
    with sync_playwright() as p:
        browser = p.webkit.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()
        browser.close()


def test_launch_headless():
    """ヘッドレスモード（GUI なし）でブラウザを起動する"""
    with sync_playwright() as p:
        # headless=True はデフォルト値。明示的に指定して起動する
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()
        browser.close()


def test_launch_headful():
    """ヘッドフルモード（GUI あり）でブラウザを起動する"""
    with sync_playwright() as p:
        # headless=False でブラウザウィンドウを表示して起動
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()
        browser.close()


def test_launch_with_slow_mo():
    """slow_mo オプションで操作間に遅延を挿入する"""
    with sync_playwright() as p:
        # slow_mo はミリ秒単位。デバッグ時に操作を目視確認しやすくなる
        browser = p.chromium.launch(headless=True, slow_mo=100)
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()
        browser.close()


def test_launch_with_channel_chrome():
    """channel 指定でインストール済みの Google Chrome を使用する"""
    with sync_playwright() as p:
        # channel="chrome" でシステムにインストールされた Chrome を利用
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()
        browser.close()


def test_launch_with_channel_msedge():
    """channel 指定でインストール済みの Microsoft Edge を使用する"""
    with sync_playwright() as p:
        # channel="msedge" でシステムにインストールされた Edge を利用
        browser = p.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()
        browser.close()


def test_launch_with_args():
    """ブラウザ引数を指定して起動する"""
    with sync_playwright() as p:
        # args でブラウザプロセスに追加の起動引数を渡す
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-extensions",      # 拡張機能を無効化
                "--disable-gpu",             # GPU アクセラレーションを無効化
                "--no-sandbox",              # サンドボックスを無効化（Docker 環境向け）
                "--window-size=1280,720",    # ウィンドウサイズを指定
            ],
        )
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()
        browser.close()


def test_browser_version():
    """ブラウザのバージョン情報を取得する"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # browser.version でブラウザのバージョン文字列を取得
        version = browser.version
        assert version is not None
        assert len(version) > 0
        print(f"Chromium バージョン: {version}")
        browser.close()


def test_browser_is_connected():
    """ブラウザの接続状態を確認する"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 起動直後は接続状態
        assert browser.is_connected() is True

        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")
        assert "Microsoft" in page.title()

        # ページ操作後も接続状態が維持されている
        assert browser.is_connected() is True

        browser.close()

        # close() 後は切断状態になる
        assert browser.is_connected() is False


def main():
    runner = TestRunner("test_01_browser_launch")
    all_tests = [
        test_launch_chromium,
        test_launch_firefox,
        test_launch_webkit,
        test_launch_headless,
        test_launch_headful,
        test_launch_with_slow_mo,
        test_launch_with_channel_chrome,
        test_launch_with_channel_msedge,
        test_launch_with_args,
        test_browser_version,
        test_browser_is_connected,
    ]
    for t in all_tests:
        runner.run(t, skip_reason=SKIP_TESTS.get(t.__name__))
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
