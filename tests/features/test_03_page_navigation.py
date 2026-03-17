"""
test_03_page_navigation.py - ページ操作の基本サンプル

ページのナビゲーション、待機、プロパティ取得など
基本的なページ操作を示す。
"""
import re

import pytest


# ---------------------------------------------------------------------------
# 1. ページ遷移 (page.goto)
# ---------------------------------------------------------------------------

def test_goto_basic(page):
    """page.goto で指定 URL に遷移する"""
    response = page.goto("https://www.microsoft.com/ja-jp")
    # goto は Response オブジェクトを返す
    assert response is not None
    assert response.ok  # ステータスコード 200–299


def test_goto_with_wait_until(page):
    """page.goto の wait_until オプションで待機条件を指定する"""
    # "domcontentloaded": DOM 構築完了まで待機
    page.goto(
        "https://www.microsoft.com/ja-jp",
        wait_until="domcontentloaded",
    )
    assert "Microsoft" in page.title()

    # "load": load イベント発火まで待機（デフォルト）
    page.goto(
        "https://www.microsoft.com/ja-jp",
        wait_until="load",
    )
    assert "Microsoft" in page.title()


def test_goto_with_timeout(page):
    """page.goto の timeout オプションでタイムアウトを指定する"""
    # タイムアウトをミリ秒で指定（30 秒）
    page.goto("https://www.microsoft.com/ja-jp", timeout=30_000)
    assert "Microsoft" in page.title()


# ---------------------------------------------------------------------------
# 2. ページタイトル取得 (page.title)
# ---------------------------------------------------------------------------

def test_page_title(page):
    """page.title() で現在のページタイトルを取得する"""
    page.goto("https://www.microsoft.com/ja-jp")
    title = page.title()
    # タイトルは空でない文字列
    assert isinstance(title, str)
    assert len(title) > 0
    assert "Microsoft" in title


# ---------------------------------------------------------------------------
# 3. URL 取得 (page.url)
# ---------------------------------------------------------------------------

def test_page_url(page):
    """page.url で現在のページ URL を取得する"""
    page.goto("https://www.microsoft.com/ja-jp")
    url = page.url
    # url はプロパティ（メソッドではない）
    assert "microsoft.com" in url
    assert url.startswith("https://")


# ---------------------------------------------------------------------------
# 4. ページコンテンツ取得 (page.content)
# ---------------------------------------------------------------------------

def test_page_content(page):
    """page.content() で HTML ソースを取得する"""
    page.goto("https://www.microsoft.com/ja-jp")
    html = page.content()
    # HTML 文字列として基本的な構造を持つ
    assert "<html" in html.lower()
    assert "</html>" in html.lower()
    assert len(html) > 0


# ---------------------------------------------------------------------------
# 5. 戻る・進む (page.go_back, page.go_forward)
# ---------------------------------------------------------------------------

def test_go_back_and_forward(page):
    """page.go_back / page.go_forward で履歴を操作する"""
    # 最初のページに遷移
    page.goto("https://www.microsoft.com/ja-jp")
    first_url = page.url

    # リンクをクリックして別のページへ遷移
    page.goto("https://www.microsoft.com/ja-jp/microsoft-365")
    second_url = page.url
    assert first_url != second_url

    # go_back で前のページに戻る
    page.go_back()
    assert "microsoft.com/ja-jp" in page.url

    # go_forward で次のページに進む
    page.go_forward()
    assert "microsoft-365" in page.url


def test_go_back_returns_response(page):
    """page.go_back は Response オブジェクト（または None）を返す"""
    page.goto("https://www.microsoft.com/ja-jp")
    page.goto("https://www.microsoft.com/ja-jp/microsoft-365")

    # 戻る操作で Response を取得
    response = page.go_back()
    # 履歴がある場合は Response が返る
    if response is not None:
        assert response.ok


# ---------------------------------------------------------------------------
# 6. リロード (page.reload)
# ---------------------------------------------------------------------------

def test_reload(page):
    """page.reload() でページをリロードする"""
    page.goto("https://www.microsoft.com/ja-jp")
    title_before = page.title()

    # リロードを実行
    response = page.reload()
    title_after = page.title()

    # リロード後もタイトルは同じ
    assert title_before == title_after
    # reload は Response を返す
    assert response is not None
    assert response.ok


def test_reload_with_wait_until(page):
    """page.reload の wait_until オプションを指定する"""
    page.goto("https://www.microsoft.com/ja-jp")
    # networkidle: ネットワーク接続が 500ms 以上アイドル状態になるまで待機
    response = page.reload(wait_until="networkidle")
    assert response is not None
    assert response.ok


# ---------------------------------------------------------------------------
# 7. ロード状態待機 (page.wait_for_load_state)
# ---------------------------------------------------------------------------

def test_wait_for_load_state_load(page):
    """wait_for_load_state("load") で load イベントを待機する"""
    page.goto(
        "https://www.microsoft.com/ja-jp",
        wait_until="commit",
    )
    # load イベントの発火を明示的に待機
    page.wait_for_load_state("load")
    assert "Microsoft" in page.title()


def test_wait_for_load_state_domcontentloaded(page):
    """wait_for_load_state("domcontentloaded") で DOM 構築完了を待機する"""
    page.goto(
        "https://www.microsoft.com/ja-jp",
        wait_until="commit",
    )
    # DOMContentLoaded イベントの発火を待機
    page.wait_for_load_state("domcontentloaded")
    assert "Microsoft" in page.title()


def test_wait_for_load_state_networkidle(page):
    """wait_for_load_state("networkidle") でネットワーク安定を待機する"""
    page.goto("https://www.microsoft.com/ja-jp")
    # すべてのネットワークリクエストが落ち着くまで待機
    page.wait_for_load_state("networkidle")
    assert "Microsoft" in page.title()


# ---------------------------------------------------------------------------
# 8. URL 待機 (page.wait_for_url)
# ---------------------------------------------------------------------------

def test_wait_for_url_string(page):
    """wait_for_url で特定の URL 文字列を待機する"""
    page.goto("https://www.microsoft.com/ja-jp")
    # 現在の URL が一致していればすぐに通過する
    page.wait_for_url("**/ja-jp")
    assert "ja-jp" in page.url


def test_wait_for_url_pattern(page):
    """wait_for_url で正規表現パターンを使用する"""
    page.goto("https://www.microsoft.com/ja-jp")
    # 正規表現パターンで URL を待機
    page.wait_for_url(re.compile(r"microsoft\.com/ja-jp"))
    assert "microsoft.com" in page.url


def test_wait_for_url_after_navigation(page):
    """ナビゲーション後に wait_for_url で遷移先を確認する"""
    page.goto("https://www.microsoft.com/ja-jp")
    page.goto("https://www.microsoft.com/ja-jp/microsoft-365")
    # 遷移後の URL を待機・確認
    page.wait_for_url("**/microsoft-365**")
    assert "microsoft-365" in page.url


# ---------------------------------------------------------------------------
# 9. ビューポートサイズ変更 (page.set_viewport_size)
# ---------------------------------------------------------------------------

def test_set_viewport_size(page):
    """page.set_viewport_size でビューポートサイズを変更する"""
    page.goto("https://www.microsoft.com/ja-jp")

    # デスクトップサイズに設定
    page.set_viewport_size({"width": 1920, "height": 1080})
    viewport = page.viewport_size
    assert viewport["width"] == 1920
    assert viewport["height"] == 1080


def test_set_viewport_size_mobile(page):
    """モバイルサイズのビューポートに変更する"""
    # iPhone SE 相当のサイズ
    page.set_viewport_size({"width": 375, "height": 667})
    page.goto("https://www.microsoft.com/ja-jp")

    viewport = page.viewport_size
    assert viewport["width"] == 375
    assert viewport["height"] == 667


def test_set_viewport_size_tablet(page):
    """タブレットサイズのビューポートに変更する"""
    # iPad 相当のサイズ
    page.set_viewport_size({"width": 768, "height": 1024})
    page.goto("https://www.microsoft.com/ja-jp")

    viewport = page.viewport_size
    assert viewport["width"] == 768
    assert viewport["height"] == 1024


# ---------------------------------------------------------------------------
# 10. ページのクローズ (page.close)
# ---------------------------------------------------------------------------

def test_page_close(context):
    """page.close() でページを閉じる"""
    # context フィクスチャから新しいページを作成
    page = context.new_page()
    page.goto("https://www.microsoft.com/ja-jp")
    assert "Microsoft" in page.title()

    # ページを閉じる
    page.close()

    # close 後は is_closed() が True を返す
    assert page.is_closed() is True


def test_page_close_multiple_pages(context):
    """複数ページを開いて個別に閉じる"""
    # 複数のページを作成
    page1 = context.new_page()
    page2 = context.new_page()

    page1.goto("https://www.microsoft.com/ja-jp")
    page2.goto("https://www.microsoft.com/ja-jp/microsoft-365")

    # page1 だけを閉じる
    page1.close()
    assert page1.is_closed() is True
    assert page2.is_closed() is False

    # page2 はまだ操作可能
    assert "Microsoft" in page2.title()

    # page2 も閉じる
    page2.close()
    assert page2.is_closed() is True
