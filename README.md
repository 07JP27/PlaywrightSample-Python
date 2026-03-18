# Playwright Python 全機能サンプル

Playwright for Python の全機能を網羅するサンプルプロジェクトです。  
24 カテゴリ・**402 テスト関数**で Playwright の API を体系的に学べます。  
さらに、業務システムを想定した **6 つの E2E シナリオテスト（37 テスト関数）** も収録しています。

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

# 機能別サンプルの実行
pytest tests/features/

# E2Eシナリオテストの実行
pytest tests/scenarios/

# 特定テストファイルの実行
pytest tests/features/test_01_browser_launch.py

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
│   ├── microsoft_page.py            # Microsoft サイト用 POM
│   ├── saucedemo/                   # SauceDemo（EC）用 POM
│   ├── orangehrm/                   # OrangeHRM（HR）用 POM
│   ├── the_internet/                # The Internet 用 POM
│   ├── demoqa/                      # DemoQA 用 POM
│   └── google/                      # Google 検索用 POM
├── tests/
│   ├── features/                    # 機能別サンプル（test_01〜24）
│   └── scenarios/                   # E2E シナリオテスト
│       ├── conftest.py              # シナリオ用フィクスチャ
│       ├── test_e2e_ec_purchase.py   # EC 購買フロー
│       ├── test_e2e_hr_management.py # HR 勤怠管理フロー
│       ├── test_e2e_portal_auth.py   # ポータル認証フロー
│       ├── test_e2e_application_form.py # 申請ワークフロー
│       ├── test_e2e_cross_system.py  # API+UI 複合シナリオ
│       └── test_e2e_google_search.py # Google 検索フロー
├── data/
│   ├── upload_sample.txt            # アップロード用サンプル
│   └── scenarios/                   # シナリオ用テストデータ
└── output/                           # 出力先（スクリーンショット・動画等）
```

### テストの種類

本プロジェクトには 2 種類のテストがあります。

| | 機能別サンプル (`tests/features/`) | E2E シナリオ (`tests/scenarios/`) |
|---|---|---|
| **目的** | Playwright API の各機能を個別に学ぶ | 実際の業務フローを通しで検証する |
| **テスト数** | 402 テスト（24 ファイル） | 37 テスト（6 ファイル） |
| **対象** | ブラウザ操作・ロケーター・アサーション等 | EC購買・HR管理・認証・申請・API連携 |
| **パターン** | 単機能デモ（`set_content` やシンプルな外部サイト） | Page Object Model + テストデータ駆動 |
| **エビデンス** | なし | 全画面スクリーンショット + HTMLレポート自動生成 |

---

## 📖 機能別サンプルガイド

### 1. ブラウザ起動・管理

> 📄 [tests/features/test_01_browser_launch.py](tests/features/test_01_browser_launch.py) — 11 テスト  
> 🔗 [公式ドキュメント: BrowserType](https://playwright.dev/python/docs/api/class-browsertype)

「ブラウザをコードから起動したい」「headless / headed を切り替えたい」「Chrome や Edge の安定版を使いたい」ときに参照。Chromium / Firefox / WebKit の 3 エンジン起動、slow_mo、channel 指定、ブラウザ引数などを扱う。

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

> 📄 [tests/features/test_02_browser_context.py](tests/features/test_02_browser_context.py) — 14 テスト  
> 🔗 [公式ドキュメント: BrowserContext](https://playwright.dev/python/docs/api/class-browsercontext)

「複数ユーザーを同時にシミュレートしたい」「Cookie やストレージをテスト間で分離したい」「Proxy や Basic 認証を設定したい」ときに参照。コンテキストの作成・分離・Cookie 操作・パーミッション制御を扱う。

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

> 📄 [tests/features/test_03_page_navigation.py](tests/features/test_03_page_navigation.py) — 21 テスト  
> 🔗 [公式ドキュメント: Page](https://playwright.dev/python/docs/api/class-page)

「ページ遷移したい」「戻る・進む・リロードしたい」「ページの読み込み完了を待ちたい」ときに参照。goto / go_back / reload / wait_for_load_state / wait_for_url / set_viewport_size など基本的なページ操作を扱う。

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

> 📄 [tests/features/test_04_locators.py](tests/features/test_04_locators.py) — 32 テスト  
> 🔗 [公式ドキュメント: Locators](https://playwright.dev/python/docs/locators)

「ページ上の要素をどうやって見つけるか？」の全パターン集。get_by_role（推奨）/ get_by_text / get_by_label / get_by_test_id / CSS / XPath の使い分けと、filter・nth・チェーンによる絞り込みテクニックを扱う。

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

> 📄 [tests/features/test_05_actions.py](tests/features/test_05_actions.py) — 44 テスト  
> 🔗 [公式ドキュメント: Actions](https://playwright.dev/python/docs/input)

「フォームに入力したい」「ボタンをクリックしたい」「ドラッグ＆ドロップしたい」「キーボードショートカットを送りたい」ときに参照。fill / click / hover / check / select_option / drag_to / keyboard / mouse 等ブラウザ上のユーザー操作を全網羅。

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

> 📄 [tests/features/test_06_assertions.py](tests/features/test_06_assertions.py) — 27 テスト  
> 🔗 [公式ドキュメント: Assertions](https://playwright.dev/python/docs/test-assertions)

「要素が表示されているか検証したい」「テキスト・属性・URL・タイトルを検証したい」ときに参照。expect() の全メソッド（to_be_visible / to_have_text / to_have_url 等 27 種）を網羅。自動リトライ付きでフレーキーテストを防ぐ。

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

> 📄 [tests/features/test_07_network.py](tests/features/test_07_network.py) — 11 テスト  
> 🔗 [公式ドキュメント: Network](https://playwright.dev/python/docs/network)

「API レスポンスをモックしたい」「リクエストヘッダーを書き換えたい」「画像や広告をブロックしたい」「通信内容を HAR に記録したい」ときに参照。route / fulfill / continue_ / abort によるネットワークレベルの制御を扱う。

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

> 📄 [tests/features/test_08_websocket.py](tests/features/test_08_websocket.py) — 4 テスト  
> 🔗 [公式ドキュメント: WebSocketRoute](https://playwright.dev/python/docs/api/class-websocketroute)

「WebSocket 通信をモックしたい」「リアルタイム通信のメッセージを傍受・検証したい」ときに参照。route_web_socket によるサーバーなしモック、framereceived / framesent イベント監視を扱う（v1.48+）。

<details><summary>テスト一覧</summary>

- route_web_socket でサーバーなしの WebSocket モック
- WebSocket メッセージの送受信モック
- page.on("websocket") でイベント監視
- framereceived / framesent でフレーム監視

</details>

---

### 9. ファイル操作

> 📄 [tests/features/test_09_file_operations.py](tests/features/test_09_file_operations.py) — 6 テスト  
> 🔗 [公式ドキュメント: Downloads](https://playwright.dev/python/docs/downloads)

「ファイルアップロードフォームをテストしたい」「ダウンロード処理を検証したい」ときに参照。set_input_files / expect_file_chooser によるアップロードと、expect_download によるダウンロード捕捉・保存を扱う。

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

> 📄 [tests/features/test_10_dialogs.py](tests/features/test_10_dialogs.py) — 10 テスト  
> 🔗 [公式ドキュメント: Dialogs](https://playwright.dev/python/docs/dialogs)

「alert / confirm / prompt のダイアログを自動で処理したい」ときに参照。page.on("dialog") でハンドラーを登録し、accept / dismiss / テキスト入力を行う方法を扱う。ハンドラーはアクション実行前に登録が必要。

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

> 📄 [tests/features/test_11_multi_page.py](tests/features/test_11_multi_page.py) — 9 テスト  
> 🔗 [公式ドキュメント: Pages](https://playwright.dev/python/docs/pages)

「target="_blank" で開く新しいタブを捕捉したい」「window.open のポップアップを制御したい」「開いている全タブを列挙したい」ときに参照。expect_popup / expect_page / bring_to_front などマルチタブ操作を扱う。

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

> 📄 [tests/features/test_12_frames.py](tests/features/test_12_frames.py) — 14 テスト  
> 🔗 [公式ドキュメント: Frames](https://playwright.dev/python/docs/frames)

「iframe の中にある要素を操作したい」「ネストされた iframe を扱いたい」ときに参照。frame_locator（推奨）/ frame(name=) / frame(url=) による iframe 内要素のアクセスと操作を扱う。

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

> 📄 [tests/features/test_13_shadow_dom.py](tests/features/test_13_shadow_dom.py) — 13 テスト  
> 🔗 [公式ドキュメント: Locators (Shadow DOM)](https://playwright.dev/python/docs/locators#locate-in-shadow-dom)

「Web Components の Shadow DOM 内にある要素を操作したい」ときに参照。Playwright の locator は Shadow DOM を自動貫通（pierce）するため、通常と同じセレクタで操作できることを示す。

<details><summary>テスト一覧</summary>

- Shadow DOM 内の要素にアクセス
- Shadow DOM 内のテキスト取得
- Shadow DOM 内のクリック操作
- get_by_role で Shadow DOM 内の要素を操作

</details>

---

### 14. エミュレーション

> 📄 [tests/features/test_14_emulation.py](tests/features/test_14_emulation.py) — 34 テスト  
> 🔗 [公式ドキュメント: Emulation](https://playwright.dev/python/docs/emulation)

「iPhone や Android でどう見えるかテストしたい」「位置情報・言語・タイムゾーン・ダークモードを切り替えたい」ときに参照。p.devices によるデバイスプリセット、geolocation / locale / timezone_id / color_scheme / offline 等の環境エミュレーションを扱う。

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

> 📄 [tests/features/test_15_auth_storage.py](tests/features/test_15_auth_storage.py) — 12 テスト  
> 🔗 [公式ドキュメント: Authentication](https://playwright.dev/python/docs/auth)

「ログイン状態を保存して複数テストで再利用したい」「テストごとに異なるユーザーで実行したい」ときに参照。storage_state の保存・復元で認証フローを毎回スキップし、テスト実行を高速化する方法を扱う。

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

> 📄 [tests/features/test_16_screenshots_video.py](tests/features/test_16_screenshots_video.py) — 8 テスト  
> 🔗 [公式ドキュメント: Screenshots](https://playwright.dev/python/docs/screenshots)

「テスト実行中のスクリーンショットを撮りたい」「テストを動画で録画したい」「ページを PDF に出力したい」ときに参照。ページ全体・要素・領域指定のスクリーンショット、動画記録、PDF 生成（Chromium + headless のみ）を扱う。

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

> 📄 [tests/features/test_17_tracing.py](tests/features/test_17_tracing.py) — 6 テスト  
> 🔗 [公式ドキュメント: Trace Viewer](https://playwright.dev/python/docs/trace-viewer-intro)

「テスト失敗の原因を詳しく調べたい」「操作の各ステップを後から再現したい」ときに参照。スクリーンショット・DOM スナップショット・ネットワークログを含むトレースを記録し、`playwright show-trace trace.zip` で可視化する方法を扱う。

<details><summary>テスト一覧</summary>

- context.tracing.start / stop でトレース記録
- screenshots=True でスクリーンショット付きトレース
- snapshots=True で DOM スナップショット付きトレース
- sources=True でソースコード付きトレース
- start_chunk / stop_chunk でチャンク分割

</details>

---

### 18. ビジュアルリグレッション

> 📄 [tests/features/test_18_visual_regression.py](tests/features/test_18_visual_regression.py) — 7 テスト  
> 🔗 [公式ドキュメント: Visual Comparisons](https://playwright.dev/python/docs/test-snapshots)

「UI の見た目が意図せず変わっていないか検知したい」ときに参照。expect(page).to_have_screenshot() でベースライン画像と比較し、ピクセル差分を自動検出する。ベースライン更新は `pytest --update-snapshots`。

<details><summary>テスト一覧</summary>

- expect(page).to_have_screenshot() でページ比較
- expect(locator).to_have_screenshot() で要素比較
- full_page=True でフルページ比較
- max_diff_pixels で差分許容値を設定
- スクリーンショット名の指定

</details>

---

### 19. Clock（時刻制御）

> 📄 [tests/features/test_19_clock.py](tests/features/test_19_clock.py) — 9 テスト  
> 🔗 [公式ドキュメント: Clock](https://playwright.dev/python/docs/clock)

「setTimeout / setInterval / Date に依存する機能をテストしたい」「5秒待つ処理を即座に完了させたい」ときに参照。page.clock でフェイクタイマーをインストールし、時間の固定・早送り・一時停止を行う方法を扱う。

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

> 📄 [tests/features/test_20_api_testing.py](tests/features/test_20_api_testing.py) — 23 テスト  
> 🔗 [公式ドキュメント: API Testing](https://playwright.dev/python/docs/api-testing)

「ブラウザを起動せずに REST API のエンドポイントをテストしたい」「E2E テスト内でバックエンドのデータを準備・検証したい」ときに参照。playwright.request による GET / POST / PUT / DELETE とレスポンス検証を扱う。

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

> 📄 [tests/features/test_21_accessibility.py](tests/features/test_21_accessibility.py) — 25 テスト  
> 🔗 [公式ドキュメント: Accessibility Testing](https://playwright.dev/python/docs/accessibility-testing)

「Web アクセシビリティの品質を自動検証したい」「スクリーンリーダーにどう認識されるか確認したい」ときに参照。ARIA ロール・アクセシブル名・説明のアサーション、アクセシビリティスナップショット、キーボードナビゲーション確認を扱う。

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

> 📄 [tests/features/test_22_js_evaluation.py](tests/features/test_22_js_evaluation.py) — 25 テスト  
> 🔗 [公式ドキュメント: Evaluating JavaScript](https://playwright.dev/python/docs/evaluating)

「ページ内で JavaScript を実行して値を取得したい」「Python 関数をブラウザ側から呼び出したい」「console.log やエラーを捕捉したい」ときに参照。evaluate / expose_function / on("console") / add_init_script を扱う。

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

> 📄 [tests/features/test_23_advanced_config.py](tests/features/test_23_advanced_config.py) — 5 テスト  
> 🔗 [公式ドキュメント: BrowserType](https://playwright.dev/python/docs/api/class-browsertype)

「ユーザープロファイルを保持したままテストしたい」「既に起動している Chrome に接続したい」「DevTools Protocol で低レベル操作したい」ときに参照。launch_persistent_context / connect_over_cdp / CDPSession を扱う。

<details><summary>テスト一覧</summary>

- launch_persistent_context でセッションデータを保持
- connect_over_cdp で既存 Chrome に接続（※要外部ブラウザ）
- CDPSession で Performance メトリクスを取得
- CDPSession でネットワーク条件をエミュレーション（Slow 3G）
- ブラウザ起動オプションの説明

</details>

---

### 24. 非同期 API（async/await）

> 📄 [tests/features/test_24_async_api.py](tests/features/test_24_async_api.py) — 33 テスト  
> 🔗 [公式ドキュメント: Library (async)](https://playwright.dev/python/docs/library)

「async/await で非同期にブラウザを操作したい」「イベントループベースのアプリと統合したい」ときに参照。同期 API（sync_api）と同等の操作を非同期 API（async_api）で記述した対比サンプル集。

<details><summary>テスト一覧（抜粋）</summary>

- 非同期でのブラウザ起動とページ遷移
- 非同期でのロケーター操作
- 非同期でのアサーション
- 非同期でのネットワーク傍受
- 非同期でのスクリーンショット
- 非同期での JavaScript 評価

</details>

---

## 🏢 E2E シナリオテストガイド

業務システムを想定した、実践的な E2E テストシナリオ集です。  
パブリックなデモサイトを使用し、Page Object Model パターンで構成されています。

```bash
# 全シナリオ実行
pytest tests/scenarios/

# 特定シナリオの実行
pytest tests/scenarios/test_e2e_ec_purchase.py

# ヘッドフルモードで実行（デバッグ向け）
pytest tests/scenarios/ --headed --slowmo 500
```

#### 📋 エビデンスレポート

全シナリオテストは各画面遷移でスクリーンショットを自動記録し、テスト完了後にHTMLエビデンスレポートを生成します。

```bash
# テスト実行後、以下にレポートが生成される
output/evidence/evidence_report.html      # 全テスト統合レポート
output/evidence/{テスト名}/01_xxx.png     # 各ステップのスクリーンショット
```

テスト内で `evidence.capture("ステップ名")` を呼ぶことで、連番付きスクリーンショットが保存されます。

### S1. EC 購買フロー

> 📄 [tests/scenarios/test_e2e_ec_purchase.py](tests/scenarios/test_e2e_ec_purchase.py) — 8 テスト  
> 🌐 対象サイト: [SauceDemo](https://www.saucedemo.com/)

EC サイトでの購買業務フロー。ログイン → 商品閲覧・ソート → カート追加 → チェックアウト → 注文完了。異常系（ロックアウトユーザー、バリデーションエラー）も網羅。

<details><summary>テスト一覧</summary>

- `test_login_and_view_products` — ログイン → 商品一覧表示確認
- `test_sort_products_by_price` — 商品ソート（価格安い順・高い順）
- `test_add_multiple_products_to_cart` — 複数商品カート追加
- `test_remove_product_from_cart` — カートから商品削除
- `test_complete_purchase_flow` — **購買フロー完走（メインシナリオ）**
- `test_checkout_validation_error` — チェックアウトバリデーションエラー
- `test_locked_out_user_cannot_login` — ロックアウトユーザーの拒否
- `test_continue_shopping_from_cart` — カートから買い物続行

</details>

---

### S2. HR 勤怠管理フロー

> 📄 [tests/scenarios/test_e2e_hr_management.py](tests/scenarios/test_e2e_hr_management.py) — 6 テスト  
> 🌐 対象サイト: [OrangeHRM Demo](https://opensource-demo.orangehrmlive.com/)

人事管理システムでの日常業務。管理者ログイン → ダッシュボード確認 → PIM（従業員管理）遷移 → 従業員検索 → メニュー遷移 → ログアウト。

<details><summary>テスト一覧</summary>

- `test_admin_login_and_dashboard` — 管理者ログイン → ダッシュボード表示確認
- `test_navigate_to_pim_module` — PIM（人事管理）モジュールへの遷移
- `test_search_employee` — 従業員検索
- `test_dashboard_menu_navigation` — サイドメニュー各項目への遷移確認
- `test_login_logout_cycle` — ログイン → ログアウト → 再ログイン
- `test_invalid_login_attempt` — 不正ログイン試行

</details>

---

### S3. ポータル認証・フォーム操作フロー

> 📄 [tests/scenarios/test_e2e_portal_auth.py](tests/scenarios/test_e2e_portal_auth.py) — 7 テスト  
> 🌐 対象サイト: [The Internet](https://the-internet.herokuapp.com/)

社内ポータルの認証フローとフォーム操作。ログイン/ログアウト → チェックボックス → ドロップダウン → ファイルアップロード。

<details><summary>テスト一覧</summary>

- `test_login_success` — 正常ログイン
- `test_login_failure` — ログイン失敗
- `test_login_logout_relogin_cycle` — ログイン → ログアウト → 再ログイン
- `test_checkbox_operations` — チェックボックス操作
- `test_dropdown_selection` — ドロップダウン選択
- `test_file_upload` — ファイルアップロード
- `test_complete_portal_workflow` — **統合ポータルワークフロー（メインシナリオ）**

</details>

---

### S4. 申請ワークフロー

> 📄 [tests/scenarios/test_e2e_application_form.py](tests/scenarios/test_e2e_application_form.py) — 7 テスト  
> 🌐 対象サイト: [DemoQA](https://demoqa.com/)

申請書フォーム入力と管理テーブル操作。フォーム送信 → バリデーション確認 → テーブル CRUD（追加・検索・編集・削除）。

<details><summary>テスト一覧</summary>

- `test_submit_practice_form` — 申請フォーム送信
- `test_form_required_fields_validation` — 必須フィールドバリデーション
- `test_web_table_add_record` — テーブルへのレコード追加
- `test_web_table_search` — テーブル検索
- `test_web_table_edit_record` — テーブルレコード編集
- `test_web_table_delete_record` — テーブルレコード削除
- `test_complete_application_workflow` — **統合申請ワークフロー（メインシナリオ）**

</details>

---

### S5. API + UI 複合シナリオ

> 📄 [tests/scenarios/test_e2e_cross_system.py](tests/scenarios/test_e2e_cross_system.py) — 6 テスト  
> 🌐 対象サイト: [httpbin.org](https://httpbin.org/) + [SauceDemo](https://www.saucedemo.com/)

システム間連携パターン。API でのデータ準備/検証と UI 操作を組み合わせた統合テスト。承認ワークフローの模擬も含む。

<details><summary>テスト一覧</summary>

- `test_api_health_check_then_ui_flow` — API 疎通確認 → UI 操作
- `test_api_data_preparation_for_ui_verification` — API データ準備 → UI 検証
- `test_api_mock_workflow_approval` — API 承認ワークフロー模擬
- `test_parallel_api_and_ui_operations` — API/UI 並行操作
- `test_api_response_headers_verification` — API レスポンスヘッダー検証
- `test_end_to_end_with_api_validation` — **エンドツーエンド統合テスト（メインシナリオ）**

</details>

---

### S6. Google 検索フロー

> 📄 [tests/scenarios/test_e2e_google_search.py](tests/scenarios/test_e2e_google_search.py) — 3 テスト  
> 🌐 対象サイト: [Google](https://www.google.com/)

シンプルな検索シナリオ。Google トップページにアクセス → 「microsoft」を検索 → 結果の表示確認。各ステップでエビデンスを取得する。

> ⚠️ Google は bot 検知が厳しいため `--headed` モードでの実行を推奨

<details><summary>テスト一覧</summary>

- `test_google_page_title` — Google トップページのタイトル確認
- `test_search_microsoft_and_view_results` — **Microsoft 検索→結果確認（メインシナリオ）**
- `test_search_box_is_visible` — 検索ボックスの表示確認

</details>
