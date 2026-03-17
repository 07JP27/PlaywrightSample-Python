"""
test_13_shadow_dom.py - Shadow DOM のサンプル

Playwright の locator() は Shadow DOM を自動的に貫通（pierce）するため、
通常のセレクタで Shadow DOM 内の要素にアクセスできる。
"""

import re

from playwright.sync_api import Page, expect


# ============================================================
# Shadow DOM 内の要素へのアクセス
# ============================================================


def test_shadow_dom_access(page: Page):
    """Shadow DOM 内の要素にアクセス"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = '<button id="shadow-btn">Shadow Button</button>';
        </script>
    """)

    # Playwright は Shadow DOM を自動貫通
    btn = page.locator("#shadow-btn")
    expect(btn).to_be_visible()
    expect(btn).to_have_text("Shadow Button")


def test_shadow_dom_nested(page: Page):
    """ネストされた Shadow DOM 内の要素にアクセス"""
    page.set_content("""
        <div id="outer-host"></div>
        <script>
            const outerHost = document.getElementById('outer-host');
            const outerShadow = outerHost.attachShadow({mode: 'open'});
            outerShadow.innerHTML = '<div id="inner-host"></div>';

            const innerHost = outerShadow.getElementById('inner-host');
            const innerShadow = innerHost.attachShadow({mode: 'open'});
            innerShadow.innerHTML = '<span class="deep-text">深い階層のテキスト</span>';
        </script>
    """)

    # ネストされた Shadow DOM でも自動貫通
    deep = page.locator(".deep-text")
    expect(deep).to_be_visible()
    expect(deep).to_have_text("深い階層のテキスト")


def test_shadow_dom_css_selector(page: Page):
    """CSS セレクタによる Shadow DOM 内の要素アクセス"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <div class="container">
                    <p class="message">Shadow DOM 内のメッセージ</p>
                    <input type="text" class="shadow-input" placeholder="入力してください">
                </div>
            `;
        </script>
    """)

    # クラスセレクタで Shadow DOM 内の要素を検索
    expect(page.locator(".message")).to_have_text("Shadow DOM 内のメッセージ")
    expect(page.locator(".shadow-input")).to_have_attribute("placeholder", "入力してください")


# ============================================================
# Shadow DOM 内のテキスト取得
# ============================================================


def test_shadow_dom_text_content(page: Page):
    """Shadow DOM 内のテキストを取得"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <h2 class="title">Shadow タイトル</h2>
                <p class="description">これは Shadow DOM 内の説明文です。</p>
            `;
        </script>
    """)

    # text_content() でテキストを取得
    title = page.locator(".title")
    assert title.text_content() == "Shadow タイトル"

    description = page.locator(".description")
    assert description.text_content() == "これは Shadow DOM 内の説明文です。"


def test_shadow_dom_inner_text(page: Page):
    """Shadow DOM 内の inner_text を取得"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <ul class="shadow-list">
                    <li>アイテム1</li>
                    <li>アイテム2</li>
                    <li>アイテム3</li>
                </ul>
            `;
        </script>
    """)

    # all_text_contents() で全リスト項目のテキストを取得
    items = page.locator(".shadow-list li")
    expect(items).to_have_count(3)
    assert items.all_text_contents() == ["アイテム1", "アイテム2", "アイテム3"]


def test_shadow_dom_get_by_text(page: Page):
    """get_by_text で Shadow DOM 内の要素を検索"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <p>通常のテキスト</p>
                <p>特別なテキスト</p>
                <p>もう一つのテキスト</p>
            `;
        </script>
    """)

    # get_by_text は Shadow DOM 内も検索対象
    special = page.get_by_text("特別なテキスト")
    expect(special).to_be_visible()
    expect(special).to_have_text("特別なテキスト")


# ============================================================
# Shadow DOM 内のクリック操作
# ============================================================


def test_shadow_dom_click(page: Page):
    """Shadow DOM 内のボタンをクリック"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <button id="shadow-btn">クリック</button>
                <span id="result"></span>
            `;
            shadow.getElementById('shadow-btn').addEventListener('click', () => {
                shadow.getElementById('result').textContent = 'クリックされました';
            });
        </script>
    """)

    # Shadow DOM 内のボタンをクリック
    page.locator("#shadow-btn").click()

    # クリック後の結果を検証
    expect(page.locator("#result")).to_have_text("クリックされました")


def test_shadow_dom_checkbox_toggle(page: Page):
    """Shadow DOM 内のチェックボックスを操作"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <label>
                    <input type="checkbox" id="shadow-cb"> 同意する
                </label>
                <p id="status">未チェック</p>
            `;
            shadow.getElementById('shadow-cb').addEventListener('change', (e) => {
                shadow.getElementById('status').textContent =
                    e.target.checked ? 'チェック済み' : '未チェック';
            });
        </script>
    """)

    cb = page.locator("#shadow-cb")

    # 初期状態はチェックなし
    expect(cb).not_to_be_checked()
    expect(page.locator("#status")).to_have_text("未チェック")

    # チェックボックスをクリック
    cb.check()
    expect(cb).to_be_checked()
    expect(page.locator("#status")).to_have_text("チェック済み")

    # チェックを外す
    cb.uncheck()
    expect(cb).not_to_be_checked()
    expect(page.locator("#status")).to_have_text("未チェック")


def test_shadow_dom_input(page: Page):
    """Shadow DOM 内の入力フィールドに値を入力"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <input type="text" id="shadow-input" placeholder="名前を入力">
                <p id="greeting"></p>
            `;
            shadow.getElementById('shadow-input').addEventListener('input', (e) => {
                shadow.getElementById('greeting').textContent = 'こんにちは、' + e.target.value + 'さん';
            });
        </script>
    """)

    # Shadow DOM 内のフィールドに入力
    page.locator("#shadow-input").fill("太郎")
    expect(page.locator("#shadow-input")).to_have_value("太郎")
    expect(page.locator("#greeting")).to_have_text("こんにちは、太郎さん")


# ============================================================
# get_by_role による Shadow DOM 内の要素操作
# ============================================================


def test_shadow_dom_get_by_role_button(page: Page):
    """get_by_role で Shadow DOM 内のボタンを操作"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <button>送信</button>
                <button>キャンセル</button>
                <p id="result"></p>
            `;
            const buttons = shadow.querySelectorAll('button');
            buttons[0].addEventListener('click', () => {
                shadow.getElementById('result').textContent = '送信されました';
            });
            buttons[1].addEventListener('click', () => {
                shadow.getElementById('result').textContent = 'キャンセルされました';
            });
        </script>
    """)

    # get_by_role でボタンを特定してクリック
    page.get_by_role("button", name="送信").click()
    expect(page.locator("#result")).to_have_text("送信されました")

    page.get_by_role("button", name="キャンセル").click()
    expect(page.locator("#result")).to_have_text("キャンセルされました")


def test_shadow_dom_get_by_role_textbox(page: Page):
    """get_by_role で Shadow DOM 内のテキストボックスを操作"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <label for="username">ユーザー名</label>
                <input type="text" id="username">
                <label for="email">メールアドレス</label>
                <input type="email" id="email">
            `;
        </script>
    """)

    # get_by_role + name でラベル関連付けされた入力欄を操作
    page.get_by_role("textbox", name="ユーザー名").fill("testuser")
    page.get_by_role("textbox", name="メールアドレス").fill("test@example.com")

    expect(page.locator("#username")).to_have_value("testuser")
    expect(page.locator("#email")).to_have_value("test@example.com")


def test_shadow_dom_get_by_role_heading(page: Page):
    """get_by_role で Shadow DOM 内の見出しを検証"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <h1>メインタイトル</h1>
                <h2>サブタイトル</h2>
                <p>本文テキスト</p>
            `;
        </script>
    """)

    # get_by_role で見出しレベルを指定して検証
    expect(page.get_by_role("heading", name="メインタイトル")).to_be_visible()
    expect(page.get_by_role("heading", name="サブタイトル")).to_be_visible()

    # heading ロール全体の数を検証
    expect(page.get_by_role("heading")).to_have_count(2)


def test_shadow_dom_get_by_role_link(page: Page):
    """get_by_role で Shadow DOM 内のリンクを操作"""
    page.set_content("""
        <div id="host"></div>
        <script>
            const host = document.getElementById('host');
            const shadow = host.attachShadow({mode: 'open'});
            shadow.innerHTML = `
                <nav>
                    <a href="#home">ホーム</a>
                    <a href="#about">概要</a>
                    <a href="#contact">お問い合わせ</a>
                </nav>
            `;
        </script>
    """)

    # get_by_role でリンクを検証
    expect(page.get_by_role("link", name="ホーム")).to_have_attribute("href", "#home")
    expect(page.get_by_role("link", name="概要")).to_have_attribute("href", "#about")
    expect(page.get_by_role("link", name="お問い合わせ")).to_have_attribute("href", "#contact")

    # ナビゲーション内のリンク数を検証
    expect(page.get_by_role("link")).to_have_count(3)
