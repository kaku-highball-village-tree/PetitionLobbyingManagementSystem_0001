# 画像DnDテキスト化 仕様整理（実装前）

## 1. スコープ

本書は **実装前の仕様整理** を目的とし、以下2ファイルに対する実装方針を定義する。

- 新規作成対象: `src/PetitionLobbyingImageToTextfile_Cmd.py`
- 修正対象: `src/PetitionLobbyingManagementSystem_DnD.py`

> 注意: この時点では実装しない。設計のみを確定する。

---

## 2. 目的

DnDウインドウに画像ファイルがドロップされた際、ChatGPTで画像内容をテキスト化し、同一フォルダーへ `.txt` を保存する。

処理フロー:

1. 画像ファイルを受け取る
2. ChatGPTへ送信してテキスト化
3. 同じ場所に `.txt` 保存

---

## 3. 参考コードの踏襲・非踏襲

参考: `src/scan_output_monitor.py`

### 3.1 踏襲する考え方

- 暗号化ファイルからOpenAI APIキーを復号して読み込む
- 画像のbase64化
- `client.responses.create()` の利用
- 応答テキスト抽出ロジック（`extract_response_text()` 相当）
- Windows向け文字扱い・最小限ログ

### 3.2 今回使わない要素

監視型・バッチ型に関する以下は非採用:

- `WATCH_DIR`
- `POLL_INTERVAL_SECONDS`
- `STABLE_REQUIRED_COUNT`
- `BATCH_TIMEOUT_SECONDS`
- `Batch` クラス
- `run_monitor()`
- 新規ファイル監視
- 20秒待機
- バッチ終了判定
- コピー確認ダイアログ
- フォルダー作成
- スキャンファイルコピー
- ファイル名提案

---

## 4. 新規CLI仕様（`PetitionLobbyingImageToTextfile_Cmd.py`）

### 4.1 実行形式

```bash
python PetitionLobbyingImageToTextfile_Cmd.py "C:\Data\相談メモ.jpg"
```

引数は画像パス1件のみ。

### 4.2 処理手順

1. 引数確認
2. ファイル存在確認
3. 拡張子確認（画像のみ）
4. APIキー読込
5. 画像base64化
6. ChatGPTへ画像テキスト化依頼
7. 応答テキスト抽出
8. 同フォルダーに `.txt` 保存
9. 成功時: 出力先パスを `stdout` に `print`
10. 失敗時: `_error.txt` 作成 + `stderr` 出力 + 非0終了

### 4.3 対応拡張子

現段階の対象:

- `.jpg`
- `.jpeg`
- `.png`

将来拡張候補（現時点は未対応）:

- `.webp`
- `.bmp`
- `.tif`
- `.tiff`

### 4.4 PDF

- **対象外**（将来対応）

### 4.5 出力ファイル命名

入力 `相談メモ_0001.jpg` の場合:

- 通常: `相談メモ_0001.txt`
- 既存時: `相談メモ_0001_1.txt`, `相談メモ_0001_2.txt` ...

### 4.6 エラーファイル命名

入力 `相談メモ_0001.jpg` の場合:

- エラー: `相談メモ_0001_error.txt`

### 4.7 文字コード

- エンコーディング: UTF-8
- 改行: CRLF（`\r\n` 推奨）

---

## 5. ChatGPTプロンプト方針

依頼内容（要点）:

- 画像内の文字を優先して正確にテキスト化
- 市民相談・陳情・請願・相談メモの検索用途（grep前提）
- 項目名やレイアウト上の意味は整理して出力
- 過剰推測は禁止
- 判読不能は `[判読不能]`
- ファイル名案・タイトル案は不要
- 出力は本文テキストのみ

モデル:

- 既定: `gpt-4o-mini`
- 将来: 上位モデルへ差し替え可能な設計

---

## 6. APIキー読込仕様

`scan_output_monitor.py` と同方式を採用:

- `./key/secret_key.bin`
- `./ciphertext/encrypted_key.bin`

`PetitionLobbyingImageToTextfile_Cmd.py` から見たスクリプト相対パスで解決する。

---

## 7. DnD側仕様（`PetitionLobbyingManagementSystem_DnD.py`）

### 7.1 拡張子分岐

- `.xlsx` → `PetitionLobbyingManagementSystem_Cmd.py` を実行
- `.jpg/.jpeg/.png` → `PetitionLobbyingImageToTextfile_Cmd.py` を実行
- その他 → `MessageBox` でエラー

### 7.2 UI表示文言

DnDウインドウに以下説明を表示:

- 「相談データExcel(.xlsx) または 相談メモ画像(.jpg/.jpeg/.png) をこのウインドウへドラッグ＆ドロップしてください。」
- 「Excelの場合: TSV/TXTを生成します。」
- 「画像の場合: ChatGPTで画像内容を読み取り、同じフォルダーにテキストファイル(.txt)を作成します。」

### 7.3 維持すべき実装方針

既存のWin32ネイティブDnDを維持:

- `WM_DROPFILES`
- `DragAcceptFiles`
- `win32gui.MessageBox`
- `win32gui.DrawText`
- `win32gui.PumpMessages`

禁止:

- tkinter
- Drop Here風UI

### 7.4 画像処理時のsubprocess要件

実行コマンド:

```bash
python PetitionLobbyingImageToTextfile_Cmd.py "<image_file_path>"
```

- `stdout` 取得
- 正常（returncode=0）: MessageBoxで結果表示
- 異常（`stderr`あり or returncode!=0）: MessageBoxでエラー表示

---

## 8. 命名規則

`docs/VARIABLE_NAMING_RULES.md` に準拠:

- 文字列: `psz...`
- int: `i...`
- bool: `b...`
- Path: `obj...`
- 過度な省略禁止

---

## 9. 今回実装しない項目

- フォルダー監視
- バッチ処理
- PDF処理
- OCRライブラリ
- SQLite
- WebUI（Flask/FastAPI/Django）
- 画像コピー
- APIによるファイル名提案

---

## 10. エラーケース整理

- 入力画像が存在しない → `_error.txt`
- APIキーが読めない → `_error.txt`
- OpenAI API失敗 → `_error.txt`
- 応答テキスト空 → `_error.txt`
- 対象外拡張子 → DnD側MessageBox

---

## 11. 最終到達イメージ

市民相談・陳情・請願・相談メモの画像をテキスト化し、既存のExcel由来TSV/TXTと併せてgrep検索可能な情報基盤へ統合する。
