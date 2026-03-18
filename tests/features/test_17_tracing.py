"""
test_17_tracing.py - トレーシングのサンプル

テスト実行のトレースを記録し、Trace Viewer で分析する方法を示す。
トレースにはスクリーンショット、DOM スナップショット、ネットワークログが含まれる。
記録したトレースは `playwright show-trace <trace.zip>` で閲覧可能。
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

from runner import TestRunner

SKIP_TESTS = {}

# プロジェクトルートと出力ディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent
TRACES_DIR = PROJECT_ROOT / "output" / "traces"


# ---------------------------------------------------------------------------
# 1. トレースの開始と停止 (context.tracing.start / stop)
# ---------------------------------------------------------------------------
def test_basic_tracing():
    """基本的なトレース記録"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        # トレースの記録を開始
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = context.new_page()
        page.set_content("<h1>トレーステスト</h1>")
        page.locator("h1").click()

        # トレースを停止してファイルに保存
        trace_path = str(TRACES_DIR / "basic_trace.zip")
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        context.tracing.stop(path=trace_path)

        assert os.path.exists(trace_path)
        browser.close()


# ---------------------------------------------------------------------------
# 2. スクリーンショット付きトレース (screenshots=True)
# ---------------------------------------------------------------------------
def test_tracing_with_screenshots():
    """スクリーンショット付きトレース - 各アクション時の画面キャプチャを含む"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        # screenshots=True でアクションごとのスクリーンショットを記録
        context.tracing.start(screenshots=True, snapshots=False, sources=False)

        page = context.new_page()
        page.set_content("""
            <h1>スクリーンショット付きトレース</h1>
            <button id="btn">クリック</button>
            <p id="result"></p>
        """)

        # 複数アクションを実行してスクリーンショットを蓄積
        page.locator("#btn").click()
        page.evaluate(
            "document.getElementById('result').textContent = 'クリック済み'"
        )

        trace_path = str(TRACES_DIR / "screenshots_trace.zip")
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        context.tracing.stop(path=trace_path)

        # トレースファイルが生成されていることを確認
        assert os.path.exists(trace_path)
        assert os.path.getsize(trace_path) > 0
        browser.close()


# ---------------------------------------------------------------------------
# 3. スナップショット付きトレース (snapshots=True)
# ---------------------------------------------------------------------------
def test_tracing_with_snapshots():
    """スナップショット付きトレース - 各アクション時の DOM スナップショットを含む"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        # snapshots=True で DOM スナップショットを記録
        context.tracing.start(screenshots=False, snapshots=True, sources=False)

        page = context.new_page()
        page.set_content("""
            <ul id="list">
                <li>項目1</li>
                <li>項目2</li>
            </ul>
        """)

        # DOM を変更して複数のスナップショットを記録
        page.evaluate("""
            const li = document.createElement('li');
            li.textContent = '項目3（動的追加）';
            document.getElementById('list').appendChild(li);
        """)

        # 変更後の DOM 状態を確認
        items = page.locator("#list li")
        assert items.count() == 3

        trace_path = str(TRACES_DIR / "snapshots_trace.zip")
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        context.tracing.stop(path=trace_path)

        assert os.path.exists(trace_path)
        assert os.path.getsize(trace_path) > 0
        browser.close()


# ---------------------------------------------------------------------------
# 4. ソースコード付きトレース (sources=True)
# ---------------------------------------------------------------------------
def test_tracing_with_sources():
    """ソースコード付きトレース - テストのソースコードをトレースに埋め込む"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        # sources=True でテストのソースコードをトレースに含める
        # Trace Viewer でアクションに対応するコード行をハイライト表示できる
        context.tracing.start(screenshots=False, snapshots=False, sources=True)

        page = context.new_page()
        page.set_content("""
            <form>
                <input type="text" id="name" placeholder="名前" />
                <input type="email" id="email" placeholder="メール" />
                <button type="submit">送信</button>
            </form>
        """)

        # フォーム操作を実行（ソースコードの各行がトレースに記録される）
        page.locator("#name").fill("テスト太郎")
        page.locator("#email").fill("test@example.com")

        trace_path = str(TRACES_DIR / "sources_trace.zip")
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        context.tracing.stop(path=trace_path)

        assert os.path.exists(trace_path)
        assert os.path.getsize(trace_path) > 0
        browser.close()


# ---------------------------------------------------------------------------
# 5. トレースのチャンク分割 (start_chunk / stop_chunk)
# ---------------------------------------------------------------------------
def test_tracing_chunks():
    """トレースのチャンク分割 - テストをフェーズごとに分割して記録する"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        # トレース全体を開始（チャンクに分割する場合もまず start が必要）
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = context.new_page()

        # --- チャンク1: ログインフェーズ ---
        page.set_content("""
            <form id="login-form">
                <input type="text" id="username" />
                <input type="password" id="password" />
                <button type="submit" id="login-btn">ログイン</button>
            </form>
        """)
        page.locator("#username").fill("user01")
        page.locator("#password").fill("password123")
        page.locator("#login-btn").click()

        # チャンク1 を保存
        chunk1_path = str(TRACES_DIR / "chunk_login.zip")
        os.makedirs(os.path.dirname(chunk1_path), exist_ok=True)
        context.tracing.stop_chunk(path=chunk1_path)

        # --- チャンク2: ダッシュボードフェーズ ---
        context.tracing.start_chunk()

        page.set_content("""
            <div id="dashboard">
                <h1>ダッシュボード</h1>
                <nav>
                    <a href="#" id="profile-link">プロフィール</a>
                    <a href="#" id="settings-link">設定</a>
                </nav>
            </div>
        """)
        page.locator("#profile-link").click()

        # チャンク2 を保存
        chunk2_path = str(TRACES_DIR / "chunk_dashboard.zip")
        context.tracing.stop_chunk(path=chunk2_path)

        # --- チャンク3: 設定フェーズ ---
        context.tracing.start_chunk()

        page.set_content("""
            <div id="settings">
                <h1>設定</h1>
                <label>
                    <input type="checkbox" id="notifications" />
                    通知を有効にする
                </label>
                <button id="save-btn">保存</button>
            </div>
        """)
        page.locator("#notifications").check()
        page.locator("#save-btn").click()

        # チャンク3 を保存
        chunk3_path = str(TRACES_DIR / "chunk_settings.zip")
        context.tracing.stop_chunk(path=chunk3_path)

        # 全チャンクのトレースファイルが生成されていることを確認
        assert os.path.exists(chunk1_path), "チャンク1（ログイン）のトレースが存在しない"
        assert os.path.exists(chunk2_path), "チャンク2（ダッシュボード）のトレースが存在しない"
        assert os.path.exists(chunk3_path), "チャンク3（設定）のトレースが存在しない"

        browser.close()


def test_tracing_all_options():
    """全オプションを有効にしたトレース記録"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()

        # 全オプションを有効化して最も詳細なトレースを記録
        context.tracing.start(
            screenshots=True,
            snapshots=True,
            sources=True,
            title="全オプション有効トレース",
        )

        page = context.new_page()
        page.set_content("""
            <div id="app">
                <h1>完全なトレーステスト</h1>
                <input type="text" id="search" placeholder="検索..." />
                <button id="search-btn">検索</button>
                <div id="results"></div>
            </div>
        """)

        # 一連の操作を実行
        page.locator("#search").fill("Playwright")
        page.locator("#search-btn").click()
        page.evaluate("""
            document.getElementById('results').innerHTML =
                '<p>検索結果: Playwright は E2E テストフレームワークです</p>';
        """)

        # 結果の確認
        result_text = page.locator("#results p").text_content()
        assert "Playwright" in result_text

        trace_path = str(TRACES_DIR / "all_options_trace.zip")
        os.makedirs(os.path.dirname(trace_path), exist_ok=True)
        context.tracing.stop(path=trace_path)

        assert os.path.exists(trace_path)
        assert os.path.getsize(trace_path) > 0
        browser.close()


def main():
    runner = TestRunner("test_17_tracing")
    all_tests = [
        test_basic_tracing,
        test_tracing_with_screenshots,
        test_tracing_with_snapshots,
        test_tracing_with_sources,
        test_tracing_chunks,
        test_tracing_all_options,
    ]
    for t in all_tests:
        runner.run(t, skip_reason=SKIP_TESTS.get(t.__name__))
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
