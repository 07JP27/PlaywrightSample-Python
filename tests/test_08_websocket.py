"""
test_08_websocket.py - WebSocket 制御のサンプル

WebSocket のモック、メッセージ傍受、イベント監視を示す。
route_web_socket は Playwright v1.48+ で利用可能。
"""

import asyncio
import threading

import pytest
import websockets


# ---------------------------------------------------------------------------
# テスト用 WebSocket エコーサーバー（フィクスチャ）
# ---------------------------------------------------------------------------
@pytest.fixture()
def ws_server():
    """テスト用 WebSocket エコーサーバーを起動・終了するフィクスチャ"""

    async def echo(ws):
        async for message in ws:
            await ws.send(f"echo:{message}")

    port_holder: dict[str, int] = {}
    ready = threading.Event()
    stop = asyncio.Event()

    async def run():
        async with websockets.serve(echo, "localhost", 0) as server:
            port_holder["port"] = server.sockets[0].getsockname()[1]
            ready.set()
            await stop.wait()  # テスト終了まで待機

    loop = asyncio.new_event_loop()
    t = threading.Thread(target=loop.run_until_complete, args=(run(),), daemon=True)
    t.start()
    ready.wait(timeout=5)

    yield f"ws://localhost:{port_holder['port']}"

    loop.call_soon_threadsafe(stop.set)


def _setup_ws_page(page, *, html: str):
    """WebSocket ルーティングを有効にするためページを初期化してからコンテンツを設定"""
    page.goto("about:blank")
    page.set_content(html)


# ---------------------------------------------------------------------------
# 1. WebSocket モック (page.route_web_socket)
#    サーバーなしで WebSocket をシミュレートする
# ---------------------------------------------------------------------------
def test_websocket_mock(page):
    """WebSocket のモック - サーバーなしでシミュレート"""

    def ws_handler(ws):
        # クライアントからのメッセージを受信し、応答を返す
        def on_message(message):
            if message == "ping":
                ws.send("pong")

        ws.on_message(on_message)

    # wss://example.com/ws への接続をモックに差し替え
    page.route_web_socket("wss://example.com/ws", ws_handler)

    _setup_ws_page(page, html="""
        <script>
            const ws = new WebSocket("wss://example.com/ws");
            ws.onopen = () => ws.send("ping");
            ws.onmessage = (e) => document.title = e.data;
        </script>
    """)

    # モックが "pong" を返すまで待機
    page.wait_for_function("document.title === 'pong'")
    assert page.title() == "pong"


# ---------------------------------------------------------------------------
# 2. WebSocket メッセージの送受信モック
#    複数メッセージのやり取りをシミュレートする
# ---------------------------------------------------------------------------
def test_websocket_send_receive_mock(page):
    """複数メッセージの送受信をモックでシミュレート"""

    def ws_handler(ws):
        def on_message(message):
            # メッセージをエコーバックする
            ws.send(f"echo:{message}")

        ws.on_message(on_message)

    page.route_web_socket("wss://example.com/ws", ws_handler)

    _setup_ws_page(page, html="""
        <script>
            const received = [];
            const ws = new WebSocket("wss://example.com/ws");
            ws.onopen = () => {
                ws.send("hello");
                ws.send("world");
            };
            ws.onmessage = (e) => {
                received.push(e.data);
                // 受信したメッセージをカンマ区切りでタイトルに反映
                document.title = received.join(",");
            };
            window._received = received;
        </script>
    """)

    # 2 件のエコー応答が届くまで待機
    page.wait_for_function("window._received.length >= 2")

    received = page.evaluate("window._received")
    assert received == ["echo:hello", "echo:world"]


# ---------------------------------------------------------------------------
# 3. WebSocket イベント監視 (page.on("websocket"))
#    ページ上で発生する WebSocket 接続を検知する
# ---------------------------------------------------------------------------
def test_websocket_event_monitoring(page, ws_server):
    """page.on('websocket') で WebSocket 接続を監視"""

    ws_urls: list[str] = []

    # WebSocket 接続が開始されたら URL を記録
    page.on("websocket", lambda ws: ws_urls.append(ws.url))

    _setup_ws_page(page, html=f"""
        <script>
            const ws = new WebSocket("{ws_server}");
            ws.onopen = () => document.title = "connected";
        </script>
    """)

    # WebSocket 接続完了を待機
    page.wait_for_function("document.title === 'connected'")
    assert len(ws_urls) == 1
    assert ws_server in ws_urls[0]


# ---------------------------------------------------------------------------
# 4. WebSocket フレーム監視
#    ws.on("framereceived") / ws.on("framesent") でフレームを傍受する
# ---------------------------------------------------------------------------
def test_websocket_frame_monitoring(page, ws_server):
    """WebSocket フレームの送受信を監視"""

    sent_frames: list[str] = []
    received_frames: list[str] = []

    def on_websocket(ws):
        # 送信フレームを記録
        ws.on("framesent", lambda payload: sent_frames.append(payload))
        # 受信フレームを記録
        ws.on("framereceived", lambda payload: received_frames.append(payload))

    page.on("websocket", on_websocket)

    _setup_ws_page(page, html=f"""
        <script>
            const ws = new WebSocket("{ws_server}");
            ws.onopen = () => ws.send("frame_test");
            ws.onmessage = (e) => document.title = e.data;
        </script>
    """)

    # エコーサーバーの応答がタイトルに反映されるまで待機
    page.wait_for_function("document.title === 'echo:frame_test'")

    # 送信フレームの検証
    assert any("frame_test" in f for f in sent_frames), (
        f"送信フレームに 'frame_test' が見つからない: {sent_frames}"
    )

    # 受信フレームの検証
    assert any("echo:frame_test" in f for f in received_frames), (
        f"受信フレームに 'echo:frame_test' が見つからない: {received_frames}"
    )
