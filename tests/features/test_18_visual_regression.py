"""
test_18_visual_regression.py - ビジュアルリグレッション（視覚比較）のサンプル

スクリーンショットベースの視覚的なリグレッションテストを示す。
初回実行時にベースライン画像が作成され、以降の実行で比較される。
ベースライン更新: pytest --update-snapshots
"""

import pytest
from playwright.sync_api import Page, expect, sync_playwright


@pytest.fixture(scope="module")
def browser():
    """Playwright ブラウザの起動と終了を管理"""
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    yield browser
    browser.close()
    pw.stop()

@pytest.fixture
def context(browser):
    """各テスト用のブラウザコンテキストを作成"""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="ja-JP",
        timezone_id="Asia/Tokyo",
    )
    yield context
    context.close()

@pytest.fixture
def page(context):
    """各テスト用のページを作成"""
    page = context.new_page()
    yield page
    page.close()


# =============================================================================
# 1. ページスクリーンショット比較
#    expect(page).to_have_screenshot() でページ全体のスクリーンショットを比較する
# =============================================================================


def test_page_screenshot_comparison(page: Page):
    """ページスクリーンショット比較"""
    # 決定論的な結果を得るために固定スタイルのHTMLを使用
    page.set_content('''
        <div style="width:200px;height:100px;background:blue;color:white;
                    display:flex;align-items:center;justify-content:center;
                    font-family:Arial;">
            テスト要素
        </div>
    ''')
    # ページ全体のスクリーンショットをベースラインと比較
    expect(page).to_have_screenshot("page_basic.png")


# =============================================================================
# 2. 要素スクリーンショット比較
#    expect(locator).to_have_screenshot() で特定の要素のみを比較する
# =============================================================================


def test_element_screenshot_comparison(page: Page):
    """要素スクリーンショット比較"""
    page.set_content('''
        <div style="padding:20px;background:#f0f0f0;">
            <button id="target-btn"
                    style="padding:10px 20px;background:green;color:white;
                           border:none;border-radius:4px;font-size:16px;
                           font-family:Arial;cursor:pointer;">
                送信ボタン
            </button>
            <p style="font-family:Arial;">この段落は比較対象外</p>
        </div>
    ''')
    # ボタン要素だけをスクリーンショット比較（周囲の要素は無視される）
    button = page.locator("#target-btn")
    expect(button).to_have_screenshot("element_button.png")


# =============================================================================
# 3. フルページスクリーンショット比較
#    full_page=True でスクロール領域を含むページ全体をキャプチャする
# =============================================================================


def test_full_page_screenshot_comparison(page: Page):
    """フルページスクリーンショット比較（スクロール領域を含む）"""
    # ビューポートより長いコンテンツを生成
    items = "".join(
        f'<div style="padding:10px;margin:5px;background:{"#e0e0ff" if i % 2 == 0 else "#ffe0e0"}; '
        f'font-family:Arial;font-size:14px;">項目 {i + 1}</div>'
        for i in range(20)
    )
    page.set_content(f'''
        <div style="width:300px;">
            <h2 style="font-family:Arial;color:#333;">リスト一覧</h2>
            {items}
        </div>
    ''')
    # full_page=True でスクロール可能な領域全体をキャプチャ
    expect(page).to_have_screenshot("full_page_list.png", full_page=True)


# =============================================================================
# 4. 差分許容値の設定
#    max_diff_pixels / max_diff_pixel_ratio で許容するピクセル差分を設定
# =============================================================================


def test_screenshot_with_max_diff_pixels(page: Page):
    """差分許容値の設定 - max_diff_pixels"""
    page.set_content('''
        <div style="width:200px;height:100px;background:#3366cc;color:white;
                    display:flex;align-items:center;justify-content:center;
                    font-family:Arial;font-size:18px;">
            許容テスト
        </div>
    ''')
    # 最大100ピクセルまでの差分を許容する
    # アンチエイリアシングやレンダリングエンジンの差異に対応
    expect(page).to_have_screenshot(
        "tolerance_pixels.png",
        max_diff_pixels=100,
    )


def test_screenshot_with_max_diff_pixel_ratio(page: Page):
    """差分許容値の設定 - max_diff_pixel_ratio"""
    page.set_content('''
        <div style="width:200px;height:100px;background:#cc6633;color:white;
                    display:flex;align-items:center;justify-content:center;
                    font-family:Arial;font-size:18px;">
            比率テスト
        </div>
    ''')
    # 全体の1%までの差分を許容する（0.01 = 1%）
    # 環境差異が大きい場合はこちらが便利
    expect(page).to_have_screenshot(
        "tolerance_ratio.png",
        max_diff_pixel_ratio=0.01,
    )


# =============================================================================
# 5. スクリーンショット名の指定
#    name引数で保存されるスクリーンショットファイル名を明示的に設定する
# =============================================================================


def test_screenshot_with_custom_name(page: Page):
    """スクリーンショット名の指定"""
    page.set_content('''
        <div style="width:300px;padding:20px;background:white;
                    border:2px solid #333;font-family:Arial;">
            <h3 style="color:#333;margin:0 0 10px;">カスタム名テスト</h3>
            <p style="color:#666;margin:0;font-size:14px;">
                スクリーンショットのファイル名を明示的に指定します。
            </p>
        </div>
    ''')
    # 名前を指定してスクリーンショットを保存・比較
    # ファイルはテストスナップショットディレクトリに保存される
    expect(page).to_have_screenshot("custom-named-screenshot.png")


def test_element_screenshot_with_custom_name(page: Page):
    """要素スクリーンショットに名前を指定"""
    page.set_content('''
        <nav style="display:flex;gap:10px;padding:10px;background:#333;
                    font-family:Arial;">
            <a href="#" style="color:white;text-decoration:none;padding:5px 10px;">ホーム</a>
            <a href="#" style="color:white;text-decoration:none;padding:5px 10px;">概要</a>
            <a href="#" style="color:white;text-decoration:none;padding:5px 10px;">連絡先</a>
        </nav>
    ''')
    nav = page.locator("nav")
    # 要素スクリーンショットにもカスタム名を指定可能
    expect(nav).to_have_screenshot("navigation-bar.png")
