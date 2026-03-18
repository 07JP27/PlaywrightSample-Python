"""
test_14_emulation.py - エミュレーションのサンプル

デバイス、ジオロケーション、ロケール、タイムゾーン、カラースキームなど
様々な環境をエミュレートする方法を示す。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

from runner import TestRunner

SKIP_TESTS = {}

TARGET_URL = "https://www.microsoft.com/ja-jp"


# ---------------------------------------------------------------------------
# 1. デバイスエミュレーション
# ---------------------------------------------------------------------------
class TestDeviceEmulation:
    """p.devices[] を使ったデバイスプリセットによるエミュレーション"""

    def test_iphone_13_emulation(self):
        """iPhone 13 のプリセットでエミュレートする"""
        with sync_playwright() as p:
            # デバイスプリセットを取得
            iphone_13 = p.devices["iPhone 13"]
            browser = p.chromium.launch()
            # プリセットを展開してコンテキストを作成
            context = browser.new_context(**iphone_13)
            page = context.new_page()
            page.goto(TARGET_URL)

            # プリセットに含まれるビューポートサイズを確認
            width = page.evaluate("window.innerWidth")
            height = page.evaluate("window.innerHeight")
            assert width == iphone_13["viewport"]["width"]
            assert height == iphone_13["viewport"]["height"]

            # ユーザーエージェントがモバイル向けになっていることを確認
            ua = page.evaluate("navigator.userAgent")
            assert "iPhone" in ua or "Mobile" in ua

            context.close()
            browser.close()

    def test_pixel_5_emulation(self):
        """Pixel 5 のプリセットでエミュレートする"""
        with sync_playwright() as p:
            pixel_5 = p.devices["Pixel 5"]
            browser = p.chromium.launch()
            context = browser.new_context(**pixel_5)
            page = context.new_page()
            page.goto(TARGET_URL)

            # モバイルデバイスとして認識されることを確認
            is_mobile = page.evaluate(
                "('ontouchstart' in window) || (navigator.maxTouchPoints > 0)"
            )
            assert is_mobile is True

            context.close()
            browser.close()

    def test_ipad_emulation(self):
        """iPad のプリセットでタブレットをエミュレートする"""
        with sync_playwright() as p:
            ipad = p.devices["iPad (gen 7)"]
            browser = p.webkit.launch()
            context = browser.new_context(**ipad)
            page = context.new_page()
            page.goto(TARGET_URL)

            # タブレットサイズのビューポートを確認
            width = page.evaluate("window.innerWidth")
            assert width == ipad["viewport"]["width"]

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 2. ビューポート設定
# ---------------------------------------------------------------------------
class TestViewport:
    """viewport オプションによるカスタムビューポートサイズの設定"""

    def test_mobile_viewport(self):
        """モバイルサイズのビューポートを設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 375, "height": 667}
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            width = page.evaluate("window.innerWidth")
            height = page.evaluate("window.innerHeight")
            assert width == 375
            assert height == 667

            context.close()
            browser.close()

    def test_desktop_viewport(self):
        """デスクトップサイズのビューポートを設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            width = page.evaluate("window.innerWidth")
            assert width == 1920

            context.close()
            browser.close()

    def test_set_viewport_size_on_page(self):
        """ページ単位でビューポートサイズを動的に変更する"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(TARGET_URL)

            # ビューポートサイズを動的に変更
            page.set_viewport_size({"width": 640, "height": 480})

            width = page.evaluate("window.innerWidth")
            height = page.evaluate("window.innerHeight")
            assert width == 640
            assert height == 480

            browser.close()


# ---------------------------------------------------------------------------
# 3. デバイススケール
# ---------------------------------------------------------------------------
class TestDeviceScaleFactor:
    """device_scale_factor（DPR）の設定"""

    def test_retina_display(self):
        """Retina ディスプレイ相当の DPR=2 を設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 375, "height": 667},
                device_scale_factor=2,
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            # devicePixelRatio を確認
            dpr = page.evaluate("window.devicePixelRatio")
            assert dpr == 2

            context.close()
            browser.close()

    def test_high_dpi_display(self):
        """高 DPI ディスプレイ（DPR=3）を設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 360, "height": 780},
                device_scale_factor=3,
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            dpr = page.evaluate("window.devicePixelRatio")
            assert dpr == 3

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 4. モバイルモード
# ---------------------------------------------------------------------------
class TestMobileMode:
    """is_mobile オプションによるモバイルモード設定"""

    def test_mobile_mode_enabled(self):
        """モバイルモードを有効にする"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 375, "height": 667},
                is_mobile=True,
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            # モバイルモードでは meta viewport が反映される
            width = page.evaluate("window.innerWidth")
            assert width > 0

            context.close()
            browser.close()

    def test_mobile_mode_disabled(self):
        """モバイルモードを無効にする（デフォルト）"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 375, "height": 667},
                is_mobile=False,
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            # デスクトップモードのビューポート幅を確認
            width = page.evaluate("window.innerWidth")
            assert width == 375

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 5. タッチサポート
# ---------------------------------------------------------------------------
class TestTouchSupport:
    """has_touch オプションによるタッチデバイスのエミュレーション"""

    def test_touch_enabled(self):
        """タッチサポートを有効にする"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(has_touch=True)
            page = context.new_page()
            page.goto(TARGET_URL)

            # タッチ対応デバイスとして認識されることを確認
            has_touch = page.evaluate(
                "('ontouchstart' in window) || (navigator.maxTouchPoints > 0)"
            )
            assert has_touch is True

            context.close()
            browser.close()

    def test_touch_disabled(self):
        """タッチサポートを無効にする（デフォルト）"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(has_touch=False)
            page = context.new_page()
            page.goto(TARGET_URL)

            # タッチ非対応デバイスであることを確認
            max_touch_points = page.evaluate("navigator.maxTouchPoints")
            assert max_touch_points == 0

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 6. ジオロケーション
# ---------------------------------------------------------------------------
class TestGeolocation:
    """geolocation + permissions による位置情報のエミュレーション"""

    def test_geolocation_tokyo(self):
        """東京の座標をジオロケーションとして設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                geolocation={"latitude": 35.6762, "longitude": 139.6503},
                permissions=["geolocation"],
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            # Geolocation API で座標を取得して検証
            position = page.evaluate(
                """() => new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        pos => resolve({
                            latitude: pos.coords.latitude,
                            longitude: pos.coords.longitude
                        })
                    );
                })"""
            )
            assert position["latitude"] == pytest.approx(35.6762, abs=0.001)
            assert position["longitude"] == pytest.approx(139.6503, abs=0.001)

            context.close()
            browser.close()

    def test_geolocation_new_york(self):
        """ニューヨークの座標をジオロケーションとして設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                geolocation={"latitude": 40.7128, "longitude": -74.0060},
                permissions=["geolocation"],
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            position = page.evaluate(
                """() => new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        pos => resolve({
                            latitude: pos.coords.latitude,
                            longitude: pos.coords.longitude
                        })
                    );
                })"""
            )
            assert position["latitude"] == pytest.approx(40.7128, abs=0.001)
            assert position["longitude"] == pytest.approx(-74.0060, abs=0.001)

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 7. ロケール設定
# ---------------------------------------------------------------------------
class TestLocale:
    """locale オプションによる言語・地域設定のエミュレーション"""

    def test_locale_japanese(self):
        """日本語ロケールを設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(locale="ja-JP")
            page = context.new_page()
            page.goto(TARGET_URL)

            # JavaScript でロケールを確認
            locale = page.evaluate("navigator.language")
            assert locale == "ja-JP"

            context.close()
            browser.close()

    def test_locale_english(self):
        """英語（米国）ロケールを設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(locale="en-US")
            page = context.new_page()
            page.goto(TARGET_URL)

            locale = page.evaluate("navigator.language")
            assert locale == "en-US"

            context.close()
            browser.close()

    def test_locale_affects_formatting(self):
        """ロケールが数値フォーマットに影響することを確認"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(locale="de-DE")
            page = context.new_page()
            page.goto(TARGET_URL)

            # ドイツ語ロケールでは小数点にカンマを使用
            formatted = page.evaluate(
                "(1234.56).toLocaleString()"
            )
            # ドイツ語では "1.234,56" のように表示される
            assert "," in formatted

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 8. タイムゾーン設定
# ---------------------------------------------------------------------------
class TestTimezone:
    """timezone_id オプションによるタイムゾーンのエミュレーション"""

    def test_timezone_tokyo(self):
        """東京タイムゾーン（UTC+9）を設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(timezone_id="Asia/Tokyo")
            page = context.new_page()
            page.goto(TARGET_URL)

            # タイムゾーンオフセットを確認（UTC+9 = -540 分）
            offset = page.evaluate("new Date().getTimezoneOffset()")
            assert offset == -540

            context.close()
            browser.close()

    def test_timezone_new_york(self):
        """ニューヨークタイムゾーンを設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(timezone_id="America/New_York")
            page = context.new_page()
            page.goto(TARGET_URL)

            # EST（UTC-5）= 300 分 または EDT（UTC-4）= 240 分
            offset = page.evaluate("new Date().getTimezoneOffset()")
            assert offset in [240, 300]

            context.close()
            browser.close()

    def test_timezone_in_date_string(self):
        """タイムゾーンが日付文字列に反映されることを確認"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(timezone_id="Europe/London")
            page = context.new_page()
            page.goto(TARGET_URL)

            # Intl API でタイムゾーン名を確認
            tz = page.evaluate(
                "Intl.DateTimeFormat().resolvedOptions().timeZone"
            )
            assert tz == "Europe/London"

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 9. カラースキーム
# ---------------------------------------------------------------------------
class TestColorScheme:
    """color_scheme オプションによるダーク/ライトモードのエミュレーション"""

    def test_dark_mode(self):
        """ダークモードを設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(color_scheme="dark")
            page = context.new_page()
            page.goto(TARGET_URL)

            # メディアクエリでダークモードを確認
            is_dark = page.evaluate(
                "window.matchMedia('(prefers-color-scheme: dark)').matches"
            )
            assert is_dark is True

            context.close()
            browser.close()

    def test_light_mode(self):
        """ライトモードを設定"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(color_scheme="light")
            page = context.new_page()
            page.goto(TARGET_URL)

            # メディアクエリでライトモードを確認
            is_light = page.evaluate(
                "window.matchMedia('(prefers-color-scheme: light)').matches"
            )
            assert is_light is True

            context.close()
            browser.close()

    def test_emulate_media_color_scheme(self):
        """page.emulate_media() でカラースキームを動的に変更"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(color_scheme="light")
            page = context.new_page()
            page.goto(TARGET_URL)

            # 初期状態はライトモード
            is_light = page.evaluate(
                "window.matchMedia('(prefers-color-scheme: light)').matches"
            )
            assert is_light is True

            # ダークモードに切り替え
            page.emulate_media(color_scheme="dark")
            is_dark = page.evaluate(
                "window.matchMedia('(prefers-color-scheme: dark)').matches"
            )
            assert is_dark is True

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 10. ユーザーエージェント
# ---------------------------------------------------------------------------
class TestUserAgent:
    """user_agent オプションによるカスタムユーザーエージェントの設定"""

    def test_custom_user_agent(self):
        """カスタムユーザーエージェントを設定"""
        custom_ua = "PlaywrightSample/1.0 (TestBot)"
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(user_agent=custom_ua)
            page = context.new_page()
            page.goto(TARGET_URL)

            # navigator.userAgent で確認
            actual_ua = page.evaluate("navigator.userAgent")
            assert actual_ua == custom_ua

            context.close()
            browser.close()

    def test_mobile_user_agent(self):
        """モバイルユーザーエージェントを設定"""
        mobile_ua = (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/16.0 Mobile/15E148 Safari/604.1"
        )
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(user_agent=mobile_ua)
            page = context.new_page()
            page.goto(TARGET_URL)

            actual_ua = page.evaluate("navigator.userAgent")
            assert "iPhone" in actual_ua
            assert "Mobile" in actual_ua

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 11. オフラインモード
# ---------------------------------------------------------------------------
class TestOfflineMode:
    """context.set_offline() によるオフライン状態のエミュレーション"""

    def test_set_offline(self):
        """オフラインモードに切り替え、ネットワーク接続が無効になることを確認"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto(TARGET_URL)

            # オフラインモードに切り替え
            context.set_offline(True)

            # navigator.onLine でオフライン状態を確認
            is_online = page.evaluate("navigator.onLine")
            assert is_online is False

            context.close()
            browser.close()

    def test_restore_online(self):
        """オフラインからオンラインに復帰する"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            page.goto(TARGET_URL)

            # オフラインに切り替え
            context.set_offline(True)
            assert page.evaluate("navigator.onLine") is False

            # オンラインに復帰
            context.set_offline(False)
            assert page.evaluate("navigator.onLine") is True

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 12. ジオロケーション変更
# ---------------------------------------------------------------------------
class TestGeolocationChange:
    """context.set_geolocation() による動的な位置情報の変更"""

    def test_change_geolocation(self):
        """コンテキスト作成後にジオロケーションを変更する"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            # 初期位置: 東京
            context = browser.new_context(
                geolocation={"latitude": 35.6762, "longitude": 139.6503},
                permissions=["geolocation"],
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            # 初期位置を確認
            position = page.evaluate(
                """() => new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        pos => resolve({
                            latitude: pos.coords.latitude,
                            longitude: pos.coords.longitude
                        })
                    );
                })"""
            )
            assert position["latitude"] == pytest.approx(35.6762, abs=0.001)

            # 位置を大阪に変更
            context.set_geolocation(
                {"latitude": 34.6937, "longitude": 135.5023}
            )

            # 変更後の位置を確認
            new_position = page.evaluate(
                """() => new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        pos => resolve({
                            latitude: pos.coords.latitude,
                            longitude: pos.coords.longitude
                        })
                    );
                })"""
            )
            assert new_position["latitude"] == pytest.approx(34.6937, abs=0.001)
            assert new_position["longitude"] == pytest.approx(135.5023, abs=0.001)

            context.close()
            browser.close()

    def test_clear_geolocation(self):
        """ジオロケーションを None に設定してクリアする"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                geolocation={"latitude": 35.6762, "longitude": 139.6503},
                permissions=["geolocation"],
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            # ジオロケーションをクリア
            context.set_geolocation(None)

            # クリア後は位置取得がエラーになることを確認
            error_occurred = page.evaluate(
                """() => new Promise((resolve) => {
                    navigator.geolocation.getCurrentPosition(
                        () => resolve(false),
                        () => resolve(true)
                    );
                })"""
            )
            assert error_occurred is True

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 13. パーミッション操作
# ---------------------------------------------------------------------------
class TestPermissions:
    """grant_permissions / clear_permissions によるパーミッション制御"""

    def test_grant_geolocation_permission(self):
        """geolocation パーミッションを許可"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()

            # geolocation パーミッションを付与
            context.grant_permissions(["geolocation"])

            page = context.new_page()
            page.goto(TARGET_URL)

            # Permissions API でパーミッション状態を確認
            state = page.evaluate(
                """async () => {
                    const result = await navigator.permissions.query(
                        { name: 'geolocation' }
                    );
                    return result.state;
                }"""
            )
            assert state == "granted"

            context.close()
            browser.close()

    def test_grant_multiple_permissions(self):
        """複数のパーミッションを同時に許可"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()

            # 複数パーミッションを一度に付与
            context.grant_permissions(["geolocation", "notifications"])

            page = context.new_page()
            page.goto(TARGET_URL)

            # 各パーミッションの状態を確認
            geo_state = page.evaluate(
                """async () => {
                    const result = await navigator.permissions.query(
                        { name: 'geolocation' }
                    );
                    return result.state;
                }"""
            )
            notification_state = page.evaluate(
                """async () => {
                    const result = await navigator.permissions.query(
                        { name: 'notifications' }
                    );
                    return result.state;
                }"""
            )
            assert geo_state == "granted"
            assert notification_state == "granted"

            context.close()
            browser.close()

    def test_grant_permissions_for_origin(self):
        """特定オリジンに対してのみパーミッションを付与"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()

            # 特定のオリジンに対してパーミッションを付与
            context.grant_permissions(
                ["geolocation"],
                origin="https://www.microsoft.com",
            )

            page = context.new_page()
            page.goto(TARGET_URL)

            state = page.evaluate(
                """async () => {
                    const result = await navigator.permissions.query(
                        { name: 'geolocation' }
                    );
                    return result.state;
                }"""
            )
            assert state == "granted"

            context.close()
            browser.close()

    def test_clear_permissions(self):
        """付与したパーミッションをすべてクリア"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()

            # パーミッションを付与してからクリア
            context.grant_permissions(["geolocation"])
            context.clear_permissions()

            page = context.new_page()
            page.goto(TARGET_URL)

            # クリア後はデフォルト状態（prompt）に戻る
            state = page.evaluate(
                """async () => {
                    const result = await navigator.permissions.query(
                        { name: 'geolocation' }
                    );
                    return result.state;
                }"""
            )
            assert state == "prompt"

            context.close()
            browser.close()


# ---------------------------------------------------------------------------
# 14. 複合エミュレーション（複数オプションの組み合わせ）
# ---------------------------------------------------------------------------
class TestCombinedEmulation:
    """複数のエミュレーション設定を組み合わせて使用"""

    def test_full_mobile_emulation(self):
        """モバイル環境をフルエミュレートする"""
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(
                viewport={"width": 390, "height": 844},
                device_scale_factor=3,
                is_mobile=True,
                has_touch=True,
                user_agent=(
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
                    "AppleWebKit/605.1.15"
                ),
                locale="ja-JP",
                timezone_id="Asia/Tokyo",
                color_scheme="dark",
                geolocation={"latitude": 35.6762, "longitude": 139.6503},
                permissions=["geolocation"],
            )
            page = context.new_page()
            page.goto(TARGET_URL)

            # 各設定が反映されていることを確認
            results = page.evaluate(
                """() => ({
                    width: window.innerWidth,
                    dpr: window.devicePixelRatio,
                    touch: navigator.maxTouchPoints > 0,
                    locale: navigator.language,
                    tzOffset: new Date().getTimezoneOffset(),
                    darkMode: window.matchMedia(
                        '(prefers-color-scheme: dark)'
                    ).matches,
                    ua: navigator.userAgent
                })"""
            )

            assert results["dpr"] == 3
            assert results["touch"] is True
            assert results["locale"] == "ja-JP"
            assert results["tzOffset"] == -540
            assert results["darkMode"] is True
            assert "iPhone" in results["ua"]

            context.close()
            browser.close()


def main():
    runner = TestRunner("test_14_emulation")
    test_classes = [
        TestDeviceEmulation,
        TestViewport,
        TestDeviceScaleFactor,
        TestMobileMode,
        TestTouchSupport,
        TestGeolocation,
        TestLocale,
        TestTimezone,
        TestColorScheme,
        TestUserAgent,
        TestOfflineMode,
        TestGeolocationChange,
        TestPermissions,
        TestCombinedEmulation,
    ]
    for cls in test_classes:
        obj = cls()
        for method_name in [m for m in dir(obj) if m.startswith("test_")]:
            method = getattr(obj, method_name)
            runner.run(method, skip_reason=SKIP_TESTS.get(method_name))
    sys.exit(runner.summary())


if __name__ == "__main__":
    main()
