"""
test_21_accessibility.py - アクセシビリティテストのサンプル

ARIA ロール、アクセシブル名・説明の検証、アクセシビリティスナップショットなど
Web アクセシビリティに関するテスト手法を示す。
"""

import re

from playwright.sync_api import Page, expect


# ============================================================
# 1. アクセシビリティスナップショットの取得
#    (Accessibility Snapshot)
# ============================================================


def test_accessibility_snapshot(page: Page):
    """アクセシビリティスナップショットの取得"""
    page.set_content('''
        <nav aria-label="メインナビゲーション">
            <a href="/home">ホーム</a>
            <a href="/about">概要</a>
        </nav>
        <main>
            <h1>メインコンテンツ</h1>
            <button aria-describedby="help">送信</button>
            <span id="help">フォームを送信します</span>
        </main>
    ''')
    # ページ全体のアクセシビリティツリーを取得
    snapshot = page.accessibility.snapshot()
    assert snapshot is not None
    assert snapshot["role"] == "WebArea"


def test_accessibility_snapshot_children(page: Page):
    """スナップショットの子ノードを確認"""
    page.set_content('''
        <nav aria-label="サイトナビ">
            <a href="/top">トップ</a>
            <a href="/info">情報</a>
        </nav>
        <main>
            <h1>見出し</h1>
            <p>本文テキスト</p>
        </main>
    ''')
    snapshot = page.accessibility.snapshot()
    assert snapshot is not None
    # ルートノードに子ノードが存在する
    children = snapshot.get("children", [])
    assert len(children) > 0
    # ナビゲーションロールの子ノードが含まれる
    roles = [child["role"] for child in children]
    assert "navigation" in roles


def test_accessibility_snapshot_specific_root(page: Page):
    """特定の要素をルートにしたスナップショット"""
    page.set_content('''
        <form aria-label="ログインフォーム">
            <label for="user">ユーザー名</label>
            <input id="user" type="text" />
            <label for="pass">パスワード</label>
            <input id="pass" type="password" />
            <button type="submit">ログイン</button>
        </form>
    ''')
    # フォーム要素をルートにスナップショットを取得
    form = page.locator("form")
    snapshot = page.accessibility.snapshot(root=form.element_handle())
    assert snapshot is not None
    assert snapshot["role"] == "form"
    assert snapshot["name"] == "ログインフォーム"


# ============================================================
# 2. ARIA ロールベースの要素検証
#    (get_by_role)
# ============================================================


def test_get_by_role_button(page: Page):
    """ボタンロールで要素を検索・検証"""
    page.set_content('''
        <button type="button">保存</button>
        <button type="submit">送信</button>
        <input type="button" value="キャンセル" />
    ''')
    # name オプションで特定のボタンを取得
    save_btn = page.get_by_role("button", name="保存")
    expect(save_btn).to_be_visible()
    # input[type=button] もボタンロールとして認識される
    cancel_btn = page.get_by_role("button", name="キャンセル")
    expect(cancel_btn).to_be_visible()


def test_get_by_role_navigation_and_links(page: Page):
    """ナビゲーション内のリンクをロールで検証"""
    page.set_content('''
        <nav aria-label="パンくずリスト">
            <a href="/home">ホーム</a>
            <a href="/products">製品一覧</a>
            <a href="/products/1" aria-current="page">製品詳細</a>
        </nav>
    ''')
    # ナビゲーションランドマークを取得
    nav = page.get_by_role("navigation", name="パンくずリスト")
    expect(nav).to_be_visible()
    # ナビゲーション内のリンク数を確認
    links = nav.get_by_role("link")
    expect(links).to_have_count(3)
    # aria-current 属性で現在ページのリンクを特定
    current_link = nav.locator('[aria-current="page"]')
    expect(current_link).to_have_text("製品詳細")


def test_get_by_role_form_elements(page: Page):
    """フォーム要素をロールで検証"""
    page.set_content('''
        <form>
            <label for="email">メールアドレス</label>
            <input id="email" type="email" required />
            <label for="agree">利用規約に同意する</label>
            <input id="agree" type="checkbox" />
            <select aria-label="都道府県">
                <option value="">選択してください</option>
                <option value="tokyo">東京都</option>
                <option value="osaka">大阪府</option>
            </select>
        </form>
    ''')
    # テキストボックスロール（email 入力）
    email_input = page.get_by_role("textbox", name="メールアドレス")
    expect(email_input).to_be_visible()
    # チェックボックスロール
    checkbox = page.get_by_role("checkbox", name="利用規約に同意する")
    expect(checkbox).not_to_be_checked()
    # コンボボックスロール（select 要素）
    select = page.get_by_role("combobox", name="都道府県")
    expect(select).to_be_visible()


def test_get_by_role_heading_level(page: Page):
    """見出しロールのレベル指定で検証"""
    page.set_content('''
        <h1>メインタイトル</h1>
        <h2>セクション1</h2>
        <p>セクション1の内容</p>
        <h2>セクション2</h2>
        <p>セクション2の内容</p>
        <h3>サブセクション</h3>
    ''')
    # level オプションで見出しレベルを指定
    h1 = page.get_by_role("heading", level=1)
    expect(h1).to_have_text("メインタイトル")
    # h2 は 2 つ存在する
    h2_list = page.get_by_role("heading", level=2)
    expect(h2_list).to_have_count(2)
    # h3 は 1 つ
    h3 = page.get_by_role("heading", level=3)
    expect(h3).to_have_text("サブセクション")


def test_get_by_role_list(page: Page):
    """リストロールで要素を検証"""
    page.set_content('''
        <ul aria-label="タスク一覧">
            <li>タスクA</li>
            <li>タスクB</li>
            <li>タスクC</li>
        </ul>
    ''')
    task_list = page.get_by_role("list", name="タスク一覧")
    expect(task_list).to_be_visible()
    # リストアイテムの件数を検証
    items = task_list.get_by_role("listitem")
    expect(items).to_have_count(3)


# ============================================================
# 3. アクセシブル名の検証
#    (to_have_accessible_name)
# ============================================================


def test_accessible_name_by_label(page: Page):
    """label 要素から算出されるアクセシブル名の検証"""
    page.set_content('''
        <label for="username">ユーザー名</label>
        <input id="username" type="text" />
    ''')
    text_input = page.locator("#username")
    # label の紐付けによりアクセシブル名が設定される
    expect(text_input).to_have_accessible_name("ユーザー名")


def test_accessible_name_by_aria_label(page: Page):
    """aria-label によるアクセシブル名の検証"""
    page.set_content('''
        <button aria-label="メニューを開く">
            <svg viewBox="0 0 24 24"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>
        </button>
    ''')
    menu_btn = page.get_by_role("button")
    # aria-label がアクセシブル名として使用される
    expect(menu_btn).to_have_accessible_name("メニューを開く")


def test_accessible_name_by_aria_labelledby(page: Page):
    """aria-labelledby によるアクセシブル名の検証"""
    page.set_content('''
        <h2 id="section-title">検索条件</h2>
        <form aria-labelledby="section-title">
            <input type="search" aria-label="キーワード" />
            <button type="submit">検索</button>
        </form>
    ''')
    form = page.locator("form")
    # aria-labelledby で参照された要素のテキストがアクセシブル名になる
    expect(form).to_have_accessible_name("検索条件")


def test_accessible_name_with_regex(page: Page):
    """正規表現によるアクセシブル名の部分一致検証"""
    page.set_content('''
        <button aria-label="3件の通知を確認">通知</button>
    ''')
    button = page.get_by_role("button")
    # 正規表現で部分一致を検証
    expect(button).to_have_accessible_name(re.compile(r"\d+件の通知"))


def test_accessible_name_image(page: Page):
    """画像の alt テキストによるアクセシブル名の検証"""
    page.set_content('''
        <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
             alt="会社ロゴ" />
    ''')
    img = page.get_by_role("img")
    # alt 属性がアクセシブル名になる
    expect(img).to_have_accessible_name("会社ロゴ")


# ============================================================
# 4. アクセシブル説明の検証
#    (to_have_accessible_description)
# ============================================================


def test_accessible_description_by_describedby(page: Page):
    """aria-describedby によるアクセシブル説明の検証"""
    page.set_content('''
        <label for="pw">パスワード</label>
        <input id="pw" type="password" aria-describedby="pw-hint" />
        <span id="pw-hint">8文字以上で英数字を含めてください</span>
    ''')
    pw_input = page.locator("#pw")
    # aria-describedby で参照された要素のテキストが説明になる
    expect(pw_input).to_have_accessible_description("8文字以上で英数字を含めてください")


def test_accessible_description_with_regex(page: Page):
    """正規表現によるアクセシブル説明の部分一致検証"""
    page.set_content('''
        <button aria-describedby="del-desc">削除</button>
        <span id="del-desc">選択した5件のアイテムを完全に削除します</span>
    ''')
    button = page.get_by_role("button", name="削除")
    # 正規表現で説明の部分一致を検証
    expect(button).to_have_accessible_description(re.compile(r"\d+件のアイテム"))


def test_accessible_description_on_form_group(page: Page):
    """フォームグループにおけるアクセシブル説明の検証"""
    page.set_content('''
        <div role="group" aria-label="日付範囲" aria-describedby="date-help">
            <label for="start">開始日</label>
            <input id="start" type="date" />
            <label for="end">終了日</label>
            <input id="end" type="date" />
        </div>
        <span id="date-help">YYYY-MM-DD 形式で入力してください</span>
    ''')
    group = page.get_by_role("group", name="日付範囲")
    expect(group).to_have_accessible_description("YYYY-MM-DD 形式で入力してください")


# ============================================================
# 5. ARIA ロールの検証
#    (to_have_role)
# ============================================================


def test_to_have_role_implicit(page: Page):
    """暗黙的 ARIA ロールの検証"""
    page.set_content('''
        <button>ボタン要素</button>
        <a href="/page">リンク要素</a>
        <input type="checkbox" />
        <select><option>選択肢</option></select>
        <h1>見出し要素</h1>
    ''')
    # HTML 要素が持つ暗黙的な ARIA ロールを検証
    expect(page.locator("button")).to_have_role("button")
    expect(page.locator("a")).to_have_role("link")
    expect(page.locator("input")).to_have_role("checkbox")
    expect(page.locator("select")).to_have_role("combobox")
    expect(page.locator("h1")).to_have_role("heading")


def test_to_have_role_explicit(page: Page):
    """明示的 ARIA ロールの検証"""
    page.set_content('''
        <div role="alert">エラーが発生しました</div>
        <div role="status">処理中...</div>
        <div role="tablist">
            <button role="tab" aria-selected="true">タブ1</button>
            <button role="tab" aria-selected="false">タブ2</button>
        </div>
    ''')
    # role 属性で明示的に指定した ARIA ロールを検証
    expect(page.locator('[role="alert"]')).to_have_role("alert")
    expect(page.locator('[role="status"]')).to_have_role("status")
    # タブロールの検証
    tabs = page.get_by_role("tab")
    expect(tabs).to_have_count(2)
    expect(tabs.first).to_have_role("tab")


def test_to_have_role_landmark(page: Page):
    """ランドマークロールの検証"""
    page.set_content('''
        <header>ヘッダー</header>
        <nav aria-label="メイン">ナビゲーション</nav>
        <main>メインコンテンツ</main>
        <aside>サイドバー</aside>
        <footer>フッター</footer>
    ''')
    # HTML5 セマンティック要素のランドマークロールを検証
    expect(page.locator("header")).to_have_role("banner")
    expect(page.locator("nav")).to_have_role("navigation")
    expect(page.locator("main")).to_have_role("main")
    expect(page.locator("aside")).to_have_role("complementary")
    expect(page.locator("footer")).to_have_role("contentinfo")


# ============================================================
# 6. キーボードナビゲーションの確認
#    (Keyboard Navigation)
# ============================================================


def test_keyboard_tab_order(page: Page):
    """Tab キーによるフォーカス移動の検証"""
    page.set_content('''
        <button id="btn1">最初のボタン</button>
        <input id="input1" type="text" placeholder="テキスト入力" />
        <a id="link1" href="/next">次のページ</a>
        <button id="btn2">最後のボタン</button>
    ''')
    # 最初の要素にフォーカスを当てる
    page.locator("#btn1").focus()
    expect(page.locator("#btn1")).to_be_focused()
    # Tab キーで次のフォーカス可能な要素へ移動
    page.keyboard.press("Tab")
    expect(page.locator("#input1")).to_be_focused()
    page.keyboard.press("Tab")
    expect(page.locator("#link1")).to_be_focused()
    page.keyboard.press("Tab")
    expect(page.locator("#btn2")).to_be_focused()


def test_keyboard_shift_tab(page: Page):
    """Shift+Tab による逆方向フォーカス移動の検証"""
    page.set_content('''
        <button id="first">最初</button>
        <button id="second">2番目</button>
        <button id="third">3番目</button>
    ''')
    # 最後の要素からスタート
    page.locator("#third").focus()
    expect(page.locator("#third")).to_be_focused()
    # Shift+Tab で逆方向に移動
    page.keyboard.press("Shift+Tab")
    expect(page.locator("#second")).to_be_focused()
    page.keyboard.press("Shift+Tab")
    expect(page.locator("#first")).to_be_focused()


def test_keyboard_enter_activates_button(page: Page):
    """Enter キーによるボタン操作の検証"""
    page.set_content('''
        <button id="action-btn">実行</button>
        <div id="result" style="display: none;">完了</div>
        <script>
            document.getElementById('action-btn').addEventListener('click', () => {
                document.getElementById('result').style.display = 'block';
            });
        </script>
    ''')
    # ボタンにフォーカス
    page.locator("#action-btn").focus()
    # 結果表示が非表示であることを確認
    expect(page.locator("#result")).to_be_hidden()
    # Enter キーでボタンを押下
    page.keyboard.press("Enter")
    # クリックイベントが発火し、結果が表示される
    expect(page.locator("#result")).to_be_visible()


def test_keyboard_space_toggles_checkbox(page: Page):
    """Space キーによるチェックボックス操作の検証"""
    page.set_content('''
        <label>
            <input id="agree" type="checkbox" />
            同意する
        </label>
    ''')
    checkbox = page.locator("#agree")
    checkbox.focus()
    # 初期状態: 未チェック
    expect(checkbox).not_to_be_checked()
    # Space キーでチェックを切り替え
    page.keyboard.press("Space")
    expect(checkbox).to_be_checked()
    # もう一度 Space で解除
    page.keyboard.press("Space")
    expect(checkbox).not_to_be_checked()


def test_keyboard_escape_closes_dialog(page: Page):
    """Escape キーによるダイアログ終了の検証"""
    page.set_content('''
        <button id="open-btn">ダイアログを開く</button>
        <dialog id="my-dialog">
            <p>ダイアログの内容</p>
            <button id="close-btn">閉じる</button>
        </dialog>
        <script>
            document.getElementById('open-btn').addEventListener('click', () => {
                document.getElementById('my-dialog').showModal();
            });
        </script>
    ''')
    # ダイアログを開く
    page.locator("#open-btn").click()
    dialog = page.locator("#my-dialog")
    expect(dialog).to_be_visible()
    # Escape キーでダイアログを閉じる
    page.keyboard.press("Escape")
    expect(dialog).to_be_hidden()


def test_keyboard_tabindex_custom_order(page: Page):
    """tabindex によるカスタムタブ順序の検証"""
    page.set_content('''
        <button id="order3" tabindex="3">3番目</button>
        <button id="order1" tabindex="1">1番目</button>
        <button id="order2" tabindex="2">2番目</button>
        <button id="skip" tabindex="-1">スキップされる</button>
    ''')
    # tabindex の昇順でフォーカスが移動する
    page.keyboard.press("Tab")
    expect(page.locator("#order1")).to_be_focused()
    page.keyboard.press("Tab")
    expect(page.locator("#order2")).to_be_focused()
    page.keyboard.press("Tab")
    expect(page.locator("#order3")).to_be_focused()
    # tabindex="-1" の要素はタブ移動ではフォーカスされない
    page.keyboard.press("Tab")
    expect(page.locator("#skip")).not_to_be_focused()
