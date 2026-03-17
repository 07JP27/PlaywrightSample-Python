"""
test_12_frames.py - Frame / iframe 操作のサンプル

iframe 内の要素にアクセスするための frame_locator と
Frame API の使い方を示す。
"""

import re

from playwright.sync_api import Page, expect


# ============================================================
# 1. frame_locator による iframe 内要素の操作（推奨方法）
# ============================================================


def test_frame_locator(page: Page):
    """frame_locator による iframe 内要素の操作"""
    page.set_content('''
        <iframe id="myframe" srcdoc="<button id='btn'>iframe内ボタン</button>"></iframe>
    ''')
    # frame_locator で iframe 内の要素を操作
    frame = page.frame_locator("#myframe")
    frame.locator("#btn").click()
    expect(frame.locator("#btn")).to_have_text("iframe内ボタン")


def test_frame_locator_with_form(page: Page):
    """frame_locator でフォーム要素を操作する"""
    page.set_content('''
        <iframe id="form-frame" srcdoc="
            <form>
                <input id='name' type='text' placeholder='名前' />
                <select id='color'>
                    <option value='red'>赤</option>
                    <option value='blue'>青</option>
                </select>
                <input id='agree' type='checkbox' />
            </form>
        "></iframe>
    ''')
    frame = page.frame_locator("#form-frame")

    # テキスト入力
    frame.locator("#name").fill("テスト太郎")
    expect(frame.locator("#name")).to_have_value("テスト太郎")

    # セレクトボックス選択
    frame.locator("#color").select_option("blue")
    expect(frame.locator("#color")).to_have_value("blue")

    # チェックボックス操作
    frame.locator("#agree").check()
    expect(frame.locator("#agree")).to_be_checked()


# ============================================================
# 2. frame(name=...) による Frame 取得
# ============================================================


def test_frame_by_name(page: Page):
    """name 属性を使って Frame を取得する"""
    page.set_content('''
        <iframe name="content-frame" srcdoc="
            <h1 id='title'>フレーム内タイトル</h1>
            <p id='desc'>これはフレーム内の説明です</p>
        "></iframe>
    ''')
    # name 属性で Frame オブジェクトを取得
    frame = page.frame(name="content-frame")
    assert frame is not None, "name='content-frame' のフレームが見つかること"

    # Frame 内の要素を操作
    title_text = frame.locator("#title").text_content()
    assert title_text == "フレーム内タイトル"

    desc_text = frame.locator("#desc").text_content()
    assert desc_text == "これはフレーム内の説明です"


def test_frame_by_name_not_found(page: Page):
    """存在しない name を指定すると None が返る"""
    page.set_content('<iframe name="existing" srcdoc="<p>内容</p>"></iframe>')

    # 存在しないフレーム名
    frame = page.frame(name="nonexistent")
    assert frame is None, "存在しない name では None が返ること"


# ============================================================
# 3. frame(url=...) による Frame 取得
# ============================================================


def test_frame_by_url_string(page: Page):
    """URL 文字列（部分一致）で Frame を取得する"""
    # srcdoc の場合、URL は about:srcdoc になる
    page.set_content('''
        <iframe name="url-frame" srcdoc="<p id='msg'>URL検索テスト</p>"></iframe>
    ''')
    # about:srcdoc で部分一致検索
    frame = page.frame(url="about:srcdoc")
    assert frame is not None, "URL で Frame が取得できること"
    assert frame.locator("#msg").text_content() == "URL検索テスト"


def test_frame_by_url_pattern(page: Page):
    """正規表現パターンで Frame を取得する"""
    page.set_content('''
        <iframe name="pattern-frame" srcdoc="<p id='info'>パターン検索</p>"></iframe>
    ''')
    # 正規表現で URL をマッチ
    frame = page.frame(url=re.compile(r"about:srcdoc"))
    assert frame is not None, "正規表現で Frame が取得できること"
    assert frame.locator("#info").text_content() == "パターン検索"


# ============================================================
# 4. 全フレーム列挙 (page.frames)
# ============================================================


def test_page_frames_list(page: Page):
    """page.frames で全フレームを列挙する"""
    page.set_content('''
        <iframe name="frame-a" srcdoc="<p>フレームA</p>"></iframe>
        <iframe name="frame-b" srcdoc="<p>フレームB</p>"></iframe>
        <iframe name="frame-c" srcdoc="<p>フレームC</p>"></iframe>
    ''')
    # すべての iframe のロードを待つ
    page.frame_locator("[name='frame-c']").locator("p").wait_for()

    frames = page.frames
    # メインフレーム + 3 つの iframe = 少なくとも 4 フレーム
    assert len(frames) >= 4, f"フレーム数は4以上: 実際は{len(frames)}"

    # フレーム名を収集
    frame_names = [f.name for f in frames]
    assert "frame-a" in frame_names
    assert "frame-b" in frame_names
    assert "frame-c" in frame_names


def test_frames_url_property(page: Page):
    """各フレームの URL プロパティを確認する"""
    page.set_content('''
        <iframe name="check-url" srcdoc="<p>URL確認</p>"></iframe>
    ''')
    page.frame_locator("[name='check-url']").locator("p").wait_for()

    for frame in page.frames:
        # すべてのフレームは URL を持つ
        assert frame.url is not None, "各フレームは URL を持つこと"

    # srcdoc フレームの URL は about:srcdoc
    srcdoc_frame = page.frame(name="check-url")
    assert srcdoc_frame is not None
    assert srcdoc_frame.url == "about:srcdoc"


# ============================================================
# 5. メインフレーム (page.main_frame)
# ============================================================


def test_main_frame(page: Page):
    """page.main_frame でメインフレームを取得する"""
    page.set_content('''
        <h1 id="main-title">メインページ</h1>
        <iframe name="sub" srcdoc="<p>サブフレーム</p>"></iframe>
    ''')
    main = page.main_frame

    # メインフレームはページ自体のフレーム
    assert main is not None, "メインフレームが取得できること"
    assert main.name == "", "メインフレームの name は空文字"

    # メインフレームから要素を操作
    title = main.locator("#main-title").text_content()
    assert title == "メインページ"


def test_main_frame_is_first_in_frames(page: Page):
    """page.frames の先頭がメインフレームであることを確認"""
    page.set_content('''
        <iframe name="child" srcdoc="<p>子フレーム</p>"></iframe>
    ''')
    page.frame_locator("[name='child']").locator("p").wait_for()

    # frames リストの先頭はメインフレーム
    assert page.frames[0] == page.main_frame, "先頭フレームはメインフレーム"


def test_main_frame_parent_is_none(page: Page):
    """メインフレームの parent_frame は None"""
    main = page.main_frame
    assert main.parent_frame is None, "メインフレームに親フレームはない"


# ============================================================
# 6. ネストされた iframe 操作
# ============================================================


def test_nested_iframes(page: Page):
    """ネストされた iframe（二重 iframe）内の要素を操作する"""
    page.set_content('''
        <iframe id="outer" srcdoc="
            <h2 id='outer-title'>外側フレーム</h2>
            <iframe id='inner' srcdoc='<button id=nested-btn>ネストボタン</button>'></iframe>
        "></iframe>
    ''')
    # 外側 → 内側と frame_locator を連鎖してアクセス
    outer = page.frame_locator("#outer")
    inner = outer.frame_locator("#inner")

    expect(inner.locator("#nested-btn")).to_have_text("ネストボタン")
    inner.locator("#nested-btn").click()


def test_nested_iframe_outer_content(page: Page):
    """ネストされた iframe で外側フレームの要素も操作できること"""
    page.set_content('''
        <iframe id="outer2" srcdoc="
            <p id='outer-msg'>外側メッセージ</p>
            <iframe id='inner2' srcdoc='<p id=inner-msg>内側メッセージ</p>'></iframe>
        "></iframe>
    ''')
    outer = page.frame_locator("#outer2")

    # 外側フレームの要素
    expect(outer.locator("#outer-msg")).to_have_text("外側メッセージ")

    # 内側フレームの要素
    inner = outer.frame_locator("#inner2")
    expect(inner.locator("#inner-msg")).to_have_text("内側メッセージ")


def test_frame_parent_frame(page: Page):
    """parent_frame で親フレームを辿れることを確認"""
    page.set_content('''
        <iframe name="parent-f" srcdoc="
            <iframe name='child-f' srcdoc='<p>子</p>'></iframe>
        "></iframe>
    ''')
    # 子フレームのロードを待つ
    page.frame_locator("[name='parent-f']").frame_locator(
        "[name='child-f']"
    ).locator("p").wait_for()

    child = page.frame(name="child-f")
    assert child is not None, "子フレームが取得できること"

    # 親フレームを辿る
    parent = child.parent_frame
    assert parent is not None, "親フレームが取得できること"
    assert parent.name == "parent-f", "親フレームの name が正しいこと"

    # さらに上はメインフレーム
    grandparent = parent.parent_frame
    assert grandparent == page.main_frame, "祖父フレームはメインフレーム"
