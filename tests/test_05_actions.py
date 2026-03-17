"""
test_05_actions.py - ユーザーアクション・入力操作のサンプル

テキスト入力、クリック、キーボード・マウス操作など
ブラウザ上でのユーザーインタラクションを網羅する。
"""
import pytest
from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# 1. fill - テキスト入力
# ---------------------------------------------------------------------------
def test_fill(page):
    """fill - テキスト入力"""
    page.set_content('<input id="name" type="text">')
    page.locator("#name").fill("テスト太郎")
    assert page.locator("#name").input_value() == "テスト太郎"


def test_fill_textarea(page):
    """fill - テキストエリアへの入力"""
    page.set_content('<textarea id="memo"></textarea>')
    page.locator("#memo").fill("複数行の\nテキスト入力")
    assert page.locator("#memo").input_value() == "複数行の\nテキスト入力"


def test_fill_replaces_existing_value(page):
    """fill - 既存の値を上書きする"""
    page.set_content('<input id="field" type="text" value="古い値">')
    page.locator("#field").fill("新しい値")
    assert page.locator("#field").input_value() == "新しい値"


# ---------------------------------------------------------------------------
# 2. type / press_sequentially - 一文字ずつ入力
# ---------------------------------------------------------------------------
def test_press_sequentially(page):
    """press_sequentially - 一文字ずつ入力（タイピングアニメーション）"""
    page.set_content('<input id="search" type="text">')
    # delay で入力速度を制御（ミリ秒）
    page.locator("#search").press_sequentially("Hello", delay=50)
    assert page.locator("#search").input_value() == "Hello"


def test_press_sequentially_with_events(page):
    """press_sequentially - 入力中のイベント検知"""
    page.set_content("""
        <input id="input" type="text">
        <div id="log"></div>
        <script>
            const input = document.getElementById('input');
            const log = document.getElementById('log');
            input.addEventListener('keydown', () => {
                log.textContent += 'K';
            });
        </script>
    """)
    page.locator("#input").press_sequentially("abc")
    # 3文字入力 → keydown が3回発火
    assert page.locator("#log").text_content() == "KKK"


# ---------------------------------------------------------------------------
# 3. clear - フィールドクリア
# ---------------------------------------------------------------------------
def test_clear(page):
    """clear - 入力フィールドのクリア"""
    page.set_content('<input id="field" type="text" value="クリアされる値">')
    page.locator("#field").clear()
    assert page.locator("#field").input_value() == ""


def test_clear_textarea(page):
    """clear - テキストエリアのクリア"""
    page.set_content('<textarea id="memo">既存のテキスト</textarea>')
    page.locator("#memo").clear()
    assert page.locator("#memo").input_value() == ""


# ---------------------------------------------------------------------------
# 4. click - シングルクリック
# ---------------------------------------------------------------------------
def test_click(page):
    """click - ボタンのシングルクリック"""
    page.set_content("""
        <button id="btn" onclick="this.textContent='クリック済み'">未クリック</button>
    """)
    page.locator("#btn").click()
    assert page.locator("#btn").text_content() == "クリック済み"


def test_click_link(page):
    """click - リンクのクリック"""
    page.set_content("""
        <a id="link" href="#clicked" onclick="document.getElementById('result').textContent='遷移済み'">リンク</a>
        <div id="result"></div>
    """)
    page.locator("#link").click()
    assert page.locator("#result").text_content() == "遷移済み"


# ---------------------------------------------------------------------------
# 5. dblclick - ダブルクリック
# ---------------------------------------------------------------------------
def test_dblclick(page):
    """dblclick - ダブルクリック"""
    page.set_content("""
        <div id="target" ondblclick="this.textContent='ダブルクリック検知'">ダブルクリックしてください</div>
    """)
    page.locator("#target").dblclick()
    assert page.locator("#target").text_content() == "ダブルクリック検知"


# ---------------------------------------------------------------------------
# 6. click (right) - 右クリック
# ---------------------------------------------------------------------------
def test_right_click(page):
    """click(button='right') - 右クリック（コンテキストメニュー）"""
    page.set_content("""
        <div id="target" oncontextmenu="document.getElementById('result').textContent='右クリック検知'; return false;">
            右クリック対象
        </div>
        <div id="result"></div>
    """)
    page.locator("#target").click(button="right")
    assert page.locator("#result").text_content() == "右クリック検知"


# ---------------------------------------------------------------------------
# 7. click with modifiers - Shift+クリック等
# ---------------------------------------------------------------------------
def test_click_with_shift(page):
    """click(modifiers) - Shift キーを押しながらクリック"""
    page.set_content("""
        <div id="target">対象</div>
        <div id="result"></div>
        <script>
            document.getElementById('target').addEventListener('click', (e) => {
                if (e.shiftKey) {
                    document.getElementById('result').textContent = 'Shift+クリック';
                }
            });
        </script>
    """)
    page.locator("#target").click(modifiers=["Shift"])
    assert page.locator("#result").text_content() == "Shift+クリック"


def test_click_with_control(page):
    """click(modifiers) - Control キーを押しながらクリック"""
    page.set_content("""
        <div id="target">対象</div>
        <div id="result"></div>
        <script>
            document.getElementById('target').addEventListener('click', (e) => {
                if (e.ctrlKey || e.metaKey) {
                    document.getElementById('result').textContent = 'Ctrl+クリック';
                }
            });
        </script>
    """)
    # macOS では Meta キーが Command に対応
    page.locator("#target").click(modifiers=["ControlOrMeta"])
    assert page.locator("#result").text_content() == "Ctrl+クリック"


# ---------------------------------------------------------------------------
# 8. click with position - 座標指定クリック
# ---------------------------------------------------------------------------
def test_click_with_position(page):
    """click(position) - 要素内の特定座標をクリック"""
    page.set_content("""
        <div id="canvas" style="width:200px;height:200px;background:#eee;">
        </div>
        <div id="result"></div>
        <script>
            document.getElementById('canvas').addEventListener('click', (e) => {
                const rect = e.target.getBoundingClientRect();
                const x = Math.round(e.clientX - rect.left);
                const y = Math.round(e.clientY - rect.top);
                document.getElementById('result').textContent = x + ',' + y;
            });
        </script>
    """)
    # 要素の左上からの相対座標 (10, 20) をクリック
    page.locator("#canvas").click(position={"x": 10, "y": 20})
    assert page.locator("#result").text_content() == "10,20"


# ---------------------------------------------------------------------------
# 9. click with force - 強制クリック
# ---------------------------------------------------------------------------
def test_click_with_force(page):
    """click(force=True) - オーバーレイ要素があっても強制クリック"""
    page.set_content("""
        <div style="position:relative;">
            <button id="btn" onclick="this.dataset.clicked='true'">ボタン</button>
            <div style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:10;"></div>
        </div>
    """)
    # 通常クリックではオーバーレイに遮られるが、force=True で強制的にクリック
    page.locator("#btn").click(force=True)
    assert page.locator("#btn").get_attribute("data-clicked") == "true"


# ---------------------------------------------------------------------------
# 10. hover - マウスオーバー
# ---------------------------------------------------------------------------
def test_hover(page):
    """hover - マウスオーバーでツールチップ表示"""
    page.set_content("""
        <div id="target" onmouseenter="document.getElementById('tooltip').style.display='block'">
            ホバー対象
        </div>
        <div id="tooltip" style="display:none;">ツールチップ</div>
    """)
    page.locator("#target").hover()
    expect(page.locator("#tooltip")).to_be_visible()


def test_hover_shows_hidden_element(page):
    """hover - CSS :hover による要素表示"""
    page.set_content("""
        <style>
            #menu { display: none; }
            #parent:hover #menu { display: block; }
        </style>
        <div id="parent">
            <span>メニュー</span>
            <ul id="menu"><li>項目1</li></ul>
        </div>
    """)
    page.locator("#parent").hover()
    expect(page.locator("#menu")).to_be_visible()


# ---------------------------------------------------------------------------
# 11. check / uncheck - チェックボックス
# ---------------------------------------------------------------------------
def test_check(page):
    """check - チェックボックスをオンにする"""
    page.set_content('<input id="agree" type="checkbox">')
    page.locator("#agree").check()
    assert page.locator("#agree").is_checked()


def test_uncheck(page):
    """uncheck - チェックボックスをオフにする"""
    page.set_content('<input id="agree" type="checkbox" checked>')
    page.locator("#agree").uncheck()
    assert not page.locator("#agree").is_checked()


def test_check_radio(page):
    """check - ラジオボタンの選択"""
    page.set_content("""
        <input type="radio" name="color" id="red" value="red">
        <input type="radio" name="color" id="blue" value="blue">
    """)
    page.locator("#blue").check()
    assert page.locator("#blue").is_checked()
    assert not page.locator("#red").is_checked()


# ---------------------------------------------------------------------------
# 12. set_checked - チェック状態の設定
# ---------------------------------------------------------------------------
def test_set_checked_on(page):
    """set_checked(True) - チェック状態をオンに設定"""
    page.set_content('<input id="opt" type="checkbox">')
    page.locator("#opt").set_checked(True)
    assert page.locator("#opt").is_checked()


def test_set_checked_off(page):
    """set_checked(False) - チェック状態をオフに設定"""
    page.set_content('<input id="opt" type="checkbox" checked>')
    page.locator("#opt").set_checked(False)
    assert not page.locator("#opt").is_checked()


def test_set_checked_toggle(page):
    """set_checked - 状態を切り替える"""
    page.set_content('<input id="toggle" type="checkbox">')
    loc = page.locator("#toggle")

    loc.set_checked(True)
    assert loc.is_checked()

    loc.set_checked(False)
    assert not loc.is_checked()


# ---------------------------------------------------------------------------
# 13. select_option - ドロップダウン選択
# ---------------------------------------------------------------------------
def test_select_option_by_value(page):
    """select_option - value 属性で選択"""
    page.set_content("""
        <select id="lang">
            <option value="">選択してください</option>
            <option value="ja">日本語</option>
            <option value="en">英語</option>
        </select>
    """)
    page.locator("#lang").select_option("ja")
    assert page.locator("#lang").input_value() == "ja"


def test_select_option_by_label(page):
    """select_option - 表示テキスト（ラベル）で選択"""
    page.set_content("""
        <select id="lang">
            <option value="ja">日本語</option>
            <option value="en">英語</option>
        </select>
    """)
    page.locator("#lang").select_option(label="英語")
    assert page.locator("#lang").input_value() == "en"


def test_select_option_by_index(page):
    """select_option - インデックスで選択"""
    page.set_content("""
        <select id="lang">
            <option value="ja">日本語</option>
            <option value="en">英語</option>
            <option value="zh">中国語</option>
        </select>
    """)
    # インデックスは 0 始まり
    page.locator("#lang").select_option(index=2)
    assert page.locator("#lang").input_value() == "zh"


def test_select_option_multiple(page):
    """select_option - 複数選択"""
    page.set_content("""
        <select id="fruits" multiple>
            <option value="apple">りんご</option>
            <option value="banana">バナナ</option>
            <option value="grape">ぶどう</option>
        </select>
    """)
    page.locator("#fruits").select_option(["apple", "grape"])
    # 複数選択の場合、選択された値のリストを検証
    selected = page.locator("#fruits option:checked")
    assert selected.count() == 2


# ---------------------------------------------------------------------------
# 14. drag_to - ドラッグ＆ドロップ
# ---------------------------------------------------------------------------
def test_drag_to(page):
    """drag_to - 要素を別の要素へドラッグ＆ドロップ"""
    page.set_content("""
        <style>
            .box { width: 100px; height: 100px; border: 1px solid #333; }
            #source { background: #aaf; }
            #target { background: #faa; }
        </style>
        <div id="source" draggable="true" class="box">ドラッグ元</div>
        <div id="target" class="box">ドロップ先</div>
        <div id="result"></div>
        <script>
            const target = document.getElementById('target');
            target.addEventListener('dragover', (e) => e.preventDefault());
            target.addEventListener('drop', (e) => {
                e.preventDefault();
                document.getElementById('result').textContent = 'ドロップ完了';
            });
        </script>
    """)
    source = page.locator("#source")
    target = page.locator("#target")
    source.drag_to(target)
    assert page.locator("#result").text_content() == "ドロップ完了"


# ---------------------------------------------------------------------------
# 15. keyboard.press - キー操作
# ---------------------------------------------------------------------------
def test_keyboard_press_enter(page):
    """keyboard.press - Enter キーでフォーム送信"""
    page.set_content("""
        <form onsubmit="document.getElementById('result').textContent='送信済み'; return false;">
            <input id="input" type="text">
            <div id="result"></div>
        </form>
    """)
    page.locator("#input").click()
    page.keyboard.press("Enter")
    assert page.locator("#result").text_content() == "送信済み"


def test_keyboard_press_tab(page):
    """keyboard.press - Tab キーでフォーカス移動"""
    page.set_content("""
        <input id="first" type="text">
        <input id="second" type="text">
    """)
    page.locator("#first").click()
    page.keyboard.press("Tab")
    # Tab で次の入力欄にフォーカスが移動する
    focused_id = page.evaluate("document.activeElement.id")
    assert focused_id == "second"


def test_keyboard_press_escape(page):
    """keyboard.press - Escape キーでダイアログを閉じる"""
    page.set_content("""
        <dialog id="dialog" open>
            <p>ダイアログ</p>
        </dialog>
    """)
    page.keyboard.press("Escape")
    expect(page.locator("#dialog")).not_to_be_visible()


def test_keyboard_press_arrow_keys(page):
    """keyboard.press - 矢印キーでスライダー操作"""
    page.set_content('<input id="slider" type="range" min="0" max="100" value="50">')
    page.locator("#slider").click()
    page.keyboard.press("ArrowRight")
    # 矢印キーでスライダーの値が変わる
    value = int(page.locator("#slider").input_value())
    assert value == 51


# ---------------------------------------------------------------------------
# 16. keyboard.type - キーボード入力
# ---------------------------------------------------------------------------
def test_keyboard_type(page):
    """keyboard.type - キーボードからのテキスト入力"""
    page.set_content('<input id="field" type="text">')
    page.locator("#field").click()
    page.keyboard.type("Playwright テスト")
    assert page.locator("#field").input_value() == "Playwright テスト"


# ---------------------------------------------------------------------------
# 17. keyboard shortcuts - ショートカットキー
# ---------------------------------------------------------------------------
def test_keyboard_select_all(page):
    """keyboard shortcut - Control+A で全選択"""
    page.set_content('<input id="field" type="text" value="全選択テスト">')
    page.locator("#field").click()
    # 全選択してから新しいテキストを入力
    page.keyboard.press("ControlOrMeta+a")
    page.keyboard.type("上書き")
    assert page.locator("#field").input_value() == "上書き"


def test_keyboard_copy_paste(page):
    """keyboard shortcut - コピー＆ペースト"""
    page.set_content("""
        <input id="source" type="text" value="コピー元テキスト">
        <input id="dest" type="text">
    """)
    # ソースフィールドで全選択 → コピー
    page.locator("#source").click()
    page.keyboard.press("ControlOrMeta+a")
    page.keyboard.press("ControlOrMeta+c")

    # ペースト先にフォーカスしてペースト
    page.locator("#dest").click()
    page.keyboard.press("ControlOrMeta+v")
    assert page.locator("#dest").input_value() == "コピー元テキスト"


def test_keyboard_undo(page):
    """keyboard shortcut - Control+Z で元に戻す"""
    page.set_content('<input id="field" type="text">')
    page.locator("#field").click()
    page.keyboard.type("テスト入力")
    # Undo で入力を取り消し
    page.keyboard.press("ControlOrMeta+z")
    value = page.locator("#field").input_value()
    assert value != "テスト入力"


# ---------------------------------------------------------------------------
# 18. mouse.move / mouse.click - マウス座標操作
# ---------------------------------------------------------------------------
def test_mouse_click_coordinates(page):
    """mouse.click - 座標指定でマウスクリック"""
    page.set_content("""
        <div id="area" style="width:300px;height:300px;background:#eee;"></div>
        <div id="result"></div>
        <script>
            document.getElementById('area').addEventListener('click', (e) => {
                document.getElementById('result').textContent = 'clicked';
            });
        </script>
    """)
    # 要素のバウンディングボックスを取得して中心をクリック
    box = page.locator("#area").bounding_box()
    page.mouse.click(box["x"] + 150, box["y"] + 150)
    assert page.locator("#result").text_content() == "clicked"


def test_mouse_move(page):
    """mouse.move - マウスカーソルの移動"""
    page.set_content("""
        <div id="tracker" style="width:300px;height:300px;background:#eee;"></div>
        <div id="result"></div>
        <script>
            document.getElementById('tracker').addEventListener('mousemove', (e) => {
                document.getElementById('result').textContent = 'moved';
            });
        </script>
    """)
    box = page.locator("#tracker").bounding_box()
    page.mouse.move(box["x"] + 10, box["y"] + 10)
    page.mouse.move(box["x"] + 100, box["y"] + 100)
    assert page.locator("#result").text_content() == "moved"


def test_mouse_down_up(page):
    """mouse.down / mouse.up - マウスボタンの押下・解放"""
    page.set_content("""
        <div id="target" style="width:100px;height:100px;background:#ccc;"></div>
        <div id="log"></div>
        <script>
            const target = document.getElementById('target');
            const log = document.getElementById('log');
            target.addEventListener('mousedown', () => log.textContent += 'down,');
            target.addEventListener('mouseup', () => log.textContent += 'up');
        </script>
    """)
    box = page.locator("#target").bounding_box()
    center_x = box["x"] + box["width"] / 2
    center_y = box["y"] + box["height"] / 2
    page.mouse.move(center_x, center_y)
    page.mouse.down()
    page.mouse.up()
    assert page.locator("#log").text_content() == "down,up"


# ---------------------------------------------------------------------------
# 19. mouse.wheel - マウスホイール
# ---------------------------------------------------------------------------
def test_mouse_wheel(page):
    """mouse.wheel - マウスホイールによるスクロール"""
    page.set_content("""
        <div id="container" style="width:200px;height:100px;overflow:auto;">
            <div style="height:500px;background:linear-gradient(#fff,#000);">
                長いコンテンツ
            </div>
        </div>
    """)
    # コンテナ上にマウスを移動してホイール操作
    box = page.locator("#container").bounding_box()
    page.mouse.move(box["x"] + 100, box["y"] + 50)
    page.mouse.wheel(0, 200)

    # スクロール位置が変わったことを確認
    scroll_top = page.evaluate(
        "document.getElementById('container').scrollTop"
    )
    assert scroll_top > 0


# ---------------------------------------------------------------------------
# 20. focus - 要素フォーカス
# ---------------------------------------------------------------------------
def test_focus(page):
    """focus - 要素にフォーカスを当てる"""
    page.set_content("""
        <input id="first" type="text">
        <input id="second" type="text">
    """)
    page.locator("#second").focus()
    focused_id = page.evaluate("document.activeElement.id")
    assert focused_id == "second"


def test_focus_triggers_event(page):
    """focus - フォーカスイベントの検知"""
    page.set_content("""
        <input id="field" type="text">
        <div id="result"></div>
        <script>
            document.getElementById('field').addEventListener('focus', () => {
                document.getElementById('result').textContent = 'フォーカス検知';
            });
        </script>
    """)
    page.locator("#field").focus()
    assert page.locator("#result").text_content() == "フォーカス検知"


# ---------------------------------------------------------------------------
# 21. scroll_into_view_if_needed - スクロール
# ---------------------------------------------------------------------------
def test_scroll_into_view_if_needed(page):
    """scroll_into_view_if_needed - 画面外の要素までスクロール"""
    page.set_content("""
        <div style="height:2000px;">上部のスペーサー</div>
        <div id="bottom" style="height:50px;background:#faa;">最下部の要素</div>
    """)
    # 要素が画面外にあるので、スクロールして表示
    page.locator("#bottom").scroll_into_view_if_needed()
    expect(page.locator("#bottom")).to_be_in_viewport()


def test_scroll_into_view_and_interact(page):
    """scroll_into_view_if_needed - スクロール後にクリック"""
    page.set_content("""
        <div style="height:2000px;">上部のスペーサー</div>
        <button id="hidden-btn" onclick="this.textContent='発見！'">
            隠れたボタン
        </button>
    """)
    btn = page.locator("#hidden-btn")
    btn.scroll_into_view_if_needed()
    btn.click()
    assert btn.text_content().strip() == "発見！"
