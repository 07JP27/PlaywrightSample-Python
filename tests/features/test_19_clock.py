"""
test_19_clock.py - Clock（時刻制御）のサンプル

ブラウザ内の時刻関数（Date, setTimeout, setInterval 等）を
フェイクタイマーで制御し、時間依存のテストを効率化する。
"""
import datetime

from playwright.sync_api import expect


# ---------------------------------------------------------------------------
# 1. フェイクタイマーのインストール (page.clock.install)
# ---------------------------------------------------------------------------
def test_install_fake_timers(page):
    """フェイクタイマーをインストールして Date を制御する"""
    # フェイクタイマーをインストール（時刻の基準を指定）
    page.clock.install(time=datetime.datetime(2025, 6, 15, 9, 0, 0))

    # Date.now() がインストール時に指定した時刻を返すことを確認
    page.set_content(
        '<div id="now"></div>'
        "<script>"
        'document.getElementById("now").textContent = new Date().toISOString();'
        "</script>"
    )

    time_text = page.locator("#now").text_content()
    assert "2025-06-15" in time_text


# ---------------------------------------------------------------------------
# 2. 固定時刻の設定 (page.clock.set_fixed_time)
# ---------------------------------------------------------------------------
def test_fixed_time(page):
    """固定時刻の設定"""
    page.clock.install()
    page.clock.set_fixed_time(datetime.datetime(2026, 1, 1, 12, 0, 0))

    page.set_content(
        '<div id="time"></div>'
        "<script>"
        'document.getElementById("time").textContent = new Date().toISOString();'
        "</script>"
    )

    time_text = page.locator("#time").text_content()
    assert "2026-01-01" in time_text


def test_fixed_time_does_not_advance(page):
    """set_fixed_time では時刻が自動で進まないことを確認する"""
    page.clock.install()
    page.clock.set_fixed_time(datetime.datetime(2026, 3, 15, 8, 30, 0))

    # 同じ時刻が繰り返し返される
    page.set_content(
        '<div id="t1"></div><div id="t2"></div>'
        "<script>"
        'document.getElementById("t1").textContent = Date.now();'
        "setTimeout(() => {"
        '  document.getElementById("t2").textContent = Date.now();'
        "}, 0);"
        "</script>"
    )

    t1 = page.locator("#t1").text_content()
    t2 = page.locator("#t2").text_content()
    # 固定時刻なので両方同じ値になる
    assert t1 == t2


# ---------------------------------------------------------------------------
# 3. 時間の早送り (page.clock.fast_forward)
# ---------------------------------------------------------------------------
def test_fast_forward(page):
    """時間の早送り"""
    page.clock.install()

    page.set_content(
        """
        <div id="result">待機中</div>
        <script>
            setTimeout(() => {
                document.getElementById("result").textContent = "完了";
            }, 5000);
        </script>
        """
    )

    # タイマー発火前は「待機中」
    assert page.locator("#result").text_content() == "待機中"
    # 5 秒早送りしてタイマーを発火させる
    page.clock.fast_forward(5000)
    assert page.locator("#result").text_content() == "完了"


def test_fast_forward_with_string(page):
    """文字列指定で時間を早送りする"""
    page.clock.install()

    page.set_content(
        """
        <div id="msg">初期</div>
        <script>
            setTimeout(() => {
                document.getElementById("msg").textContent = "1分後";
            }, 60000);
        </script>
        """
    )

    assert page.locator("#msg").text_content() == "初期"
    # "01:00" = 1 分を文字列で指定して早送り
    page.clock.fast_forward("01:00")
    assert page.locator("#msg").text_content() == "1分後"


# ---------------------------------------------------------------------------
# 4. 特定時刻での一時停止 (page.clock.pause_at)
# ---------------------------------------------------------------------------
def test_pause_at(page):
    """特定の時刻で一時停止し、時間を手動制御する"""
    # 指定した時刻でフェイクタイマーを一時停止状態にする
    page.clock.pause_at(datetime.datetime(2025, 12, 25, 12, 0, 0))

    # toLocaleString でローカルタイムゾーン（Asia/Tokyo）の日付を取得
    page.set_content(
        '<div id="paused"></div>'
        "<script>"
        'document.getElementById("paused").textContent = new Date().toLocaleDateString("ja-JP");'
        "</script>"
    )

    paused_text = page.locator("#paused").text_content()
    assert "2025/12/25" in paused_text

    # 一時停止中なので fast_forward で手動に進める
    page.clock.fast_forward(3600_000)  # 1 時間進める

    page.evaluate(
        'document.getElementById("paused").textContent = new Date().getHours()'
    )
    updated_text = page.locator("#paused").text_content()
    # 1 時間進んで 13 時になっている
    assert updated_text == "13"


# ---------------------------------------------------------------------------
# 5. 時間の再開 (page.clock.resume)
# ---------------------------------------------------------------------------
def test_resume(page):
    """一時停止した時間を再開してシステム時刻と同期させる"""
    page.clock.pause_at(datetime.datetime(2025, 7, 1, 0, 0, 0))

    page.set_content(
        '<div id="before"></div><div id="after"></div>'
        "<script>"
        'document.getElementById("before").textContent = Date.now();'
        "</script>"
    )

    before_val = int(page.locator("#before").text_content())

    # 時間を再開 ― 以降はリアルタイムのシステム時刻に追従する
    page.clock.resume()

    page.evaluate(
        'document.getElementById("after").textContent = String(Date.now())'
    )
    after_val = int(page.locator("#after").text_content())

    # 再開後は時刻が進む（before 以上になる）
    assert after_val >= before_val


# ---------------------------------------------------------------------------
# 6. 指定時間分の実行 (page.clock.run_for)
# ---------------------------------------------------------------------------
def test_run_for(page):
    """指定したミリ秒分だけタイマーを進める"""
    page.clock.install()

    # setInterval で 1 秒ごとにカウントアップする HTML
    page.set_content(
        """
        <div id="counter">0</div>
        <script>
            let count = 0;
            setInterval(() => {
                count++;
                document.getElementById("counter").textContent = String(count);
            }, 1000);
        </script>
        """
    )

    assert page.locator("#counter").text_content() == "0"

    # 3 秒分タイマーを実行 → カウンターが 3 になる
    page.clock.run_for(3000)
    assert page.locator("#counter").text_content() == "3"


def test_run_for_with_string(page):
    """文字列で指定した時間分だけ実行する"""
    page.clock.install()

    page.set_content(
        """
        <div id="tick">0</div>
        <script>
            let ticks = 0;
            setInterval(() => {
                ticks++;
                document.getElementById("tick").textContent = String(ticks);
            }, 1000);
        </script>
        """
    )

    # "00:05" = 5 秒分実行
    page.clock.run_for("00:05")
    expect(page.locator("#tick")).to_have_text("5")
