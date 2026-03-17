"""
test_04_locators.py - ロケーター戦略のサンプル

Playwright が提供する各種ロケーター戦略を網羅的に示す。

■ ロケーターの優先順位（推奨順）:
  1. get_by_role     - ARIA ロールによる検索（最も推奨・アクセシビリティに準拠）
  2. get_by_text     - 表示テキストによる検索
  3. get_by_test_id  - data-testid 属性による検索（テスト専用属性）
  4. CSS セレクタ    - クラス名・属性など構造ベースの検索
  5. XPath           - XML パス式による検索（最終手段）

推奨: ユーザーから見える属性（ロール・テキスト・ラベル）を優先し、
実装詳細に依存するセレクタ（CSS/XPath）は極力避ける。
"""
import re

import pytest
from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# 1. get_by_role - ARIA ロールによる要素検索
# ---------------------------------------------------------------------------
def test_get_by_role_link(page):
    """get_by_role - リンクロールで要素を検索"""
    page.goto("https://www.microsoft.com/ja-jp")
    # ナビゲーション内のリンクを ARIA ロールで取得
    link = page.get_by_role("link", name="Microsoft")
    expect(link.first).to_be_visible()


def test_get_by_role_heading(page):
    """get_by_role - 見出しロールで要素を検索"""
    page.goto("https://www.microsoft.com/ja-jp")
    # ページ内の見出し要素を取得
    headings = page.get_by_role("heading")
    expect(headings.first).to_be_visible()


def test_get_by_role_navigation(page):
    """get_by_role - ナビゲーションロールで要素を検索"""
    page.goto("https://www.microsoft.com/ja-jp")
    # ナビゲーション領域を取得
    nav = page.get_by_role("navigation")
    expect(nav.first).to_be_visible()


def test_get_by_role_button(page):
    """get_by_role - ボタンロールで要素を検索"""
    page.set_content('<button type="button">送信</button>')
    button = page.get_by_role("button", name="送信")
    expect(button).to_be_visible()
    expect(button).to_have_text("送信")


# ---------------------------------------------------------------------------
# 2. get_by_text - テキスト内容による検索
# ---------------------------------------------------------------------------
def test_get_by_text_partial(page):
    """get_by_text - 部分一致でテキスト検索"""
    page.goto("https://www.microsoft.com/ja-jp")
    # 部分一致（デフォルト）でテキストを検索
    element = page.get_by_text("Microsoft")
    expect(element.first).to_be_visible()


def test_get_by_text_exact(page):
    """get_by_text - exact=True で完全一致検索"""
    page.set_content("""
        <p>Playwright テスト</p>
        <p>Playwright テスト入門</p>
    """)
    # exact=True で完全一致のみヒット
    element = page.get_by_text("Playwright テスト", exact=True)
    expect(element).to_have_count(1)


def test_get_by_text_regex(page):
    """get_by_text - 正規表現によるテキスト検索"""
    page.set_content("""
        <span>注文番号: 12345</span>
        <span>注文番号: 67890</span>
    """)
    # 正規表現でパターンマッチ
    elements = page.get_by_text(re.compile(r"注文番号: \d+"))
    expect(elements).to_have_count(2)


# ---------------------------------------------------------------------------
# 3. get_by_label - ラベルテキストによるフォーム要素検索
# ---------------------------------------------------------------------------
def test_get_by_label(page):
    """get_by_label - ラベルテキストによるフォーム要素検索"""
    page.set_content(
        '<label for="email">メールアドレス</label>'
        '<input id="email" type="email">'
    )
    # ラベルテキストで対応する入力欄を取得
    page.get_by_label("メールアドレス").fill("test@example.com")
    expect(page.get_by_label("メールアドレス")).to_have_value("test@example.com")


def test_get_by_label_checkbox(page):
    """get_by_label - チェックボックスをラベルで操作"""
    page.set_content(
        '<label><input type="checkbox" name="agree"> 利用規約に同意する</label>'
    )
    page.get_by_label("利用規約に同意する").check()
    expect(page.get_by_label("利用規約に同意する")).to_be_checked()


# ---------------------------------------------------------------------------
# 4. get_by_placeholder - プレースホルダーテキストによる検索
# ---------------------------------------------------------------------------
def test_get_by_placeholder(page):
    """get_by_placeholder - プレースホルダーテキストで入力欄を検索"""
    page.set_content('<input type="text" placeholder="キーワードを入力">')
    input_field = page.get_by_placeholder("キーワードを入力")
    input_field.fill("Playwright")
    expect(input_field).to_have_value("Playwright")


def test_get_by_placeholder_partial(page):
    """get_by_placeholder - 部分一致でプレースホルダー検索"""
    page.set_content('<input type="search" placeholder="ここに検索語句を入力してください">')
    # 部分一致でもヒットする
    input_field = page.get_by_placeholder("検索語句")
    input_field.fill("テスト")
    expect(input_field).to_have_value("テスト")


# ---------------------------------------------------------------------------
# 5. get_by_alt_text - alt 属性による画像検索
# ---------------------------------------------------------------------------
def test_get_by_alt_text(page):
    """get_by_alt_text - alt 属性テキストで画像を検索"""
    page.set_content(
        '<img src="logo.png" alt="会社ロゴ">'
        '<img src="banner.png" alt="キャンペーンバナー">'
    )
    logo = page.get_by_alt_text("会社ロゴ")
    expect(logo).to_have_attribute("src", "logo.png")


def test_get_by_alt_text_regex(page):
    """get_by_alt_text - 正規表現で alt 属性を検索"""
    page.set_content("""
        <img src="product1.png" alt="商品画像 A">
        <img src="product2.png" alt="商品画像 B">
    """)
    images = page.get_by_alt_text(re.compile(r"商品画像 [A-B]"))
    expect(images).to_have_count(2)


# ---------------------------------------------------------------------------
# 6. get_by_title - title 属性による検索
# ---------------------------------------------------------------------------
def test_get_by_title(page):
    """get_by_title - title 属性テキストで要素を検索"""
    page.set_content(
        '<button title="設定を開く">⚙</button>'
        '<a href="/help" title="ヘルプページへ移動">ヘルプ</a>'
    )
    settings_btn = page.get_by_title("設定を開く")
    expect(settings_btn).to_be_visible()

    help_link = page.get_by_title("ヘルプページへ移動")
    expect(help_link).to_have_text("ヘルプ")


# ---------------------------------------------------------------------------
# 7. get_by_test_id - data-testid 属性による検索
# ---------------------------------------------------------------------------
def test_get_by_test_id(page):
    """get_by_test_id - data-testid 属性で要素を検索"""
    page.set_content("""
        <div data-testid="user-profile">
            <span data-testid="user-name">田中太郎</span>
            <span data-testid="user-email">tanaka@example.com</span>
        </div>
    """)
    # data-testid で特定の要素を取得（テスト専用属性として安定）
    profile = page.get_by_test_id("user-profile")
    expect(profile).to_be_visible()

    name = page.get_by_test_id("user-name")
    expect(name).to_have_text("田中太郎")

    email = page.get_by_test_id("user-email")
    expect(email).to_have_text("tanaka@example.com")


# ---------------------------------------------------------------------------
# 8. locator (CSS セレクタ)
# ---------------------------------------------------------------------------
def test_locator_css_class(page):
    """locator - CSS クラスセレクタで要素を検索"""
    page.set_content("""
        <div class="card primary">
            <h2 class="card-title">タイトル</h2>
            <p class="card-body">本文テキスト</p>
        </div>
    """)
    title = page.locator(".card-title")
    expect(title).to_have_text("タイトル")


def test_locator_css_attribute(page):
    """locator - CSS 属性セレクタで要素を検索"""
    page.set_content('<input type="email" name="user_email" value="">')
    # 属性セレクタで特定の input を取得
    email_input = page.locator('input[name="user_email"]')
    email_input.fill("user@example.com")
    expect(email_input).to_have_value("user@example.com")


def test_locator_css_nth_child(page):
    """locator - CSS :nth-child 擬似クラスで要素を検索"""
    page.set_content("""
        <ul>
            <li>項目1</li>
            <li>項目2</li>
            <li>項目3</li>
        </ul>
    """)
    # CSS の :nth-child で2番目の li を取得
    second_item = page.locator("ul > li:nth-child(2)")
    expect(second_item).to_have_text("項目2")


# ---------------------------------------------------------------------------
# 9. locator (XPath)
# ---------------------------------------------------------------------------
def test_locator_xpath(page):
    """locator - XPath 式で要素を検索"""
    page.set_content("""
        <table>
            <tr><th>名前</th><th>年齢</th></tr>
            <tr><td>田中</td><td>30</td></tr>
            <tr><td>佐藤</td><td>25</td></tr>
        </table>
    """)
    # XPath で2行目の最初のセル（田中）を取得
    cell = page.locator("xpath=//table//tr[2]/td[1]")
    expect(cell).to_have_text("田中")


def test_locator_xpath_contains(page):
    """locator - XPath の contains() でテキスト部分一致検索"""
    page.set_content("""
        <div>
            <span class="status">ステータス: 完了</span>
            <span class="status">ステータス: 処理中</span>
        </div>
    """)
    # XPath contains() でテキスト部分一致
    completed = page.locator("xpath=//span[contains(text(), '完了')]")
    expect(completed).to_have_count(1)
    expect(completed).to_contain_text("完了")


# ---------------------------------------------------------------------------
# 10. filter - 条件フィルタリング
# ---------------------------------------------------------------------------
def test_filter_has_text(page):
    """filter - has_text で特定テキストを含む要素に絞り込み"""
    page.set_content("""
        <ul>
            <li class="product">りんご - ¥100</li>
            <li class="product">バナナ - ¥200</li>
            <li class="product">みかん - ¥150</li>
        </ul>
    """)
    # has_text で「バナナ」を含む li に絞り込み
    banana = page.locator("li.product").filter(has_text="バナナ")
    expect(banana).to_have_count(1)
    expect(banana).to_contain_text("¥200")


def test_filter_has(page):
    """filter - has で特定の子要素を持つ要素に絞り込み"""
    page.set_content("""
        <div class="card"><h3>通常カード</h3><p>説明文</p></div>
        <div class="card"><h3>特別カード</h3><p>説明文</p><span class="badge">NEW</span></div>
        <div class="card"><h3>古いカード</h3><p>説明文</p></div>
    """)
    # has で .badge を持つカードに絞り込み
    card_with_badge = page.locator(".card").filter(has=page.locator(".badge"))
    expect(card_with_badge).to_have_count(1)
    expect(card_with_badge).to_contain_text("特別カード")


def test_filter_chained(page):
    """filter - 複数条件を連鎖して絞り込み"""
    page.set_content("""
        <div class="item" data-category="fruit">りんご - 赤</div>
        <div class="item" data-category="fruit">バナナ - 黄</div>
        <div class="item" data-category="vegetable">トマト - 赤</div>
    """)
    # フルーツカテゴリかつ「赤」を含む要素
    red_fruit = (
        page.locator('.item[data-category="fruit"]')
        .filter(has_text="赤")
    )
    expect(red_fruit).to_have_count(1)
    expect(red_fruit).to_contain_text("りんご")


# ---------------------------------------------------------------------------
# 11. nth / first / last - N番目の要素
# ---------------------------------------------------------------------------
def test_nth_element(page):
    """nth - インデックス指定で N 番目の要素を取得（0始まり）"""
    page.set_content("""
        <ol>
            <li>第1位</li>
            <li>第2位</li>
            <li>第3位</li>
        </ol>
    """)
    items = page.locator("ol > li")
    # nth(0) は最初の要素、nth(1) は2番目
    expect(items.nth(0)).to_have_text("第1位")
    expect(items.nth(1)).to_have_text("第2位")
    expect(items.nth(2)).to_have_text("第3位")


def test_first_last(page):
    """first / last - 最初と最後の要素を取得"""
    page.set_content("""
        <ul>
            <li>最初の項目</li>
            <li>中間の項目</li>
            <li>最後の項目</li>
        </ul>
    """)
    items = page.locator("ul > li")
    expect(items.first).to_have_text("最初の項目")
    expect(items.last).to_have_text("最後の項目")


def test_nth_negative_index(page):
    """nth - 負のインデックスで末尾から要素を取得"""
    page.set_content("""
        <div class="list">
            <span>A</span>
            <span>B</span>
            <span>C</span>
        </div>
    """)
    spans = page.locator(".list > span")
    # nth(-1) は最後の要素
    expect(spans.nth(-1)).to_have_text("C")
    expect(spans.nth(-2)).to_have_text("B")


# ---------------------------------------------------------------------------
# 12. チェーン - ロケーターの連鎖
# ---------------------------------------------------------------------------
def test_locator_chain(page):
    """チェーン - ロケーターを連鎖して子孫要素を絞り込み"""
    page.set_content("""
        <div class="sidebar">
            <a href="/home">ホーム</a>
            <a href="/about">概要</a>
        </div>
        <div class="main">
            <a href="/home">ホーム</a>
            <a href="/contact">お問い合わせ</a>
        </div>
    """)
    # .main 内のリンクだけを取得（連鎖でスコープを限定）
    main_links = page.locator(".main").locator("a")
    expect(main_links).to_have_count(2)
    expect(main_links.first).to_have_text("ホーム")


def test_locator_chain_role(page):
    """チェーン - locator と get_by_role を組み合わせる"""
    page.set_content("""
        <nav aria-label="メインメニュー">
            <button>ホーム</button>
            <button>設定</button>
        </nav>
        <footer>
            <button>トップへ戻る</button>
        </footer>
    """)
    # nav 内のボタンだけを取得
    nav_buttons = page.locator("nav").get_by_role("button")
    expect(nav_buttons).to_have_count(2)

    # さらに名前で絞り込み
    settings = page.locator("nav").get_by_role("button", name="設定")
    expect(settings).to_be_visible()


# ---------------------------------------------------------------------------
# 13. count - 要素数取得
# ---------------------------------------------------------------------------
def test_count(page):
    """count - マッチした要素の数を取得"""
    page.set_content("""
        <ul class="menu">
            <li>項目A</li>
            <li>項目B</li>
            <li>項目C</li>
            <li>項目D</li>
        </ul>
    """)
    items = page.locator(".menu > li")
    # count() で要素数を取得
    assert items.count() == 4


def test_count_on_live_site(page):
    """count - 実サイトで要素数を確認"""
    page.goto("https://www.microsoft.com/ja-jp")
    # ページ内のリンク数を取得（0 より多いことを確認）
    links = page.get_by_role("link")
    assert links.count() > 0


# ---------------------------------------------------------------------------
# 14. all - 全要素取得
# ---------------------------------------------------------------------------
def test_all_elements(page):
    """all - 全マッチ要素をリストとして取得しループ処理"""
    page.set_content("""
        <div class="tags">
            <span class="tag">Python</span>
            <span class="tag">Playwright</span>
            <span class="tag">pytest</span>
        </div>
    """)
    tags = page.locator(".tag")
    # all() でロケーターのリストを取得
    all_tags = tags.all()
    assert len(all_tags) == 3

    # 各要素のテキストを収集
    tag_texts = [tag.text_content() for tag in all_tags]
    assert "Python" in tag_texts
    assert "Playwright" in tag_texts
    assert "pytest" in tag_texts


def test_all_inner_texts(page):
    """all - all_inner_texts() で全要素のテキストを一括取得"""
    page.set_content("""
        <ol>
            <li>手順1: インストール</li>
            <li>手順2: 設定</li>
            <li>手順3: 実行</li>
        </ol>
    """)
    items = page.locator("ol > li")
    texts = items.all_inner_texts()
    assert len(texts) == 3
    assert texts[0] == "手順1: インストール"
    assert texts[2] == "手順3: 実行"
