"""
test_e2e_google_search.py - Google 検索 E2E シナリオテスト

Google（https://www.google.com/）を対象とした
シンプルな検索フロー全体を検証するエンドツーエンドテスト。

テスト対象:
  - Google トップページへのアクセス
  - 検索クエリ入力・実行
  - 検索結果の表示確認

注意: Google はヘッドレスモードで bot 検知を行うため、
      headed モード（--headed）での実行を推奨。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import Page, expect, sync_playwright
from runner import TestRunner
from evidence import Evidence, generate_evidence_report

from pages.google.search_page import GoogleSearchPage


class TestGoogleSearchFlow:
    """Google 検索フローの E2E シナリオテストクラス"""

    # ------------------------------------------------------------------ #
    # 1. Google トップページのタイトル確認
    # ------------------------------------------------------------------ #
    def test_google_page_title(self, page: Page, evidence):
        """Google トップページにアクセスし、タイトルが正しいことを確認する"""
        search_page = GoogleSearchPage(page)

        search_page.navigate_to_google()
        evidence.capture("Googleトップページ表示")

        expect(page).to_have_title("Google")
        evidence.capture("タイトル確認完了")

    # ------------------------------------------------------------------ #
    # 2. Microsoft を検索して結果を確認（メインシナリオ）
    # ------------------------------------------------------------------ #
    def test_search_microsoft_and_view_results(self, page: Page, evidence):
        """Google で 'microsoft' を検索し、結果が表示されることを確認する"""
        search_page = GoogleSearchPage(page)

        # Step 1: Google トップページにアクセス
        search_page.navigate_to_google()
        evidence.capture("Googleトップページ表示")

        # Step 2: 検索ボックスに 'microsoft' を入力
        search_page.search_input.fill("microsoft")
        evidence.capture("検索クエリ入力_microsoft")

        # Step 3: 検索を実行
        search_page.search_input.press("Enter")
        page.wait_for_load_state("domcontentloaded")
        evidence.capture("検索実行後_結果ページ")

        # Step 4: 検索結果が表示されていることを確認
        assert search_page.has_results(), "検索結果が表示されていません"
        result_count = search_page.get_result_count()
        assert result_count > 0, f"検索結果が0件です"
        evidence.capture(f"検索結果_{result_count}件表示確認")

        # Step 5: 結果に Microsoft 関連のリンクが含まれることを確認
        titles = search_page.get_result_titles()
        has_microsoft = any("microsoft" in t.lower() or "マイクロソフト" in t for t in titles)
        assert has_microsoft, (
            f"検索結果に Microsoft 関連のリンクが見つかりません: {titles[:5]}"
        )
        evidence.capture("Microsoft関連リンク確認完了")

    # ------------------------------------------------------------------ #
    # 3. 検索ボックスの存在確認
    # ------------------------------------------------------------------ #
    def test_search_box_is_visible(self, page: Page, evidence):
        """Google トップページの検索ボックスが表示されていることを確認する"""
        search_page = GoogleSearchPage(page)

        search_page.navigate_to_google()
        evidence.capture("Googleトップページ表示")

        expect(search_page.search_input).to_be_visible()
        evidence.capture("検索ボックス表示確認")


def main():
    runner = TestRunner("test_e2e_google_search")
    session_id = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    all_evidence = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        instance = TestGoogleSearchFlow()

        test_methods = [
            instance.test_google_page_title,
            instance.test_search_microsoft_and_view_results,
            instance.test_search_box_is_visible,
        ]

        for test_func in test_methods:
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                locale="ja-JP",
                timezone_id="Asia/Tokyo",
            )
            page = context.new_page()

            output_dir = Path(__file__).resolve().parent.parent.parent / "output"
            scenario_name = Path(__file__).stem.replace("test_e2e_", "")
            evidence_dir = output_dir / "evidence" / "scenarios" / scenario_name / session_id
            ev = Evidence(test_func.__name__, evidence_dir, page)

            runner.run(test_func, page, ev)
            all_evidence.append(ev.metadata())
            context.close()

        browser.close()

    scenario_name = Path(__file__).stem.replace("test_e2e_", "")
    generate_evidence_report(scenario_name, all_evidence, session_id)
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
