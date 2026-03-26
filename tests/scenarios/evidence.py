"""
evidence.py - テスト実行のエビデンス記録モジュール

スクリーンショット＋メタデータの記録と HTML レポート生成を行う。
pytest に依存せず、各テストスクリプトから直接使用する。

使い方:
    from evidence import Evidence, generate_evidence_report

    ev = Evidence("test_name", output_dir, page)
    ev.capture("ログイン画面表示")
    ...
    generate_evidence_report("scenario_name", [ev.metadata()], session_id)
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "scenarios"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"


def load_test_users() -> dict:
    """テストユーザー情報を読み込む"""
    with open(DATA_DIR / "test_users.json", encoding="utf-8") as f:
        return json.load(f)


def load_test_products() -> list:
    """テスト商品情報を読み込む"""
    with open(DATA_DIR / "test_products.json", encoding="utf-8") as f:
        return json.load(f)


def load_test_employees() -> list:
    """テスト従業員情報を読み込む"""
    with open(DATA_DIR / "test_employees.json", encoding="utf-8") as f:
        return json.load(f)


class Evidence:
    """テスト実行のエビデンス（スクリーンショット＋メタデータ）を記録するクラス

    全画面遷移のスクリーンショットを連番付きで保存し、
    メタデータを収集する。
    """

    def __init__(self, test_name: str, output_dir: Path, page: Page):
        self.test_name = test_name
        self.output_dir = output_dir / test_name
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.page = page
        self._step_count = 0
        self.steps: list[dict] = []

    def capture(self, step_description: str, *, full_page: bool = False):
        """画面のスクリーンショットを記録する

        Args:
            step_description: ステップの説明（例: "ログイン画面表示"）
            full_page: True の場合、ページ全体をキャプチャ
        """
        self._step_count += 1
        safe_desc = step_description.replace("/", "_").replace("\\", "_").replace(" ", "_")
        filename = f"{self._step_count:02d}_{safe_desc}.png"
        filepath = self.output_dir / filename

        self.page.screenshot(path=str(filepath), full_page=full_page)

        self.steps.append({
            "step": self._step_count,
            "description": step_description,
            "filename": filename,
            "url": self.page.url,
            "title": self.page.title(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    @property
    def step_count(self) -> int:
        return self._step_count

    def metadata(self) -> dict:
        """エビデンスのメタデータを返す"""
        return {
            "test_name": self.test_name,
            "steps": self.steps,
            "output_dir": str(self.output_dir),
        }


def generate_evidence_report(
    scenario_name: str,
    all_evidence: list[dict],
    session_id: str,
) -> Path | None:
    """HTML エビデンスレポートを生成する

    Args:
        scenario_name: シナリオ名（例: "ec_purchase"）
        all_evidence: Evidence.metadata() のリスト
        session_id: セッション ID（タイムスタンプ等）

    Returns:
        生成したレポートファイルのパス
    """
    if not all_evidence:
        return None

    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    report_dir = OUTPUT_DIR / "evidence" / "scenarios" / scenario_name / session_id
    report_dir.mkdir(parents=True, exist_ok=True)
    report_filename = f"evidence_{scenario_name}_{session_id}.html"
    report_path = report_dir / report_filename

    total_tests = len(all_evidence)
    total_steps = sum(len(e["steps"]) for e in all_evidence)

    html = _generate_report_html(scenario_name, all_evidence, timestamp, total_tests, total_steps)
    report_path.write_text(html, encoding="utf-8")

    print(f"\n📋 エビデンスレポート生成完了:")
    print(f"   {report_path}")
    return report_path


def _generate_report_html(
    scenario_name: str,
    evidences: list[dict],
    timestamp: str,
    total_tests: int,
    total_steps: int,
) -> str:
    """シナリオ単位のHTMLエビデンスレポートを生成する"""

    SCENARIO_LABELS = {
        "ec_purchase": "EC 購買フロー",
        "hr_management": "HR 勤怠管理フロー",
        "portal_auth": "ポータル認証・フォーム操作フロー",
        "application_form": "申請ワークフロー",
        "cross_system": "API + UI 複合シナリオ",
        "google_search": "Google 検索フロー",
    }
    label = SCENARIO_LABELS.get(scenario_name, scenario_name)

    html_parts = [
        "<!DOCTYPE html>",
        "<html lang='ja'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>",
        f"<title>エビデンスレポート — {label} — {timestamp}</title>",
        "<style>",
        """
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', 'Meiryo', sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }
        .header { background: #1a237e; color: white; padding: 24px 32px; }
        .header h1 { font-size: 1.5em; }
        .header .meta { font-size: 0.9em; opacity: 0.85; margin-top: 8px; }
        .summary { display: flex; gap: 24px; padding: 20px 32px; background: white; border-bottom: 1px solid #e0e0e0; }
        .summary-card { padding: 12px 24px; background: #e8eaf6; border-radius: 8px; text-align: center; }
        .summary-card .number { font-size: 2em; font-weight: bold; color: #1a237e; }
        .summary-card .label { font-size: 0.85em; color: #666; }
        .test-section { margin: 16px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; }
        .test-section h2 { background: #283593; color: white; padding: 14px 24px; font-size: 1.1em; }
        .step { display: flex; gap: 20px; padding: 16px 24px; border-bottom: 1px solid #f0f0f0; align-items: flex-start; }
        .step:last-child { border-bottom: none; }
        .step-number { background: #1a237e; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.85em; flex-shrink: 0; }
        .step-info { flex: 1; min-width: 0; }
        .step-desc { font-weight: bold; margin-bottom: 4px; }
        .step-meta { font-size: 0.8em; color: #888; }
        .step-meta span { margin-right: 16px; }
        .step-screenshot { margin-top: 8px; }
        .step-screenshot img { max-width: 100%; border: 1px solid #e0e0e0; border-radius: 4px; }
        .footer { text-align: center; padding: 24px; color: #999; font-size: 0.85em; }
        """,
        "</style>",
        "</head>",
        "<body>",
        "<div class='header'>",
        f"<h1>📋 {label} — エビデンスレポート</h1>",
        f"<div class='meta'>生成日時: {timestamp} ｜ シナリオ: {scenario_name} ｜ Playwright for Python</div>",
        "</div>",
        "<div class='summary'>",
        f"<div class='summary-card'><div class='number'>{total_tests}</div><div class='label'>テストケース</div></div>",
        f"<div class='summary-card'><div class='number'>{total_steps}</div><div class='label'>画面キャプチャ</div></div>",
        "</div>",
    ]

    for ev_data in evidences:
        test_name = ev_data["test_name"]
        html_parts.append(f"<div class='test-section' id='{test_name}'>")
        html_parts.append(f"<h2>🔍 {test_name}</h2>")

        for step in ev_data["steps"]:
            img_rel_path = f"{test_name}/{step['filename']}"
            html_parts.append("<div class='step'>")
            html_parts.append(f"<div class='step-number'>{step['step']}</div>")
            html_parts.append("<div class='step-info'>")
            html_parts.append(f"<div class='step-desc'>{step['description']}</div>")
            html_parts.append("<div class='step-meta'>")
            html_parts.append(f"<span>🕐 {step['timestamp']}</span>")
            html_parts.append(f"<span>🌐 {step['url']}</span>")
            html_parts.append("</div>")
            html_parts.append(f"<div class='step-screenshot'><img src='{img_rel_path}' alt='{step['description']}'></div>")
            html_parts.append("</div></div>")

        if not ev_data["steps"]:
            html_parts.append("<div class='step'><div class='step-info'>エビデンスなし</div></div>")

        html_parts.append("</div>")

    html_parts.append("<div class='footer'>E2E Test Evidence Report — Generated by Playwright for Python</div>")
    html_parts.append("</body></html>")

    return "\n".join(html_parts)
