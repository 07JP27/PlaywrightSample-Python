"""
conftest.py - E2Eシナリオテスト用フィクスチャ

シナリオテスト共通の設定・データロード・ヘルパーを提供する。
エビデンス記録（全画面スクリーンショット＋HTMLレポート）機能を含む。
"""
import json
from datetime import datetime
from pathlib import Path

import pytest
from playwright.sync_api import Page


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "scenarios"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "output"


# ============================================================
# エビデンス記録クラス
# ============================================================

class Evidence:
    """テスト実行のエビデンス（スクリーンショット＋メタデータ）を記録するクラス

    JTCの品質管理基準に準拠し、全画面遷移のスクリーンショットを
    連番付きで保存し、HTMLレポートとして出力する。
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
        # ファイル名をサニタイズ（日本語もそのまま使用可能）
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


# セッション中の全テストのエビデンスを収集
_all_evidence: list[dict] = []
_session_id: str = ""


# ============================================================
# テストデータフィクスチャ
# ============================================================

@pytest.fixture(scope="session")
def test_users():
    """テストユーザー情報を読み込む"""
    with open(DATA_DIR / "test_users.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def test_products():
    """テスト商品情報を読み込む"""
    with open(DATA_DIR / "test_products.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def test_employees():
    """テスト従業員情報を読み込む"""
    with open(DATA_DIR / "test_employees.json", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# エビデンスフィクスチャ
# ============================================================

@pytest.fixture
def screenshot_dir():
    """スクリーンショット保存ディレクトリ（後方互換用）"""
    dir_path = OUTPUT_DIR / "screenshots" / "scenarios"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


@pytest.fixture
def evidence(request, page: Page):
    """エビデンス記録フィクスチャ

    各テストで evidence.capture("ステップ名") を呼ぶと
    連番付きスクリーンショットが自動保存される。
    テスト終了時に結果を全体レポート用に収集する。
    """
    global _session_id
    if not _session_id:
        _session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    test_name = request.node.name
    # ブラウザパラメータを除去（例: test_xxx[chromium] → test_xxx）
    if "[" in test_name:
        test_name = test_name[:test_name.index("[")]
    # クラス名を含める
    if request.node.cls:
        test_name = f"{request.node.cls.__name__}__{test_name}"

    # シナリオ名をテストファイル名から取得（例: test_e2e_ec_purchase → ec_purchase）
    test_file = Path(request.node.fspath).stem
    scenario_name = test_file.replace("test_e2e_", "")

    evidence_dir = OUTPUT_DIR / "evidence" / "scenarios" / scenario_name / _session_id
    ev = Evidence(test_name, evidence_dir, page)

    yield ev

    # テスト終了後、メタデータを収集
    _all_evidence.append({
        "test_name": test_name,
        "test_nodeid": request.node.nodeid,
        "scenario": scenario_name,
        "steps": ev.steps,
        "output_dir": str(ev.output_dir),
    })


# ============================================================
# HTMLエビデンスレポート生成
# ============================================================

def pytest_sessionfinish(session, exitstatus):
    """テストセッション終了時にHTMLエビデンスレポートをシナリオ別に生成する"""
    if not _all_evidence:
        return

    timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

    # シナリオごとにグループ化
    from collections import defaultdict
    by_scenario = defaultdict(list)
    for ev_data in _all_evidence:
        by_scenario[ev_data["scenario"]].append(ev_data)

    generated = []
    for scenario_name, evidences in by_scenario.items():
        report_dir = OUTPUT_DIR / "evidence" / "scenarios" / scenario_name / _session_id
        report_dir.mkdir(parents=True, exist_ok=True)
        report_filename = f"evidence_{scenario_name}_{_session_id}.html"
        report_path = report_dir / report_filename

        total_tests = len(evidences)
        total_steps = sum(len(e["steps"]) for e in evidences)

        html = _generate_report_html(scenario_name, evidences, timestamp, total_tests, total_steps)
        report_path.write_text(html, encoding="utf-8")
        generated.append(report_path)

    print(f"\n📋 エビデンスレポート生成完了（{len(generated)} シナリオ）:")
    for p in generated:
        print(f"   {p}")


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
        .toc { padding: 20px 32px; background: white; margin: 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .toc h2 { margin-bottom: 12px; font-size: 1.2em; border-bottom: 2px solid #1a237e; padding-bottom: 8px; }
        .toc ul { list-style: none; }
        .toc li { padding: 6px 0; }
        .toc a { color: #1a237e; text-decoration: none; }
        .toc a:hover { text-decoration: underline; }
        .toc .step-count { color: #888; font-size: 0.85em; margin-left: 8px; }
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
        .step-screenshot img { max-width: 100%; border: 1px solid #e0e0e0; border-radius: 4px; cursor: pointer; transition: transform 0.2s; }
        .step-screenshot img:hover { transform: scale(1.02); }
        .footer { text-align: center; padding: 24px; color: #999; font-size: 0.85em; }
        @media print {
            .step-screenshot img { max-width: 100%; page-break-inside: avoid; }
            .test-section { page-break-inside: avoid; }
        }
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

    # 目次
    html_parts.append("<div class='toc'>")
    html_parts.append("<h2>📑 目次</h2>")
    html_parts.append("<ul>")
    for ev_data in evidences:
        step_count = len(ev_data["steps"])
        html_parts.append(
            f"<li><a href='#{ev_data['test_name']}'>{ev_data['test_name']}</a>"
            f"<span class='step-count'>（{step_count} ステップ）</span></li>"
        )
    html_parts.append("</ul>")
    html_parts.append("</div>")

    # 各テストセクション
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
            html_parts.append(f"<span>📄 {step['title']}</span>")
            html_parts.append("</div>")
            html_parts.append(f"<div class='step-screenshot'><img src='{img_rel_path}' alt='{step['description']}' loading='lazy'></div>")
            html_parts.append("</div>")
            html_parts.append("</div>")

        if not ev_data["steps"]:
            html_parts.append("<div class='step'><div class='step-info'>エビデンスなし（evidence.capture() 未呼出）</div></div>")

        html_parts.append("</div>")

    html_parts.append("<div class='footer'>E2E Test Evidence Report — Generated by pytest + Playwright</div>")
    html_parts.append("</body></html>")

    return "\n".join(html_parts)

