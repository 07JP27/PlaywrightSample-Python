"""
test_16_screenshots_video.py - スクリーンショット・動画・PDF のサンプル

ページやUI要素のキャプチャ、テスト実行の録画、PDF出力を示す。
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

from runner import TestRunner

SKIP_TESTS = {}

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# 1. ページスクリーンショット
# ---------------------------------------------------------------------------
def test_page_screenshot():
    """ページスクリーンショット"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content("<h1>スクリーンショットテスト</h1><p>コンテンツ</p>")
        output_path = str(PROJECT_ROOT / "output" / "screenshots" / "page.png")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        page.screenshot(path=output_path)
        assert os.path.exists(output_path)
        browser.close()


# ---------------------------------------------------------------------------
# 2. フルページスクリーンショット
# ---------------------------------------------------------------------------
def test_full_page_screenshot():
    """フルページスクリーンショット（スクロール領域を含む全体をキャプチャ）"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # スクロールが必要な長いページを作成
        long_content = "<h1>フルページテスト</h1>" + "".join(
            f"<p>段落 {i}</p>" for i in range(50)
        )
        page.set_content(long_content)
        output_path = str(
            PROJECT_ROOT / "output" / "screenshots" / "full_page.png"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        page.screenshot(path=output_path, full_page=True)
        assert os.path.exists(output_path)
        # フルページは通常のビューポートより縦に大きくなる
        file_size = os.path.getsize(output_path)
        assert file_size > 0
        browser.close()


# ---------------------------------------------------------------------------
# 3. 要素スクリーンショット
# ---------------------------------------------------------------------------
def test_element_screenshot():
    """特定の要素だけをスクリーンショットとして取得"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(
            """
            <div style="padding: 20px;">
                <h1>ページタイトル</h1>
                <div id="target"
                     style="background: #4CAF50; color: white;
                            padding: 40px; border-radius: 8px;">
                    <p>この要素だけキャプチャされます</p>
                </div>
                <p>この部分は含まれません</p>
            </div>
            """
        )
        output_path = str(
            PROJECT_ROOT / "output" / "screenshots" / "element.png"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # locator.screenshot() で要素単位のキャプチャ
        page.locator("#target").screenshot(path=output_path)
        assert os.path.exists(output_path)
        browser.close()


# ---------------------------------------------------------------------------
# 4. クリップ（領域指定）スクリーンショット
# ---------------------------------------------------------------------------
def test_clip_screenshot():
    """指定した矩形領域のみをキャプチャ"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(
            """
            <div style="width: 800px; height: 600px;
                        background: linear-gradient(135deg, #667eea, #764ba2);">
                <h1 style="color: white; padding: 20px;">クリップテスト</h1>
            </div>
            """
        )
        output_path = str(
            PROJECT_ROOT / "output" / "screenshots" / "clip.png"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # clip で矩形領域（x, y, width, height）を指定
        page.screenshot(
            path=output_path,
            clip={"x": 0, "y": 0, "width": 400, "height": 300},
        )
        assert os.path.exists(output_path)
        browser.close()


# ---------------------------------------------------------------------------
# 5. スクリーンショット形式指定 (JPEG + 品質)
# ---------------------------------------------------------------------------
def test_jpeg_screenshot():
    """JPEG 形式でスクリーンショットを保存（品質指定あり）"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(
            "<h1>JPEG テスト</h1><p>品質 80 で保存されます</p>"
        )
        output_path = str(
            PROJECT_ROOT / "output" / "screenshots" / "page.jpeg"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # type="jpeg" と quality（0-100）を指定
        page.screenshot(path=output_path, type="jpeg", quality=80)
        assert os.path.exists(output_path)
        browser.close()


# ---------------------------------------------------------------------------
# 6. 動画記録
# ---------------------------------------------------------------------------
def test_video_recording():
    """テスト実行中の画面を動画として記録"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        video_dir = str(PROJECT_ROOT / "output" / "videos")
        os.makedirs(video_dir, exist_ok=True)
        # コンテキスト作成時に record_video_dir を指定すると録画開始
        context = browser.new_context(record_video_dir=video_dir)
        page = context.new_page()
        # いくつかの操作を記録
        page.set_content("<h1>動画テスト</h1>")
        page.set_content("<h1>ページ 2</h1><p>遷移しました</p>")
        page.set_content("<h1>ページ 3</h1><p>最後のページ</p>")
        # 動画パスはコンテキストを閉じた後に確定する
        video_path = page.video.path()
        # コンテキストを閉じると動画ファイルが書き出される
        context.close()
        assert os.path.exists(video_path)
        assert os.path.getsize(video_path) > 0
        browser.close()


# ---------------------------------------------------------------------------
# 7. 動画サイズ指定
# ---------------------------------------------------------------------------
def test_video_recording_with_size():
    """動画の解像度を指定して記録"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        video_dir = str(PROJECT_ROOT / "output" / "videos")
        os.makedirs(video_dir, exist_ok=True)
        # record_video_size で録画解像度を指定
        context = browser.new_context(
            record_video_dir=video_dir,
            record_video_size={"width": 640, "height": 480},
        )
        page = context.new_page()
        page.set_content(
            "<h1>動画サイズ指定テスト</h1>"
            "<p>640x480 で録画されます</p>"
        )
        video_path = page.video.path()
        context.close()
        assert os.path.exists(video_path)
        assert os.path.getsize(video_path) > 0
        browser.close()


# ---------------------------------------------------------------------------
# 8. PDF 生成（Chromium + ヘッドレスのみ）
# ---------------------------------------------------------------------------
def test_pdf_generation():
    """ページを PDF として出力（Chromium のヘッドレスモードのみ対応）"""
    with sync_playwright() as p:
        # PDF 生成は Chromium のヘッドレスモードでのみ利用可能
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(
            """
            <html>
            <head>
                <style>
                    body { font-family: sans-serif; margin: 40px; }
                    h1 { color: #333; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px;
                             text-align: left; }
                    th { background-color: #4CAF50; color: white; }
                </style>
            </head>
            <body>
                <h1>PDF 出力サンプル</h1>
                <p>Playwright で生成された PDF ドキュメントです。</p>
                <table>
                    <tr><th>項目</th><th>値</th></tr>
                    <tr><td>テスト名</td><td>PDF生成テスト</td></tr>
                    <tr><td>ブラウザ</td><td>Chromium</td></tr>
                </table>
            </body>
            </html>
            """
        )
        output_path = str(PROJECT_ROOT / "output" / "pdf" / "report.pdf")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # format, margin などのオプションで体裁を調整可能
        page.pdf(
            path=output_path,
            format="A4",
            margin={"top": "20mm", "bottom": "20mm",
                    "left": "15mm", "right": "15mm"},
            print_background=True,
        )
        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0
        browser.close()


def main():
    runner = TestRunner("test_16_screenshots_video")
    all_tests = [
        test_page_screenshot,
        test_full_page_screenshot,
        test_element_screenshot,
        test_clip_screenshot,
        test_jpeg_screenshot,
        test_video_recording,
        test_video_recording_with_size,
        test_pdf_generation,
    ]
    for t in all_tests:
        runner.run(t, skip_reason=SKIP_TESTS.get(t.__name__))
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
