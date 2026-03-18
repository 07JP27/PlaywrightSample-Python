"""
test_09_file_operations.py - ファイル操作のサンプル

ファイルのアップロード（input 要素経由、ファイルチューザー経由）と
ダウンロードの操作を示す。
"""

import os
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

# プロジェクトルートからの相対パスでアップロード用ファイルを指定
PROJECT_ROOT = Path(__file__).parent.parent
UPLOAD_FILE = PROJECT_ROOT / "data" / "upload_sample.txt"


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


# ---------- ファイルアップロード ----------


def test_file_upload_via_input(page):
    """ファイルアップロード - input 要素経由 (set_input_files)"""
    page.set_content('<input type="file" id="upload">')

    # input 要素にファイルをセット
    page.locator("#upload").set_input_files(str(UPLOAD_FILE))

    # ファイルが設定されたことを確認
    files_count = page.locator("#upload").evaluate("el => el.files.length")
    assert files_count == 1

    # ファイル名を確認
    file_name = page.locator("#upload").evaluate("el => el.files[0].name")
    assert file_name == "upload_sample.txt"


def test_multiple_file_upload(page):
    """複数ファイルアップロード"""
    page.set_content('<input type="file" id="upload" multiple>')

    # 同じファイルを複数回指定して複数ファイルアップロードをシミュレート
    # 実際のプロジェクトでは異なるファイルを指定する
    second_file = PROJECT_ROOT / "data" / "upload_sample.txt"
    page.locator("#upload").set_input_files([
        str(UPLOAD_FILE),
        str(second_file),
    ])

    # 2 件のファイルが設定されたことを確認
    files_count = page.locator("#upload").evaluate("el => el.files.length")
    assert files_count == 2


def test_file_upload_via_file_chooser(page):
    """ファイルチューザー経由のアップロード (page.expect_file_chooser)"""
    page.set_content("""
        <button id="custom-upload" onclick="document.getElementById('hidden-input').click()">
            ファイルを選択
        </button>
        <input type="file" id="hidden-input" style="display:none">
    """)

    # ファイルチューザーの発火を待ちつつボタンをクリック
    with page.expect_file_chooser() as fc_info:
        page.locator("#custom-upload").click()

    file_chooser = fc_info.value

    # ファイルチューザー経由でファイルをセット
    file_chooser.set_files(str(UPLOAD_FILE))

    # ファイルが設定されたことを確認
    files_count = page.locator("#hidden-input").evaluate("el => el.files.length")
    assert files_count == 1


def test_clear_uploaded_file(page):
    """アップロードファイルのクリア (set_input_files([]))"""
    page.set_content('<input type="file" id="upload">')

    # まずファイルをセット
    page.locator("#upload").set_input_files(str(UPLOAD_FILE))
    files_count = page.locator("#upload").evaluate("el => el.files.length")
    assert files_count == 1

    # 空リストを渡してファイルをクリア
    page.locator("#upload").set_input_files([])

    # ファイルがクリアされたことを確認
    files_count = page.locator("#upload").evaluate("el => el.files.length")
    assert files_count == 0


# ---------- ファイルダウンロード ----------


def test_file_download(page):
    """ファイルダウンロード (page.expect_download)"""
    page.set_content(
        '<a href="data:text/plain,Hello" download="test.txt">ダウンロード</a>'
    )

    # ダウンロードイベントを待ちつつリンクをクリック
    with page.expect_download() as download_info:
        page.get_by_text("ダウンロード").click()

    download = download_info.value

    # ダウンロードしたファイルを一時パスに保存して中身を確認
    path = download.path()
    assert path is not None
    assert Path(path).read_text() == "Hello"


def test_download_file_info(page):
    """ダウンロードファイル情報取得 (suggested_filename, url)"""
    page.set_content(
        '<a href="data:text/plain,TestContent" download="report.csv">レポート取得</a>'
    )

    with page.expect_download() as download_info:
        page.get_by_text("レポート取得").click()

    download = download_info.value

    # suggested_filename: ブラウザが提示するファイル名
    assert download.suggested_filename == "report.csv"

    # url: ダウンロード元の URL
    assert download.url.startswith("data:text/plain")
