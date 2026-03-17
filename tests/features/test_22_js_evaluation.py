"""
test_22_js_evaluation.py - JavaScript 実行・評価のサンプル

ブラウザコンテキスト内で JavaScript を実行し、
値の取得、関数の公開、イベントの監視を行う方法を示す。
"""

import pytest
from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# 1. JavaScript 式の評価 (page.evaluate) - 値の取得
# ---------------------------------------------------------------------------
def test_evaluate_basic(page):
    """JavaScript 式の評価 - 値の取得"""
    page.set_content("<h1>Hello</h1>")

    # querySelector でテキストを取得
    title = page.evaluate("document.querySelector('h1').textContent")
    assert title == "Hello"


def test_evaluate_expression(page):
    """JavaScript の式を評価して値を返す"""
    # 数値の計算
    result = page.evaluate("1 + 2 * 3")
    assert result == 7

    # 文字列操作
    upper = page.evaluate("'hello world'.toUpperCase()")
    assert upper == "HELLO WORLD"

    # 現在のURL取得
    page.goto("https://example.com")
    url = page.evaluate("location.href")
    assert "example.com" in url


# ---------------------------------------------------------------------------
# 2. 引数付き evaluate
# ---------------------------------------------------------------------------
def test_evaluate_with_args(page):
    """引数付き evaluate"""
    # 複数引数を配列で渡す
    result = page.evaluate("([a, b]) => a + b", [3, 4])
    assert result == 7


def test_evaluate_with_single_arg(page):
    """単一引数の evaluate"""
    # 単一引数をそのまま渡す
    result = page.evaluate("x => x * 2", 5)
    assert result == 10


def test_evaluate_with_dict_arg(page):
    """辞書を引数として渡す"""
    result = page.evaluate(
        "({name, age}) => `${name} is ${age} years old`",
        {"name": "Taro", "age": 25},
    )
    assert result == "Taro is 25 years old"


def test_evaluate_with_dom_arg(page):
    """DOM 要素に対して引数を使って評価する"""
    page.set_content('<input id="target" value="hello" />')

    # Locator で要素を取得し、evaluate で属性を取得
    value = page.evaluate(
        "selector => document.querySelector(selector).value",
        "#target",
    )
    assert value == "hello"


# ---------------------------------------------------------------------------
# 3. evaluate_handle - JSHandle の取得
# ---------------------------------------------------------------------------
def test_evaluate_handle(page):
    """evaluate_handle で JSHandle を取得する"""
    page.set_content("<ul><li>A</li><li>B</li><li>C</li></ul>")

    # JSHandle として取得（ブラウザ内オブジェクトへの参照）
    handle = page.evaluate_handle("document.querySelectorAll('li')")

    # JSHandle のプロパティを取得
    length = handle.evaluate("nodes => nodes.length")
    assert length == 3

    # 不要になったら破棄
    handle.dispose()


def test_evaluate_handle_window(page):
    """window オブジェクトの JSHandle を取得する"""
    # window オブジェクトへの参照を取得
    window_handle = page.evaluate_handle("window")

    # window のプロパティにアクセス
    inner_width = window_handle.evaluate("w => w.innerWidth")
    assert isinstance(inner_width, (int, float))
    assert inner_width > 0

    window_handle.dispose()


# ---------------------------------------------------------------------------
# 4. Locator 上の evaluate (locator.evaluate)
# ---------------------------------------------------------------------------
def test_locator_evaluate(page):
    """Locator 上で JavaScript を評価する"""
    page.set_content('<div id="box" style="width: 200px; height: 100px;">Content</div>')

    locator = page.locator("#box")

    # Locator が指す要素に対して evaluate
    tag_name = locator.evaluate("el => el.tagName")
    assert tag_name == "DIV"

    # スタイル情報を取得
    width = locator.evaluate("el => getComputedStyle(el).width")
    assert width == "200px"


def test_locator_evaluate_with_arg(page):
    """Locator 上で引数付き evaluate を実行する"""
    page.set_content('<div data-info="secret">Hello</div>')

    locator = page.locator("div[data-info]")

    # 第2引数で追加の値を渡せる
    result = locator.evaluate(
        "(el, suffix) => el.textContent + suffix",
        " World",
    )
    assert result == "Hello World"


# ---------------------------------------------------------------------------
# 5. ページへの関数公開 (page.expose_function)
# ---------------------------------------------------------------------------
def test_expose_function(page):
    """Python 関数をブラウザ側に公開する"""

    # Python 側の関数を定義
    def compute_hash(text: str) -> int:
        return hash(text) % 10000

    # ブラウザ側に公開
    page.expose_function("computeHash", compute_hash)

    page.set_content("<div>Test</div>")

    # ブラウザの JavaScript から公開した関数を呼び出す
    result = page.evaluate("() => computeHash('hello')")
    expected = hash("hello") % 10000
    assert result == expected


def test_expose_function_with_button(page):
    """公開した関数をボタンクリックから呼び出す"""
    results = []

    def log_message(msg: str) -> str:
        results.append(msg)
        return f"logged: {msg}"

    page.expose_function("logMessage", log_message)

    page.set_content("""
        <button onclick="logMessage('clicked').then(r => document.title = r)">
            Click
        </button>
    """)

    page.click("button")
    # expose_function の戻り値が title に反映されるのを待つ
    page.wait_for_function("document.title === 'logged: clicked'")

    assert results == ["clicked"]
    assert page.title() == "logged: clicked"


# ---------------------------------------------------------------------------
# 6. コンソールメッセージ監視 (page.on("console"))
# ---------------------------------------------------------------------------
def test_console_message(page):
    """console.log メッセージを監視する"""
    messages = []

    # コンソールイベントをリスン
    page.on("console", lambda msg: messages.append(msg.text))

    page.evaluate("console.log('Hello from JS')")
    page.evaluate("console.warn('Warning!')")
    page.evaluate("console.error('Error occurred')")

    assert "Hello from JS" in messages
    assert "Warning!" in messages
    assert "Error occurred" in messages


def test_console_message_type(page):
    """コンソールメッセージの種類を区別する"""
    log_entries = []

    def on_console(msg):
        log_entries.append({"type": msg.type, "text": msg.text})

    page.on("console", on_console)

    page.evaluate("console.log('info message')")
    page.evaluate("console.warn('warn message')")
    page.evaluate("console.error('error message')")

    types = [e["type"] for e in log_entries]
    assert "log" in types
    assert "warning" in types
    assert "error" in types


# ---------------------------------------------------------------------------
# 7. ページエラー監視 (page.on("pageerror"))
# ---------------------------------------------------------------------------
def test_page_error(page):
    """ページ内の未捕捉エラーを監視する"""
    errors = []

    page.on("pageerror", lambda err: errors.append(str(err)))

    # 意図的にエラーを発生させる
    page.set_content("""
        <script>
            throw new Error("Intentional error for testing");
        </script>
    """)

    assert len(errors) == 1
    assert "Intentional error for testing" in errors[0]


def test_page_error_reference(page):
    """ReferenceError を検出する"""
    errors = []

    page.on("pageerror", lambda err: errors.append(str(err)))

    page.set_content("""
        <script>
            // 存在しない変数を参照してエラーを発生させる
            undefinedVariable.doSomething();
        </script>
    """)

    assert len(errors) == 1
    assert "undefinedVariable" in errors[0]


# ---------------------------------------------------------------------------
# 8. 初期化スクリプト (context.add_init_script)
# ---------------------------------------------------------------------------
def test_add_init_script(context):
    """初期化スクリプトで全ページにグローバル変数を設定する"""
    # すべてのページで実行される初期化スクリプトを追加
    context.add_init_script("window.__CUSTOM_FLAG__ = true")

    page = context.new_page()
    page.goto("https://example.com")

    flag = page.evaluate("window.__CUSTOM_FLAG__")
    assert flag is True

    page.close()


def test_add_init_script_function(context):
    """初期化スクリプトでユーティリティ関数を注入する"""
    context.add_init_script("""
        window.utils = {
            formatDate: (ts) => new Date(ts).toISOString().split('T')[0],
            capitalize: (s) => s.charAt(0).toUpperCase() + s.slice(1),
        };
    """)

    page = context.new_page()
    page.set_content("<div>test</div>")

    # 注入した関数を使用
    capitalized = page.evaluate("window.utils.capitalize('hello')")
    assert capitalized == "Hello"

    # 日付フォーマット関数のテスト (UTC)
    formatted = page.evaluate("window.utils.formatDate(0)")
    assert formatted == "1970-01-01"

    page.close()


def test_add_init_script_persists_across_navigations(context):
    """初期化スクリプトはナビゲーション後も有効"""
    context.add_init_script("window.__INIT_COUNT__ = (window.__INIT_COUNT__ || 0) + 1")

    page = context.new_page()

    # 最初のページ
    page.goto("https://example.com")
    count1 = page.evaluate("window.__INIT_COUNT__")
    assert count1 == 1

    # 別のページに遷移しても初期化スクリプトが再実行される
    page.goto("https://example.com/")
    count2 = page.evaluate("window.__INIT_COUNT__")
    assert count2 == 1  # ナビゲーション毎にリセットされて再実行

    page.close()


# ---------------------------------------------------------------------------
# 9. 複雑なオブジェクトの評価
# ---------------------------------------------------------------------------
def test_evaluate_complex_object(page):
    """複雑なオブジェクトを返す evaluate"""
    result = page.evaluate("""() => {
        return {
            name: "テスト",
            values: [1, 2, 3],
            nested: {
                flag: true,
                count: 42
            }
        };
    }""")

    assert result["name"] == "テスト"
    assert result["values"] == [1, 2, 3]
    assert result["nested"]["flag"] is True
    assert result["nested"]["count"] == 42


def test_evaluate_array_of_objects(page):
    """オブジェクトの配列を返す evaluate"""
    page.set_content("""
        <ul>
            <li data-id="1">Apple</li>
            <li data-id="2">Banana</li>
            <li data-id="3">Cherry</li>
        </ul>
    """)

    items = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('li')).map(li => ({
            id: li.dataset.id,
            text: li.textContent
        }));
    }""")

    assert len(items) == 3
    assert items[0] == {"id": "1", "text": "Apple"}
    assert items[1] == {"id": "2", "text": "Banana"}
    assert items[2] == {"id": "3", "text": "Cherry"}


def test_evaluate_date_and_special_types(page):
    """Date やその他の特殊な型の評価"""
    # Date は文字列として返る（UTC で生成してタイムゾーンの影響を回避）
    date_str = page.evaluate("new Date(Date.UTC(2024, 0, 15)).toISOString()")
    assert "2024-01-15" in date_str

    # Map/Set はシリアライズされない → オブジェクトに変換して返す
    map_result = page.evaluate("""() => {
        const m = new Map([["a", 1], ["b", 2]]);
        return Object.fromEntries(m);
    }""")
    assert map_result == {"a": 1, "b": 2}

    # undefined は None として返る
    undef = page.evaluate("undefined")
    assert undef is None

    # null も None として返る
    null_val = page.evaluate("null")
    assert null_val is None


# ---------------------------------------------------------------------------
# 10. evaluate_all - 全マッチ要素への評価
# ---------------------------------------------------------------------------
def test_evaluate_all(page):
    """Locator にマッチする全要素に対して evaluate する"""
    page.set_content("""
        <ul>
            <li class="item">First</li>
            <li class="item">Second</li>
            <li class="item">Third</li>
        </ul>
    """)

    # 全マッチ要素のテキストを配列で取得
    texts = page.locator("li.item").evaluate_all(
        "elements => elements.map(el => el.textContent)"
    )

    assert texts == ["First", "Second", "Third"]


def test_evaluate_all_attributes(page):
    """全マッチ要素から属性を一括取得する"""
    page.set_content("""
        <a href="/page1" class="link">Page 1</a>
        <a href="/page2" class="link">Page 2</a>
        <a href="/page3" class="link">Page 3</a>
    """)

    # 全リンクの href を取得
    hrefs = page.locator("a.link").evaluate_all(
        "elements => elements.map(el => el.getAttribute('href'))"
    )

    assert hrefs == ["/page1", "/page2", "/page3"]


def test_evaluate_all_computed_values(page):
    """全マッチ要素から計算済みの値を取得する"""
    page.set_content("""
        <div class="box" style="width: 100px">A</div>
        <div class="box" style="width: 200px">B</div>
        <div class="box" style="width: 300px">C</div>
    """)

    # 各要素の幅を数値として取得
    widths = page.locator("div.box").evaluate_all(
        "elements => elements.map(el => parseInt(getComputedStyle(el).width))"
    )

    assert widths == [100, 200, 300]
