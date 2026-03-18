"""
test_06_assertions.py - アサーション（expect）のサンプル

Playwright の Web-first アサーションは自動的にリトライし、
条件が満たされるまで待機する。これによりフレーキーなテストを防ぐ。
"""

import re

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


# ============================================================
# ページアサーション (Page Assertions)
# ============================================================


def test_to_have_title(page: Page):
    """to_have_title - ページタイトルの検証"""
    page.set_content("<title>テストページ</title><h1>Hello</h1>")
    # 完全一致
    expect(page).to_have_title("テストページ")
    # 正規表現による部分一致
    expect(page).to_have_title(re.compile("テスト"))


def test_to_have_url(page: Page):
    """to_have_url - URL の検証"""
    page.set_content("<title>URL Test</title>")
    # about:blank から始まるURLを検証
    expect(page).to_have_url(re.compile(".*"))
    # ナビゲーション後のURL検証
    page.goto("https://example.com/")
    expect(page).to_have_url("https://example.com/")
    expect(page).to_have_url(re.compile(r"example\.com"))


# ============================================================
# ロケーターアサーション - 表示・状態 (Visibility & State)
# ============================================================


def test_to_be_visible(page: Page):
    """to_be_visible - 要素が表示されていることを検証"""
    page.set_content("""
        <div id="visible-element">見える要素</div>
        <div id="hidden-element" style="display: none;">隠れた要素</div>
    """)
    expect(page.locator("#visible-element")).to_be_visible()
    # 非表示要素は visible ではない
    expect(page.locator("#hidden-element")).not_to_be_visible()


def test_to_be_hidden(page: Page):
    """to_be_hidden - 要素が非表示であることを検証"""
    page.set_content("""
        <div id="hidden-display" style="display: none;">非表示(display)</div>
        <div id="hidden-visibility" style="visibility: hidden;">非表示(visibility)</div>
        <div id="visible-item">表示中</div>
    """)
    expect(page.locator("#hidden-display")).to_be_hidden()
    expect(page.locator("#hidden-visibility")).to_be_hidden()
    # 表示中の要素は hidden ではない
    expect(page.locator("#visible-item")).not_to_be_hidden()


def test_to_be_attached(page: Page):
    """to_be_attached - 要素がDOMにアタッチされていることを検証"""
    page.set_content("""
        <div id="attached-element">DOM に存在する要素</div>
    """)
    # DOM に存在する要素
    expect(page.locator("#attached-element")).to_be_attached()
    # DOM に存在しない要素
    expect(page.locator("#non-existent")).not_to_be_attached()


def test_to_be_enabled(page: Page):
    """to_be_enabled - 要素が有効（操作可能）であることを検証"""
    page.set_content("""
        <button id="enabled-btn">有効ボタン</button>
        <button id="disabled-btn" disabled>無効ボタン</button>
    """)
    expect(page.locator("#enabled-btn")).to_be_enabled()
    expect(page.locator("#disabled-btn")).not_to_be_enabled()


def test_to_be_disabled(page: Page):
    """to_be_disabled - 要素が無効であることを検証"""
    page.set_content("""
        <input id="disabled-input" disabled value="無効" />
        <input id="enabled-input" value="有効" />
    """)
    expect(page.locator("#disabled-input")).to_be_disabled()
    expect(page.locator("#enabled-input")).not_to_be_disabled()


def test_to_be_editable(page: Page):
    """to_be_editable - 要素が編集可能であることを検証"""
    page.set_content("""
        <input id="editable-input" value="編集可能" />
        <input id="readonly-input" readonly value="読み取り専用" />
        <input id="disabled-input" disabled value="無効" />
    """)
    expect(page.locator("#editable-input")).to_be_editable()
    expect(page.locator("#readonly-input")).not_to_be_editable()
    expect(page.locator("#disabled-input")).not_to_be_editable()


def test_to_be_empty(page: Page):
    """to_be_empty - 要素が空であることを検証"""
    page.set_content("""
        <input id="empty-input" />
        <input id="filled-input" value="入力済み" />
        <div id="empty-div"></div>
        <div id="filled-div">テキストあり</div>
    """)
    expect(page.locator("#empty-input")).to_be_empty()
    expect(page.locator("#filled-input")).not_to_be_empty()
    expect(page.locator("#empty-div")).to_be_empty()
    expect(page.locator("#filled-div")).not_to_be_empty()


def test_to_be_focused(page: Page):
    """to_be_focused - 要素がフォーカスされていることを検証"""
    page.set_content("""
        <input id="input-a" placeholder="入力欄A" />
        <input id="input-b" placeholder="入力欄B" />
    """)
    # input-a にフォーカスを当てる
    page.locator("#input-a").focus()
    expect(page.locator("#input-a")).to_be_focused()
    expect(page.locator("#input-b")).not_to_be_focused()


def test_to_be_checked(page: Page):
    """to_be_checked - チェックボックス／ラジオボタンがチェック状態であることを検証"""
    page.set_content("""
        <input type="checkbox" id="cb-checked" checked />
        <input type="checkbox" id="cb-unchecked" />
        <input type="radio" name="group" id="radio-selected" checked />
        <input type="radio" name="group" id="radio-unselected" />
    """)
    expect(page.locator("#cb-checked")).to_be_checked()
    expect(page.locator("#cb-unchecked")).not_to_be_checked()
    expect(page.locator("#radio-selected")).to_be_checked()
    expect(page.locator("#radio-unselected")).not_to_be_checked()


def test_to_be_in_viewport(page: Page):
    """to_be_in_viewport - 要素がビューポート内に表示されていることを検証"""
    page.set_content("""
        <div id="in-view" style="margin-top: 0;">ビューポート内</div>
        <div id="out-of-view" style="margin-top: 10000px;">ビューポート外</div>
    """)
    expect(page.locator("#in-view")).to_be_in_viewport()
    expect(page.locator("#out-of-view")).not_to_be_in_viewport()


# ============================================================
# ロケーターアサーション - テキスト (Text)
# ============================================================


def test_to_have_text(page: Page):
    """to_have_text - 要素のテキストが完全一致することを検証"""
    page.set_content("""
        <p id="greeting">こんにちは、世界！</p>
        <ul id="fruit-list">
            <li>りんご</li>
            <li>みかん</li>
            <li>ぶどう</li>
        </ul>
    """)
    # 単一要素のテキスト完全一致
    expect(page.locator("#greeting")).to_have_text("こんにちは、世界！")
    # 正規表現での検証
    expect(page.locator("#greeting")).to_have_text(re.compile("こんにちは"))
    # 複数要素のテキスト検証（リストの各項目）
    expect(page.locator("#fruit-list li")).to_have_text(["りんご", "みかん", "ぶどう"])


def test_to_contain_text(page: Page):
    """to_contain_text - 要素のテキストに部分一致することを検証"""
    page.set_content("""
        <p id="message">Playwright は素晴らしいテストフレームワークです</p>
        <ul id="items">
            <li>商品A - 100円</li>
            <li>商品B - 200円</li>
        </ul>
    """)
    # 部分一致
    expect(page.locator("#message")).to_contain_text("素晴らしい")
    expect(page.locator("#message")).to_contain_text(re.compile(r"テスト.*ワーク"))
    # 複数要素の部分一致
    expect(page.locator("#items li")).to_contain_text(["商品A", "商品B"])


# ============================================================
# ロケーターアサーション - 値・属性 (Values & Attributes)
# ============================================================


def test_to_have_value(page: Page):
    """to_have_value - input 要素の値を検証"""
    page.set_content("""
        <input id="name-input" value="山田太郎" />
        <textarea id="comment">コメント内容</textarea>
    """)
    expect(page.locator("#name-input")).to_have_value("山田太郎")
    expect(page.locator("#name-input")).to_have_value(re.compile("山田"))
    expect(page.locator("#comment")).to_have_value("コメント内容")


def test_to_have_values(page: Page):
    """to_have_values - 複数選択（select multiple）の値を検証"""
    page.set_content("""
        <select id="multi-select" multiple>
            <option value="apple" selected>りんご</option>
            <option value="orange">みかん</option>
            <option value="grape" selected>ぶどう</option>
        </select>
    """)
    # 選択された値を検証
    expect(page.locator("#multi-select")).to_have_values(["apple", "grape"])
    # 正規表現でも検証可能
    expect(page.locator("#multi-select")).to_have_values(
        [re.compile("app"), re.compile("gra")]
    )


def test_to_have_attribute(page: Page):
    """to_have_attribute - 要素の属性値を検証"""
    page.set_content("""
        <a id="link" href="https://example.com" target="_blank" data-testid="ext-link">
            外部リンク
        </a>
        <img id="logo" src="logo.png" alt="ロゴ画像" />
    """)
    expect(page.locator("#link")).to_have_attribute("href", "https://example.com")
    expect(page.locator("#link")).to_have_attribute("target", "_blank")
    expect(page.locator("#link")).to_have_attribute("data-testid", "ext-link")
    expect(page.locator("#logo")).to_have_attribute("alt", "ロゴ画像")


def test_to_have_class(page: Page):
    """to_have_class - 要素の CSS クラスを検証"""
    page.set_content("""
        <div id="box" class="card primary active">カードコンポーネント</div>
        <ul>
            <li class="item">項目1</li>
            <li class="item selected">項目2</li>
        </ul>
    """)
    # class 属性の完全一致
    expect(page.locator("#box")).to_have_class("card primary active")
    # 正規表現による検証
    expect(page.locator("#box")).to_have_class(re.compile("primary"))
    # 複数要素のクラス検証
    expect(page.locator("ul li")).to_have_class(["item", "item selected"])


def test_to_contain_class(page: Page):
    """to_contain_class - 要素が特定の CSS クラスを含むことを検証"""
    page.set_content("""
        <div id="element" class="btn btn-primary active large">ボタン</div>
    """)
    # 単一クラスが含まれていることを検証
    expect(page.locator("#element")).to_contain_class("btn-primary")
    # 複数クラスが含まれていることを検証
    expect(page.locator("#element")).to_contain_class(["btn", "active", "large"])


def test_to_have_css(page: Page):
    """to_have_css - 要素の CSS プロパティ値を検証"""
    page.set_content("""
        <div id="styled-box" style="color: rgb(255, 0, 0); font-size: 20px; display: flex;">
            スタイル付き要素
        </div>
    """)
    expect(page.locator("#styled-box")).to_have_css("color", "rgb(255, 0, 0)")
    expect(page.locator("#styled-box")).to_have_css("font-size", "20px")
    expect(page.locator("#styled-box")).to_have_css("display", "flex")


def test_to_have_id(page: Page):
    """to_have_id - 要素の id 属性を検証"""
    page.set_content("""
        <section id="main-content">メインコンテンツ</section>
    """)
    expect(page.locator("section")).to_have_id("main-content")
    expect(page.locator("section")).to_have_id(re.compile("main"))


# ============================================================
# ロケーターアサーション - 要素数・プロパティ (Count & Properties)
# ============================================================


def test_to_have_count(page: Page):
    """to_have_count - 要素の数を検証"""
    page.set_content("""
        <ul id="task-list">
            <li class="task">タスク1</li>
            <li class="task">タスク2</li>
            <li class="task">タスク3</li>
        </ul>
    """)
    expect(page.locator(".task")).to_have_count(3)
    # 存在しない要素は 0 個
    expect(page.locator(".completed")).to_have_count(0)


def test_to_have_js_property(page: Page):
    """to_have_js_property - 要素の JavaScript プロパティを検証"""
    page.set_content("""
        <input id="check" type="checkbox" checked />
        <input id="text" type="text" value="テスト値" />
    """)
    # チェックボックスの checked プロパティ（JS プロパティ）
    expect(page.locator("#check")).to_have_js_property("checked", True)
    expect(page.locator("#text")).to_have_js_property("type", "text")
    expect(page.locator("#text")).to_have_js_property("value", "テスト値")


# ============================================================
# ロケーターアサーション - アクセシビリティ (Accessibility)
# ============================================================


def test_to_have_accessible_name(page: Page):
    """to_have_accessible_name - 要素のアクセシブル名を検証"""
    page.set_content("""
        <button aria-label="メニューを開く">☰</button>
        <label for="email">メールアドレス</label>
        <input id="email" type="email" />
    """)
    expect(page.locator("button")).to_have_accessible_name("メニューを開く")
    expect(page.locator("#email")).to_have_accessible_name("メールアドレス")
    # 正規表現でも検証可能
    expect(page.locator("button")).to_have_accessible_name(re.compile("メニュー"))


def test_to_have_accessible_description(page: Page):
    """to_have_accessible_description - 要素のアクセシブル説明を検証"""
    page.set_content("""
        <button aria-describedby="btn-desc">送信</button>
        <span id="btn-desc">フォームの内容をサーバーに送信します</span>
    """)
    expect(page.locator("button")).to_have_accessible_description(
        "フォームの内容をサーバーに送信します"
    )
    expect(page.locator("button")).to_have_accessible_description(
        re.compile("サーバーに送信")
    )


def test_to_have_role(page: Page):
    """to_have_role - 要素の ARIA ロールを検証"""
    page.set_content("""
        <nav>ナビゲーション</nav>
        <div role="alert">警告メッセージ</div>
        <button>ボタン</button>
    """)
    expect(page.locator("nav")).to_have_role("navigation")
    expect(page.locator("[role='alert']")).to_have_role("alert")
    expect(page.locator("button")).to_have_role("button")


# ============================================================
# 否定アサーション (Negation)
# ============================================================


def test_not_to_be_visible(page: Page):
    """not_to_be_visible - 要素が表示されていないことを検証（否定アサーション）"""
    page.set_content("""
        <div id="modal" style="display: none;">
            <p>モーダルコンテンツ</p>
        </div>
        <div id="tooltip" style="opacity: 0; visibility: hidden;">ツールチップ</div>
    """)
    # not_ プレフィックスで否定アサーションを行う
    expect(page.locator("#modal")).not_to_be_visible()
    expect(page.locator("#tooltip")).not_to_be_visible()
    # DOM に存在しない要素も not_to_be_visible
    expect(page.locator("#non-existent")).not_to_be_visible()
