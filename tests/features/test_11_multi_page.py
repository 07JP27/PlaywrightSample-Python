"""
test_11_multi_page.py - マルチページ・タブ・ポップアップのサンプル

複数のタブやポップアップウィンドウの操作方法を示す。
各 Page オブジェクトは BrowserContext 内で管理される。
"""
import re

from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# 1. 新しいタブの作成 (context.new_page)
# ---------------------------------------------------------------------------
def test_new_tab(context):
    """context.new_page() で複数タブを作成し操作する"""
    # 1 枚目のページを作成
    page1 = context.new_page()
    page1.set_content("<h1>ページ1</h1>")

    # 2 枚目のページを作成
    page2 = context.new_page()
    page2.set_content("<h1>ページ2</h1>")

    # コンテキスト内に 2 ページ以上が存在する
    assert len(context.pages) >= 2

    # 各ページの内容を個別に検証
    expect(page1.locator("h1")).to_have_text("ページ1")
    expect(page2.locator("h1")).to_have_text("ページ2")


# ---------------------------------------------------------------------------
# 2. ポップアップの捕捉 (page.expect_popup)
# ---------------------------------------------------------------------------
def test_expect_popup_with_target_blank(page):
    """target='_blank' リンクによるポップアップを捕捉する"""
    page.set_content(
        '<a href="about:blank" target="_blank" id="open-link">新しいタブを開く</a>'
    )

    # expect_popup でポップアップページを捕捉
    with page.expect_popup() as popup_info:
        page.click("#open-link")
    popup = popup_info.value

    # ポップアップが開かれたことを確認
    assert popup is not None
    assert popup.url == "about:blank"
    popup.close()


# ---------------------------------------------------------------------------
# 3. 新ページイベント (context.expect_page)
# ---------------------------------------------------------------------------
def test_context_expect_page(context):
    """context.expect_page() で新規ページの作成を待機する"""
    page = context.new_page()
    page.set_content(
        '<a href="about:blank" target="_blank" id="new-tab">新しいタブ</a>'
    )

    # コンテキストレベルで新しいページイベントを待機
    with context.expect_page() as new_page_info:
        page.click("#new-tab")
    new_page = new_page_info.value

    # 新しいページが取得できることを確認
    assert new_page is not None
    new_page.wait_for_load_state()
    assert new_page.url == "about:blank"


# ---------------------------------------------------------------------------
# 4. 全ページの列挙 (context.pages)
# ---------------------------------------------------------------------------
def test_enumerate_all_pages(context):
    """context.pages で現在開いている全ページを列挙する"""
    # 3 つのページを作成
    pages = []
    for i in range(3):
        p = context.new_page()
        p.set_content(f"<h1>タブ{i + 1}</h1>")
        pages.append(p)

    # context.pages にすべてのページが含まれる
    all_pages = context.pages
    assert len(all_pages) >= 3

    # 各ページの内容を確認
    for i, p in enumerate(pages):
        expect(p.locator("h1")).to_have_text(f"タブ{i + 1}")


# ---------------------------------------------------------------------------
# 5. タブの前面化 (page.bring_to_front)
# ---------------------------------------------------------------------------
def test_bring_to_front(context):
    """page.bring_to_front() でタブを前面に持ってくる"""
    page1 = context.new_page()
    page1.set_content("<h1>背面ページ</h1>")

    page2 = context.new_page()
    page2.set_content("<h1>前面ページ</h1>")

    # page2 が最後に作成されたため前面にある → page1 を前面化
    page1.bring_to_front()

    # bring_to_front 後もページの内容は維持される
    expect(page1.locator("h1")).to_have_text("背面ページ")
    expect(page2.locator("h1")).to_have_text("前面ページ")


# ---------------------------------------------------------------------------
# 6. window.open によるポップアップ
# ---------------------------------------------------------------------------
def test_window_open_popup(page):
    """window.open() で開かれるポップアップを捕捉する"""
    page.set_content(
        """
        <button id="open-popup"
                onclick="window.open('about:blank', '_blank', 'width=400,height=300')">
            ポップアップを開く
        </button>
        """
    )

    # window.open によるポップアップも expect_popup で捕捉可能
    with page.expect_popup() as popup_info:
        page.click("#open-popup")
    popup = popup_info.value

    assert popup is not None

    # ポップアップ側にコンテンツを設定して操作
    popup.set_content("<p>ポップアップの内容</p>")
    expect(popup.locator("p")).to_have_text("ポップアップの内容")
    popup.close()


def test_window_open_with_url(page, context):
    """window.open() で特定コンテンツを持つポップアップを開く"""
    page.set_content(
        """
        <button id="open-win"
                onclick="var w = window.open('', '_blank'); w.document.write('<h1>子ウィンドウ</h1>');">
            子ウィンドウを開く
        </button>
        """
    )

    with page.expect_popup() as popup_info:
        page.click("#open-win")
    popup = popup_info.value

    # ポップアップに書き込まれた内容を確認
    expect(popup.locator("h1")).to_have_text("子ウィンドウ")

    # 親ページとポップアップが同じコンテキストに属する
    assert popup in context.pages
    popup.close()


# ---------------------------------------------------------------------------
# 複合シナリオ: 複数ページ間でのデータ受け渡し
# ---------------------------------------------------------------------------
def test_cross_page_data_flow(context):
    """複数ページ間で localStorage を使いデータを共有する"""
    # 同一オリジンの 2 ページを作成（data: URI は localStorage 不可のため
    # set_content で同一オリジンにする）
    page1 = context.new_page()
    page1.goto("about:blank")
    page2 = context.new_page()
    page2.goto("about:blank")

    # page1 で localStorage に値をセット
    page1.evaluate("() => localStorage.setItem('shared_key', 'こんにちは')")

    # page2 から同じ値を読み取れることを確認
    value = page2.evaluate("() => localStorage.getItem('shared_key')")
    assert value == "こんにちは"


def test_close_page_and_verify(context):
    """ページを閉じた後、context.pages から除外されることを確認する"""
    page1 = context.new_page()
    page2 = context.new_page()
    page3 = context.new_page()

    initial_count = len(context.pages)

    # page2 を閉じる
    page2.close()

    # ページ数が 1 減っている
    assert len(context.pages) == initial_count - 1

    # 閉じたページが一覧に含まれない
    assert page2 not in context.pages

    # 残りのページは引き続き操作可能
    page1.set_content("<p>まだ開いています</p>")
    expect(page1.locator("p")).to_have_text("まだ開いています")
