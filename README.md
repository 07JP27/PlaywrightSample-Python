# Playwright Python 全機能サンプル

Playwright for Python の全機能を網羅するサンプルプロジェクトです。  
24 カテゴリ・**403 テスト関数**で Playwright の API を体系的に学べます。

## セットアップ

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# ブラウザバイナリのインストール
playwright install
```

## テスト実行

```bash
# 全テスト実行
pytest

# 特定テストファイルの実行
pytest tests/test_01_browser_launch.py

# ヘッドフルモード（ブラウザ表示）
pytest --headed

# スローモーション付き
pytest --slowmo 500

# 特定ブラウザで実行
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit

# 全ブラウザで実行
pytest --browser chromium --browser firefox --browser webkit

# トレース記録付き
pytest --tracing on

# 動画記録付き
pytest --video on

# 失敗時のみスクリーンショット
pytest --screenshot only-on-failure

# HTML レポート生成
pytest --html=output/report.html --self-contained-html

# ベースURL指定
pytest --base-url https://www.microsoft.com
```

## プロジェクト構成

```
├── conftest.py                       # 共通フィクスチャ・設定
├── pages/                            # Page Object Model
│   ├── base_page.py                  # 基底ページクラス
│   └── microsoft_page.py            # Microsoft サイト用 POM
├── tests/                            # テストファイル（下記ガイド参照）
├── data/                             # テストデータ
└── output/                           # 出力先（スクリーンショット・動画等）
```

---

## 📖 機能別サンプルガイド

### 1. ブラウザ起動・管理

> 📄 [tests/test_01_browser_launch.py](tests/test_01_browser_launch.py) — 11 テスト  
> 🔗 [公式ドキュメント: BrowserType](https://playwright.dev/python/docs/api/class-browsertype)

Chromium / Firefox / WebKit の 3 エンジンの起動方法と各種オプション。

<details><summary>テスト一覧</summary>

- Chromium ブラウザを起動してページを開く
- Firefox ブラウザを起動してページを開く
- WebKit ブラウザを起動してページを開く
- ヘッドレスモード（GUI なし）でブラウザを起動する
- ヘッドフルモード（GUI あり）でブラウザを起動する
- slow_mo オプションで操作間に遅延を挿入する
- channel 指定でインストール済みの Google Chrome を使用する
- channel 指定でインストール済みの Microsoft Edge を使用する
- ブラウザ引数を指定して起動する
- ブラウザのバージョン情報を取得する
- ブラウザの接続状態を確認する

</details>

---

### 2. ブラウザコンテキスト

> 📄 [tests/test_02_browser_context.py](tests/test_02_browser_context.py) — 14 テスト  
> 🔗 [公式ドキュメント: BrowserContext](https://playwright.dev/python/docs/api/class-browsercontext)

独立したセッション（Cookie・ストレージの分離）の管理。

<details><summary>テスト一覧</summary>

- コンテキストを作成し、ページを開けることを確認
- 2 つのコンテキストが独立して動作することを確認
- Cookie を追加し、取得できることを確認
- clear_cookies で Cookie を削除できることを確認
- カスタムビューポートサイズを設定できることを確認
- デスクトップサイズのビューポートを確認
- http_credentials を設定したコンテキストを作成
- プロキシ設定を指定してコンテキストを作成
- geolocation パーミッションを許可
- 付与したパーミッションをクリア
- カスタムユーザーエージェントが反映されることを確認
- 一方のコンテキストに追加した Cookie が他方に見えないこと
- コンテキストをクローズするとページも閉じられること
- 一方のコンテキストを閉じても他方に影響しないこと

</details>

---

### 3. ページ操作の基本

> 📄 [tests/test_03_page_navigation.py](tests/test_03_page_navigation.py) — 21 テスト  
> 🔗 [公式ドキュメント: Page](https://playwright.dev/python/docs/api/class-page)

ナビゲーション、待機、プロパティ取得などの基本操作。

<details><summary>テスト一覧</summary>

- page.goto で指定 URL に遷移する
- page.goto の wait_until オプションで待機条件を指定する
- page.goto の timeout オプションでタイムアウトを指定する
- page.title() で現在のページタイトルを取得する
- page.url で現在のページ URL を取得する
- page.content() で HTML ソースを取得する
- page.go_back / page.go_forward で履歴を操作する
- page.go_back は Response オブジェクト（または None）を返す
- page.reload() でページをリロードする
- page.reload の wait_until オプションを指定する
- wait_for_load_state("load") で load イベントを待機する
- wait_for_load_state("domcontentloaded") で DOM 構築完了を待機する
- wait_for_load_state("networkidle") でネットワーク安定を待機する
- wait_for_url で特定の URL 文字列を待機する
- wait_for_url で正規表現パターンを使用する
- ナビゲーション後に wait_for_url で遷移先を確認する
- page.set_viewport_size でビューポートサイズを変更する
- モバイルサイズのビューポートに変更する
- タブレットサイズのビューポートに変更する
- page.close() でページを閉じる
- 複数ページを開いて個別に閉じる

</details>

---

### 4. ロケーター戦略

> 📄 [tests/test_04_locators.py](tests/test_04_locators.py) — 32 テスト  
> 🔗 [公式ドキュメント: Locators](https://playwright.dev/python/docs/locators)

get_by_role 等 14 種のロケーター戦略を網羅。推奨順位付き。

<details><summary>テスト一覧</summary>

- get_by_role - リンクロールで要素を検索
- get_by_role - 見出しロールで要素を検索
- get_by_role - ナビゲーションロールで要素を検索
- get_by_role - ボタンロールで要素を検索
- get_by_text - 部分一致でテキスト検索
- get_by_text - exact=True で完全一致検索
- get_by_text - 正規表現によるテキスト検索
- get_by_label - ラベルテキストによるフォーム要素検索
- get_by_label - チェックボックスをラベルで操作
- get_by_placeholder - プレースホルダーテキストで入力欄を検索
- get_by_placeholder - 部分一致でプレースホルダー検索
- get_by_alt_text - alt 属性テキストで画像を検索
- get_by_alt_text - 正規表現で alt 属性を検索
- get_by_title - title 属性テキストで要素を検索
- get_by_test_id - data-testid 属性で要素を検索
- locator - CSS クラスセレクタで要素を検索
- locator - CSS 属性セレクタで要素を検索
- locator - CSS :nth-child 擬似クラスで要素を検索
- locator - XPath 式で要素を検索
- locator - XPath の contains() でテキスト部分一致検索
- filter - has_text で特定テキストを含む要素に絞り込み
- filter - has で特定の子要素を持つ要素に絞り込み
- filter - 複数条件を連鎖して絞り込み
- nth - インデックス指定で N 番目の要素を取得
- first / last - 最初と最後の要素を取得
- nth - 負のインデックスで末尾から要素を取得
- チェーン - ロケーターを連鎖して子孫要素を絞り込み
- チェーン - locator と get_by_role を組み合わせる
- count - マッチした要素の数を取得
- count - 実サイトで要素数を確認
- all - 全マッチ要素をリストとして取得しループ処理
- all - all_inner_texts() で全要素のテキストを一括取得

</details>

---

### 5. ユーザーアクション・入力操作

> 📄 [tests/test_05_actions.py](tests/test_05_actions.py) — 44 テスト  
> 🔗 [公式ドキュメント: Actions](https://playwright.dev/python/docs/input)

クリック・入力・キーボード・マウス・ドラッグ＆ドロップなど全操作を網羅。

<details><summary>テスト一覧（抜粋）</summary>

- fill - テキスト入力 / textarea / 上書き
- press_sequentially - 一文字ずつ入力 / イベント検知
- clear - input / textarea のクリア
- click - ボタン / リンクのクリック
- dblclick - ダブルクリック
- click(button="right") - 右クリック
- click(modifiers=["Shift"]) - 修飾キー付きクリック
- click(position=...) - 座標指定クリック
- click(force=True) - 強制クリック
- hover - マウスオーバー / CSS :hover
- check / uncheck - チェックボックス / ラジオボタン
- set_checked - チェック状態の設定
- select_option - ドロップダウン選択（value / label / index / 複数）
- drag_to - ドラッグ＆ドロップ
- keyboard.press - Enter / Tab / Escape / Arrow
- keyboard.type - キーボード入力
- keyboard shortcuts - Ctrl+A / コピー&ペースト / Undo
- mouse - クリック / 移動 / down&up
- mouse.wheel - マウスホイールスクロール
- focus - フォーカス / フォーカスイベント
- scroll_into_view_if_needed - ビューポートスクロール

</details>

---

### 6. アサーション（expect）

> 📄 [tests/test_06_assertions.py](tests/test_06_assertions.py) — 27 テスト  
> 🔗 [公式ドキュメント: Assertions](https://playwright.dev/python/docs/test-assertions)

Playwright の Web-first アサーション全メソッドを網羅。自動リトライ付き。

<details><summary>テスト一覧</summary>

- to_have_title - ページタイトルの検証
- to_have_url - ページ URL の検証
- to_be_visible - 要素が表示されていることを検証
- to_be_hidden - 要素が非表示であることを検証
- to_be_attached - 要素が DOM にアタッチされていることを検証
- to_be_enabled / to_be_disabled - 有効・無効状態の検証
- to_be_editable - 編集可能であることを検証
- to_be_empty - 要素が空であることを検証
- to_be_focused - フォーカス状態の検証
- to_be_checked - チェック状態の検証
- to_be_in_viewport - ビューポート内にあることを検証
- to_have_text / to_contain_text - テキスト一致・部分一致
- to_have_value / to_have_values - 入力値の検証
- to_have_attribute - HTML 属性の検証
- to_have_class / to_contain_class - CSS クラスの検証
- to_have_css - CSS プロパティの検証
- to_have_id - id 属性の検証
- to_have_count - 要素数の検証
- to_have_js_property - JavaScript プロパティの検証
- to_have_accessible_name / to_have_accessible_description - ARIA 検証
- to_have_role - ARIA ロールの検証
- not_to_be_visible - 否定アサーション

</details>

---

### 7. ネットワーク制御

> 📄 [tests/test_07_network.py](tests/test_07_network.py) — 11 テスト  
> 🔗 [公式ドキュメント: Network](https://playwright.dev/python/docs/network)

リクエストの傍受・モック・修正・ブロック、HAR 記録。

<details><summary>テスト一覧</summary>

- route + fulfill でリクエストを傍受しモックレスポンスを返す
- route + continue_ でリクエストヘッダーを修正
- route + abort でリクエストをブロック（画像等）
- expect_response でレスポンスを待機
- expect_request でリクエストを待機
- page.on("request") / page.on("response") でイベント監視
- record_har_path で HAR ファイルを記録
- page.unroute でルートを解除
- context.route でコンテキストレベルのルーティング
- response.body / json / text でレスポンスボディ取得

</details>

---

### 8. WebSocket 制御

> 📄 [tests/test_08_websocket.py](tests/test_08_websocket.py) — 4 テスト  
> 🔗 [公式ドキュメント: WebSocketRoute](https://playwright.dev/python/docs/api/class-websocketroute)

WebSocket のモック、メッセージ傍受、イベント監視（v1.48+）。

<details><summary>テスト一覧</summary>

- route_web_socket でサーバーなしの WebSocket モック
- WebSocket メッセージの送受信モック
- page.on("websocket") でイベント監視
- framereceived / framesent でフレーム監視

</details>

---

### 9. ファイル操作

> 📄 [tests/test_09_file_operations.py](tests/test_09_file_operations.py) — 6 テスト  
> 🔗 [公式ドキュメント: Downloads](https://playwright.dev/python/docs/downloads)

ファイルのアップロード・ダウンロード操作。

<details><summary>テスト一覧</summary>

- set_input_files で input 要素経由のアップロード
- 複数ファイルの同時アップロード
- expect_file_chooser でファイルチューザー経由のアップロード
- set_input_files([]) でアップロード済みファイルのクリア
- expect_download でファイルダウンロード
- ダウンロードファイルの情報取得（suggested_filename, url）

</details>

---

### 10. ダイアログ処理

> 📄 [tests/test_10_dialogs.py](tests/test_10_dialogs.py) — 10 テスト  
> 🔗 [公式ドキュメント: Dialogs](https://playwright.dev/python/docs/dialogs)

alert / confirm / prompt のブラウザダイアログのハンドリング。

<details><summary>テスト一覧</summary>

- alert ダイアログの処理（accept）
- confirm ダイアログの承認（accept）
- confirm ダイアログの拒否（dismiss）
- prompt ダイアログへのテキスト入力
- ダイアログのプロパティ取得（type, message, default_value）
- page.once による一度きりのハンドラー

</details>

---

### 11. マルチページ・タブ・ポップアップ

> 📄 [tests/test_11_multi_page.py](tests/test_11_multi_page.py) — 9 テスト  
> 🔗 [公式ドキュメント: Pages](https://playwright.dev/python/docs/pages)

複数タブ・ポップアップウィンドウの操作。

<details><summary>テスト一覧</summary>

- context.new_page() で新しいタブを作成
- expect_popup でポップアップを捕捉
- context.expect_page で新ページイベントを監視
- context.pages で全ページを列挙
- page.bring_to_front() でタブを前面化
- window.open によるポップアップ

</details>

---

### 12. Frame / iframe 操作

> 📄 [tests/test_12_frames.py](tests/test_12_frames.py) — 14 テスト  
> 🔗 [公式ドキュメント: Frames](https://playwright.dev/python/docs/frames)

iframe 内要素の操作、frame_locator、ネストされた iframe。

<details><summary>テスト一覧</summary>

- frame_locator で iframe 内要素を操作（推奨）
- frame(name=...) で名前指定の Frame 取得
- frame(url=...) で URL 指定の Frame 取得
- page.frames で全フレーム列挙
- page.main_frame でメインフレーム取得
- ネストされた iframe の操作

</details>

---

### 13. Shadow DOM

> 📄 [tests/test_13_shadow_dom.py](tests/test_13_shadow_dom.py) — 13 テスト  
> 🔗 [公式ドキュメント: Locators (Shadow DOM)](https://playwright.dev/python/docs/locators#locate-in-shadow-dom)

Playwright の locator は Shadow DOM を自動貫通（pierce）する。

<details><summary>テスト一覧</summary>

- Shadow DOM 内の要素にアクセス
- Shadow DOM 内のテキスト取得
- Shadow DOM 内のクリック操作
- get_by_role で Shadow DOM 内の要素を操作

</details>

---

### 14. エミュレーション

> 📄 [tests/test_14_emulation.py](tests/test_14_emulation.py) — 34 テスト  
> 🔗 [公式ドキュメント: Emulation](https://playwright.dev/python/docs/emulation)

デバイス・位置情報・ロケール・タイムゾーン・カラースキーム等の環境エミュレーション。

<details><summary>テスト一覧（抜粋）</summary>

- iPhone 13 / Pixel 5 / iPad のデバイスエミュレーション
- モバイル / デスクトップ / カスタムビューポート
- Retina / High-DPI ディスプレイ
- モバイルモード / タッチサポート
- ジオロケーション（東京 / ニューヨーク）
- ロケール設定（ja-JP / en-US 等）
- タイムゾーン設定（Asia/Tokyo 等）
- カラースキーム（dark / light）
- ユーザーエージェント設定
- オフラインモード
- パーミッション操作

</details>

---

### 15. 認証・ストレージ状態

> 📄 [tests/test_15_auth_storage.py](tests/test_15_auth_storage.py) — 12 テスト  
> 🔗 [公式ドキュメント: Authentication](https://playwright.dev/python/docs/auth)

Cookie / localStorage の保存・復元でログイン状態を共有。

<details><summary>テスト一覧</summary>

- add_cookies で Cookie を設定
- storage_state(path=...) でストレージ状態を保存
- new_context(storage_state=...) でストレージ状態を復元
- add_init_script で localStorage を操作
- context.cookies() で Cookie を取得・確認
- context.clear_cookies() で Cookie をクリア

</details>

---

### 16. スクリーンショット・動画・PDF

> 📄 [tests/test_16_screenshots_video.py](tests/test_16_screenshots_video.py) — 8 テスト  
> 🔗 [公式ドキュメント: Screenshots](https://playwright.dev/python/docs/screenshots)

ページキャプチャ、テスト録画、PDF 出力。

<details><summary>テスト一覧</summary>

- page.screenshot() でページスクリーンショット
- full_page=True でフルページスクリーンショット
- locator.screenshot() で要素スクリーンショット
- clip={...} で領域指定スクリーンショット
- type="jpeg" / quality でフォーマット・品質指定
- record_video_dir で動画記録
- record_video_size で動画サイズ指定
- page.pdf() で PDF 生成（Chromium + headless のみ）

</details>

---

### 17. トレーシング

> 📄 [tests/test_17_tracing.py](tests/test_17_tracing.py) — 6 テスト  
> 🔗 [公式ドキュメント: Trace Viewer](https://playwright.dev/python/docs/trace-viewer-intro)

テスト実行のトレース記録。`playwright show-trace trace.zip` で分析可能。

<details><summary>テスト一覧</summary>

- context.tracing.start / stop でトレース記録
- screenshots=True でスクリーンショット付きトレース
- snapshots=True で DOM スナップショット付きトレース
- sources=True でソースコード付きトレース
- start_chunk / stop_chunk でチャンク分割

</details>

---

### 18. ビジュアルリグレッション

> 📄 [tests/test_18_visual_regression.py](tests/test_18_visual_regression.py) — 7 テスト  
> 🔗 [公式ドキュメント: Visual Comparisons](https://playwright.dev/python/docs/test-snapshots)

スクリーンショットベースの視覚比較テスト。ベースライン更新: `pytest --update-snapshots`

<details><summary>テスト一覧</summary>

- expect(page).to_have_screenshot() でページ比較
- expect(locator).to_have_screenshot() で要素比較
- full_page=True でフルページ比較
- max_diff_pixels で差分許容値を設定
- スクリーンショット名の指定

</details>

---

### 19. Clock（時刻制御）

> 📄 [tests/test_19_clock.py](tests/test_19_clock.py) — 9 テスト  
> 🔗 [公式ドキュメント: Clock](https://playwright.dev/python/docs/clock)

ブラウザ内の時刻関数をフェイクタイマーで制御。

<details><summary>テスト一覧</summary>

- page.clock.install() でフェイクタイマーをインストール
- page.clock.set_fixed_time() で固定時刻を設定
- page.clock.fast_forward() で時間を早送り
- page.clock.pause_at() で特定時刻で一時停止
- page.clock.resume() で時間を再開
- page.clock.run_for() で指定時間分実行

</details>

---

### 20. API テスト

> 📄 [tests/test_20_api_testing.py](tests/test_20_api_testing.py) — 23 テスト  
> 🔗 [公式ドキュメント: API Testing](https://playwright.dev/python/docs/api-testing)

ブラウザを使わずに REST API を直接テスト。

<details><summary>テスト一覧（抜粋）</summary>

- GET / POST / PUT / PATCH / DELETE リクエスト
- レスポンスステータスの検証（ok, status）
- レスポンスボディの取得（json, text）
- カスタムヘッダー（extra_http_headers）
- APIRequestContext の作成と破棄
- expect(response).to_be_ok() による API レスポンスアサーション

</details>

---

### 21. アクセシビリティテスト

> 📄 [tests/test_21_accessibility.py](tests/test_21_accessibility.py) — 25 テスト  
> 🔗 [公式ドキュメント: Accessibility Testing](https://playwright.dev/python/docs/accessibility-testing)

ARIA ロール・アクセシブル名・説明の検証、アクセシビリティスナップショット。

<details><summary>テスト一覧（抜粋）</summary>

- page.accessibility.snapshot() でアクセシビリティスナップショット取得
- get_by_role で ARIA ロールベースの要素検証
- to_have_accessible_name でアクセシブル名の検証
- to_have_accessible_description でアクセシブル説明の検証
- to_have_role で ARIA ロールの検証
- キーボードナビゲーションの確認

</details>

---

### 22. JavaScript 実行・評価

> 📄 [tests/test_22_js_evaluation.py](tests/test_22_js_evaluation.py) — 25 テスト  
> 🔗 [公式ドキュメント: Evaluating JavaScript](https://playwright.dev/python/docs/evaluating)

ブラウザコンテキストでの JavaScript 実行、関数公開、イベント監視。

<details><summary>テスト一覧（抜粋）</summary>

- page.evaluate() で JavaScript 式を評価
- 引数付き evaluate
- evaluate_handle で JSHandle を取得
- locator.evaluate() で要素上の JavaScript 実行
- page.expose_function() で Python 関数をページに公開
- page.on("console") でコンソールメッセージ監視
- page.on("pageerror") でページエラー監視
- context.add_init_script() で初期化スクリプト
- evaluate_all で全マッチ要素への評価

</details>

---

### 23. 高度な接続・設定

> 📄 [tests/test_23_advanced_config.py](tests/test_23_advanced_config.py) — 5 テスト  
> 🔗 [公式ドキュメント: BrowserType](https://playwright.dev/python/docs/api/class-browsertype)

永続コンテキスト、CDP 接続、CDPSession による低レベル操作。

<details><summary>テスト一覧</summary>

- launch_persistent_context でセッションデータを保持
- connect_over_cdp で既存 Chrome に接続（※要外部ブラウザ）
- CDPSession で Performance メトリクスを取得
- CDPSession でネットワーク条件をエミュレーション（Slow 3G）
- ブラウザ起動オプションの説明

</details>

---

### 24. 非同期 API（async/await）

> 📄 [tests/test_24_async_api.py](tests/test_24_async_api.py) — 33 テスト  
> 🔗 [公式ドキュメント: Library (async)](https://playwright.dev/python/docs/library)

同期 API と同等の操作を async/await で記述するサンプル。

<details><summary>テスト一覧（抜粋）</summary>

- 非同期でのブラウザ起動とページ遷移
- 非同期でのロケーター操作
- 非同期でのアサーション
- 非同期でのネットワーク傍受
- 非同期でのスクリーンショット
- 非同期での JavaScript 評価

</details>
