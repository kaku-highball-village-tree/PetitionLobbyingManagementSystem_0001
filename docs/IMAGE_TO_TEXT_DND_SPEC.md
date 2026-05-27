# 画像DnDテキスト化 機能仕様（実装前整理）

## 1. 対象プロジェクト
- PetitionLobbyingManagementSystem

## 2. 本ドキュメントの位置づけ
- **本仕様は実装前の整理のみ**を目的とする。
- 今回は以下を行わない。
  - `PetitionLobbyingImageToTextfile_Cmd.py` の実装
  - `PetitionLobbyingManagementSystem_DnD.py` の機能改修実装

## 3. 追加予定ファイル / 修正予定ファイル
- 新規（予定）:
  - `src/PetitionLobbyingImageToTextfile_Cmd.py`
- 修正（予定）:
  - `src/PetitionLobbyingManagementSystem_DnD.py`
- 参考:
  - `src/scan_output_monitor.py`

## 4. 目的
DnDウインドウへ画像ファイルがドロップされた場合に、画像をChatGPTへ送信して内容をテキスト化し、同じフォルダーへ`.txt`として保存する。

```text
画像ファイル
↓
ChatGPTで画像内容をテキスト化
↓
同じ場所に .txt ファイルとして保存
```

## 5. scan_output_monitor.py から踏襲する考え方
- OpenAI APIキーを暗号化ファイルから読み込む
- 画像をbase64化してOpenAI APIへ送る
- ChatGPT応答からテキストを抽出する
- Windows禁止文字の扱い方（必要箇所のみ）
- ログ/エラー情報の出力方針（最小限）

## 6. scan_output_monitor.py から変更する点
監視型からDnD起動型へ変更する。

- 廃止対象（今回不要）
  - `WATCH_DIR`
  - `POLL_INTERVAL_SECONDS`
  - `STABLE_REQUIRED_COUNT`
  - `BATCH_TIMEOUT_SECONDS`
  - `Batch`クラス
  - `run_monitor()`
  - 新規ファイル監視 / 待機 / バッチ終了判定
  - コピー確認ダイアログ
  - フォルダー作成
  - スキャンファイルコピー
  - ファイル名提案処理

## 7. 新規Cmd（予定）仕様
対象: `PetitionLobbyingImageToTextfile_Cmd.py`

### 7.1 起動方式
- コマンドライン引数で画像パスを1つ受け取る。
- 例:
  - `python PetitionLobbyingImageToTextfile_Cmd.py "C:\Data\相談メモ.jpg"`

### 7.2 処理手順
1. 引数確認
2. 画像ファイル存在確認
3. 画像拡張子確認
4. OpenAI APIキー読込
5. 画像base64化
6. ChatGPTへテキスト化依頼
7. 応答テキスト取得
8. 同一フォルダーへ`.txt`保存
9. 成功時: 出力先パスを`print`
10. エラー時: `_error.txt`出力

### 7.3 対象拡張子
- 現段階の対象:
  - `.jpg`
  - `.jpeg`
  - `.png`
- 将来拡張候補:
  - `.webp` / `.bmp` / `.tif` / `.tiff`

### 7.4 非対象
- PDFは対象外（将来拡張）

### 7.5 出力ファイル名
- 入力: `相談メモ_0001.jpg`
- 出力: `相談メモ_0001.txt`
- 衝突時:
  - `相談メモ_0001_1.txt`
  - `相談メモ_0001_2.txt`

### 7.6 エラーファイル名
- 入力: `相談メモ_0001.jpg`
- エラー: `相談メモ_0001_error.txt`

### 7.7 ChatGPTプロンプト方針
- 目的: grep検索可能な本文テキスト化
- ルール:
  - 画像内文字を最優先
  - 項目名・レイアウト意味を可能な範囲で整理
  - 過度な推測をしない
  - 判読不能箇所は`[判読不能]`
  - ファイル名案/タイトル案は不要
  - 出力は本文テキストのみ

### 7.8 OpenAI API仕様（踏襲方針）
- `SECRET_KEY_PATH`
- `ENCRYPTED_KEY_PATH`
- `load_api_key_from_encrypted_files()`
- `extract_response_text()`
- `data:image/jpeg;base64,...` 形式
- `client.responses.create()`
- モデル: `gpt-4o-mini`（将来変更可能）

### 7.9 APIキー配置
`PetitionLobbyingImageToTextfile_Cmd.py` から見て:
- `./key/secret_key.bin`
- `./ciphertext/encrypted_key.bin`

### 7.10 文字コード
- 出力txt: UTF-8
- 改行: CRLF推奨

## 8. DnD側（予定）仕様
対象: `PetitionLobbyingManagementSystem_DnD.py`

### 8.1 拡張子による分岐
- `.xlsx`:
  - `PetitionLobbyingManagementSystem_Cmd.py` を呼び出す
- `.jpg / .jpeg / .png`:
  - `PetitionLobbyingImageToTextfile_Cmd.py` を呼び出す
- その他:
  - `MessageBox`でエラー表示

### 8.2 画面表示文言（予定）
- 相談データExcel(.xlsx) または 相談メモ画像(.jpg/.jpeg/.png) を
  このウインドウへドラッグ＆ドロップしてください。
- Excelの場合: TSV/TXTを生成します。
- 画像の場合: ChatGPTで画像内容を読み取り、同じフォルダーにテキストファイル(.txt)を作成します。

### 8.3 UI/実装方針（維持）
- Win32ネイティブDnD方式を維持
- 維持対象:
  - `WM_DROPFILES`
  - `DragAcceptFiles`
  - `win32gui.MessageBox`
  - `win32gui.DrawText`
  - `win32gui.PumpMessages`
- 不採用:
  - tkinter
  - Drop Here風UI

### 8.4 subprocess仕様（画像時）
- 実行:
  - `python PetitionLobbyingImageToTextfile_Cmd.py "<image_file_path>"`
- 成功:
  - `stdout`内容をMessageBoxで表示
- 失敗:
  - `stderr` または `returncode != 0` をMessageBoxで表示

## 9. エラーケース整理
- 画像ファイル不存在 → `_error.txt`
- APIキー読込失敗 → `_error.txt`
- OpenAI API失敗 → `_error.txt`
- ChatGPT応答空 → `_error.txt`
- 対象外拡張子 → DnD側MessageBox

## 10. 命名規則
`docs/VARIABLE_NAMING_RULES.md` を遵守する。
- 文字列: `psz～`
- int: `i～`
- bool: `b～`
- Path: `obj～`
- 過度な省略名は使用しない

## 11. 今回実装しないもの（再確認）
- フォルダー監視
- バッチ処理
- PDF処理
- OCRライブラリ
- SQLite
- WebUI（Flask/FastAPI/Django）
- 画像コピー
- APIによるファイル名提案

## 12. 最終目的
市民相談・陳情・請願・相談メモの画像をgrep検索可能なテキストへ変換し、既存のExcel由来テキストと合わせて同一検索文化で活用可能にする。
