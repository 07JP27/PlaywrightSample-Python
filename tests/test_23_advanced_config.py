"""
test_23_advanced_config.py - 高度な接続・設定のサンプル

永続コンテキスト、CDP（Chrome DevTools Protocol）接続、
CDPSession を使った低レベル操作など、高度な設定を示す。
"""

import pytest
import tempfile
from playwright.sync_api import sync_playwright


# ---------------------------------------------------------------------------
# 1. 永続コンテキスト (launch_persistent_context)
# ---------------------------------------------------------------------------
def test_persistent_context():
    """永続コンテキスト - セッションデータを保持

    launch_persistent_context は、ユーザーデータディレクトリを指定して
    ブラウザを起動する。Cookie やローカルストレージなどのセッション情報が
    ディレクトリに永続化されるため、テスト間でログイン状態を維持できる。
    """
    with sync_playwright() as p:
        # 一時ディレクトリをユーザーデータとして使用
        with tempfile.TemporaryDirectory() as user_data_dir:
            context = p.chromium.launch_persistent_context(
                user_data_dir,
                headless=True,
            )
            page = context.new_page()
            page.goto("https://www.microsoft.com/ja-jp")
            assert "Microsoft" in page.title()

            # 永続コンテキストではコンテキスト自体を閉じる
            context.close()


# ---------------------------------------------------------------------------
# 2. CDP 接続 (connect_over_cdp) - 外部ブラウザが必要なため skip
# ---------------------------------------------------------------------------
@pytest.mark.skip(reason="CDP 接続は外部ブラウザが必要（デモ用コード）")
def test_connect_over_cdp():
    """CDP 接続 - 既存の Chrome ブラウザに接続

    事前に `chrome --remote-debugging-port=9222` で起動した
    ブラウザインスタンスに接続する。CI 環境では利用不可。
    """
    with sync_playwright() as p:
        # リモートデバッグポートに接続
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        print(f"現在の URL: {page.url}")
        print(f"タイトル: {page.title()}")
        browser.close()


# ---------------------------------------------------------------------------
# 3. CDPSession の使用 (Performance メトリクス取得)
# ---------------------------------------------------------------------------
def test_cdp_session_performance_metrics():
    """CDPSession - Performance メトリクスを取得

    CDPSession を使うと Chrome DevTools Protocol コマンドを
    直接送信でき、ブラウザの低レベル情報にアクセスできる。
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.microsoft.com/ja-jp")

        # CDPSession を作成して Performance ドメインを有効化
        cdp = page.context.new_cdp_session(page)
        cdp.send("Performance.enable")

        # メトリクスを取得
        result = cdp.send("Performance.getMetrics")
        assert "metrics" in result
        assert len(result["metrics"]) > 0

        # メトリクス名の一覧を確認（例: Timestamp, Documents, JSHeapUsedSize）
        metric_names = [m["name"] for m in result["metrics"]]
        assert "Timestamp" in metric_names
        assert "JSHeapUsedSize" in metric_names

        cdp.detach()
        browser.close()


# ---------------------------------------------------------------------------
# 4. ネットワーク条件エミュレーション（CDPSession 経由、Slow 3G）
# ---------------------------------------------------------------------------
def test_cdp_network_emulation_slow3g():
    """CDPSession - Slow 3G ネットワーク条件をエミュレーション

    Network.emulateNetworkConditions で帯域幅やレイテンシを制限し、
    低速ネットワーク環境でのページ挙動をテストできる。
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # CDPSession でネットワーク条件を設定（Slow 3G 相当）
        cdp = page.context.new_cdp_session(page)
        cdp.send(
            "Network.emulateNetworkConditions",
            {
                "offline": False,
                "downloadThroughput": 500 * 1024 / 8,    # 500 kbps
                "uploadThroughput": 500 * 1024 / 8,      # 500 kbps
                "latency": 400,                           # 400ms RTT
            },
        )

        # Slow 3G 条件下でページを読み込み
        page.goto("https://www.microsoft.com/ja-jp", timeout=60000)
        assert "Microsoft" in page.title()

        # ネットワーク条件を解除
        cdp.send(
            "Network.emulateNetworkConditions",
            {
                "offline": False,
                "downloadThroughput": -1,
                "uploadThroughput": -1,
                "latency": 0,
            },
        )

        cdp.detach()
        browser.close()


# ---------------------------------------------------------------------------
# 5. ブラウザ起動オプション（説明用テスト）
# ---------------------------------------------------------------------------
def test_browser_launch_options():
    """ブラウザ起動オプションの代表例

    launch() に渡せる主要なオプション:
      - headless: ヘッドレスモード (デフォルト True)
      - slow_mo: 各操作間の遅延 (ms)、デバッグ時に便利
      - downloads_path: ダウンロードファイルの保存先
      - executable_path: 使用するブラウザの実行ファイルパス
      - args: ブラウザに渡す追加の起動引数
      - chromium_sandbox: Chromium サンドボックスの有効/無効
      - proxy: プロキシサーバー設定
      - timeout: 起動タイムアウト (ms)
    """
    with sync_playwright() as p:
        with tempfile.TemporaryDirectory() as downloads_dir:
            browser = p.chromium.launch(
                headless=True,
                slow_mo=0,
                downloads_path=downloads_dir,
                # executable_path="/path/to/chrome"  # カスタムブラウザを指定する場合
                args=["--disable-extensions"],
            )
            page = browser.new_page()
            page.goto("https://www.microsoft.com/ja-jp")
            assert "Microsoft" in page.title()

            browser.close()
