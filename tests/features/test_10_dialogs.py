"""
test_10_dialogs.py - ダイアログ処理のサンプル

alert, confirm, prompt のブラウザダイアログを
ハンドリングする方法を示す。ハンドラーはアクション実行前に登録する必要がある。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright
from runner import TestRunner


# ---------------------------------------------------------------------------
# 1. alert ダイアログの処理
# ---------------------------------------------------------------------------
def test_alert_dialog(page):
    """alert ダイアログを accept で閉じる"""
    dialog_message = []

    def handle_dialog(dialog):
        dialog_message.append(dialog.message)
        dialog.accept()

    # ダイアログハンドラーを登録してからアクションを実行
    page.on("dialog", handle_dialog)
    page.evaluate("alert('テストアラート')")

    assert dialog_message[0] == "テストアラート"


# ---------------------------------------------------------------------------
# 2. confirm ダイアログの承認
# ---------------------------------------------------------------------------
def test_confirm_accept(page):
    """confirm ダイアログを accept（OK）で閉じると true が返る"""

    def handle_dialog(dialog):
        dialog.accept()

    page.on("dialog", handle_dialog)
    # confirm() は OK なら true, キャンセルなら false を返す
    result = page.evaluate("confirm('続行しますか？')")

    assert result is True


# ---------------------------------------------------------------------------
# 3. confirm ダイアログの拒否
# ---------------------------------------------------------------------------
def test_confirm_dismiss(page):
    """confirm ダイアログを dismiss（キャンセル）で閉じると false が返る"""

    def handle_dialog(dialog):
        dialog.dismiss()

    page.on("dialog", handle_dialog)
    result = page.evaluate("confirm('削除しますか？')")

    assert result is False


# ---------------------------------------------------------------------------
# 4. prompt ダイアログへの入力
# ---------------------------------------------------------------------------
def test_prompt_accept_with_text(page):
    """prompt ダイアログにテキストを入力して accept する"""

    def handle_dialog(dialog):
        # accept にテキストを渡すと入力値として返される
        dialog.accept("こんにちは")

    page.on("dialog", handle_dialog)
    result = page.evaluate("prompt('名前を入力してください')")

    assert result == "こんにちは"


def test_prompt_dismiss(page):
    """prompt ダイアログを dismiss すると null が返る"""

    def handle_dialog(dialog):
        dialog.dismiss()

    page.on("dialog", handle_dialog)
    result = page.evaluate("prompt('名前を入力してください')")

    assert result is None


# ---------------------------------------------------------------------------
# 5. ダイアログのプロパティ取得
# ---------------------------------------------------------------------------
def test_dialog_properties_alert(page):
    """alert ダイアログの type, message を検証する"""
    dialog_info = {}

    def handle_dialog(dialog):
        dialog_info["type"] = dialog.type
        dialog_info["message"] = dialog.message
        dialog_info["default_value"] = dialog.default_value
        dialog.accept()

    page.on("dialog", handle_dialog)
    page.evaluate("alert('プロパティ確認')")

    assert dialog_info["type"] == "alert"
    assert dialog_info["message"] == "プロパティ確認"
    # alert にはデフォルト値がない
    assert dialog_info["default_value"] == ""


def test_dialog_properties_confirm(page):
    """confirm ダイアログの type を検証する"""
    dialog_info = {}

    def handle_dialog(dialog):
        dialog_info["type"] = dialog.type
        dialog_info["message"] = dialog.message
        dialog.accept()

    page.on("dialog", handle_dialog)
    page.evaluate("confirm('確認ダイアログ')")

    assert dialog_info["type"] == "confirm"
    assert dialog_info["message"] == "確認ダイアログ"


def test_dialog_properties_prompt(page):
    """prompt ダイアログの type, message, default_value を検証する"""
    dialog_info = {}

    def handle_dialog(dialog):
        dialog_info["type"] = dialog.type
        dialog_info["message"] = dialog.message
        dialog_info["default_value"] = dialog.default_value
        dialog.accept()

    page.on("dialog", handle_dialog)
    # 第2引数がデフォルト値になる
    page.evaluate("prompt('お名前は？', 'ゲスト')")

    assert dialog_info["type"] == "prompt"
    assert dialog_info["message"] == "お名前は？"
    assert dialog_info["default_value"] == "ゲスト"


# ---------------------------------------------------------------------------
# 6. page.once による一度きりのハンドラー
# ---------------------------------------------------------------------------
def test_once_handler(page):
    """page.once で登録したハンドラーは最初の1回だけ実行される"""
    handled_count = []

    def handle_dialog(dialog):
        handled_count.append(1)
        dialog.accept()

    # once で登録すると最初のダイアログのみハンドリングされる
    page.once("dialog", handle_dialog)
    page.evaluate("alert('1回目')")

    assert len(handled_count) == 1


def test_once_handler_multiple_dialogs(page):
    """once ハンドラーは2回目以降のダイアログには反応しない"""
    first_messages = []
    second_messages = []

    def handle_first(dialog):
        first_messages.append(dialog.message)
        dialog.accept()

    def handle_second(dialog):
        second_messages.append(dialog.message)
        dialog.accept()

    # 1回目用と2回目用で別々の once ハンドラーを順番に登録
    page.once("dialog", handle_first)
    page.evaluate("alert('最初のダイアログ')")

    page.once("dialog", handle_second)
    page.evaluate("alert('次のダイアログ')")

    # 各ハンドラーがそれぞれ1回だけ呼ばれたことを確認
    assert first_messages == ["最初のダイアログ"]
    assert second_messages == ["次のダイアログ"]


def main():
    runner = TestRunner("test_10_dialogs")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for test_func in [
            test_alert_dialog,
            test_confirm_accept,
            test_confirm_dismiss,
            test_prompt_accept_with_text,
            test_prompt_dismiss,
            test_dialog_properties_alert,
            test_dialog_properties_confirm,
            test_dialog_properties_prompt,
            test_once_handler,
            test_once_handler_multiple_dialogs,
        ]:
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                locale="ja-JP",
                timezone_id="Asia/Tokyo",
            )
            page = context.new_page()
            runner.run(test_func, page)
            context.close()
        browser.close()
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
