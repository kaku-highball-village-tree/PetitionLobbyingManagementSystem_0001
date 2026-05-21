# FOLDER STRUCTURE

## 概要

本ドキュメントは、

PetitionLobbyingManagementSystem

のフォルダー構成を定義します。

本システムは：

- grep中心
- TSV中心
- TXT文化重視
- 長期保守重視
- 市役所運用重視

を前提として設計されています。

---

# 基本フォルダー構成

```text
PetitionLobbyingManagementSystem/

    PetitionLobbyingManagementSystem_Cmd.py
    PetitionLobbyingManagementSystem_DnD.py

    docs/

    TSV/

    Text/
```

---

# ルートフォルダー

## PetitionLobbyingManagementSystem/

システム全体のルートフォルダー。

---

## 目的

以下を一元管理する。

- Pythonコード
- docs
- TSV
- TXT

---

# Pythonコード

## PetitionLobbyingManagementSystem_Cmd.py

メイン処理。

---

## 役割

- Excel読込
- TSV生成
- TXT生成
- 禁止文字置換
- フォルダー生成

---

## PetitionLobbyingManagementSystem_DnD.py

Drag & Drop受付。

---

## 役割

- Drag & Drop受付
- Cmd呼び出し
- MessageBox表示
- エラー通知

---

# docs/

## 目的

仕様書・思想・ルール保存。

---

## 理由

本システムは：

長期保守

を重視するため。

---

## 想定ファイル

```text
docs/

    SYSTEM_OVERVIEW.md

    EXCEL_FORMAT_SPECIFICATION.md

    TSV_FORMAT_SPECIFICATION.md

    TEXT_FILE_SPECIFICATION.md

    VARIABLE_NAMING_RULES.md

    PROJECT_PHILOSOPHY.md

    FOLDER_STRUCTURE.md
```

---

# TSV/

## 目的

grep用TSV保存。

---

## 理由

TSVは：

- grepに強い
- SQLite移行しやすい
- Excel再読込しやすい
- AI前処理しやすい

ため。

---

## 出力例

```text
TSV/

    相談データ_2025年12月_search.tsv
```

---

## 内容

相談一覧シートを、
そのままTSV化。

---

## 文字コード

```text
UTF-8
```

---

# Text/

## 目的

1相談
=
1TXT

保存。

---

## 理由

TXTは：

- grepに強い
- AIに強い
- PDF連携しやすい
- 壊れにくい

ため。

---

## 出力例

```text
Text/

    000001_2025-12-0001_道路騒音.txt

    000002_2025-12-0002_ゴミ問題.txt
```

---

# TXTファイル命名規則

## 基本形式

```text
管理番号_受付番号_表題.txt
```

---

## 例

```text
000001_2025-12-0001_道路騒音.txt
```

---

# 禁止文字置換

## 対象文字

```text
\ / : * ? " < > |
```

---

## 置換文字

```text
_
```

---

# フォルダー生成仕様

## TSV/

存在しなければ自動生成。

---

## Text/

存在しなければ自動生成。

---

## docs/

通常は手動管理。

---

# grep中心思想

## 検索フロー

```text
Excel
↓
TSV/TXT生成
↓
秀丸grep
```

---

## grep推奨ソフト

```text
秀丸grep
```

---

# SQLite移行可能思想

## 将来構想

```text
TSV
↓
SQLite
```

---

## 現段階

SQLiteは未使用。

---

# AI/RAG対応思想

TXTフォルダーは、
将来的な：

- Embedding
- RAG
- AI検索
- AI要約

への発展を想定。

---

# OCR将来構想

将来的に：

```text
PDF
↓
OCR
↓
TXT
↓
grep / AI
```

へ発展可能。

---

# VBA最小思想

## VBAは極力使用しない

理由：

- 壊れやすい
- 市役所PC制約
- セキュリティ警告
- 保守難易度

---

# Python最小思想

## Pythonは変換専用

Pythonへ：

検索機能

を過剰実装しない。

---

## 検索はgrep

検索エンジンは：

```text
秀丸grep
```

---

# 長期運用思想

## 10年以上運用可能構成

本フォルダー構成は：

- 単純
- grep中心
- TXT中心
- TSV中心

を重視する。

---

# 市役所運用思想

## 非エンジニア運用

以下を重視する。

- Drag & Drop
- 単純構成
- 分かりやすいフォルダー
- VBA最小

---

# 非目的

以下は現段階では対象外。

- WebUI
- Flask
- FastAPI
- Django
- SaaS化
- クラウドDB
- OCR
- AI自動分類

---

# 最終目標

```text
Excel
↓
TSV/TXT生成
↓
秀丸grep
```

という：

最小構成
+
長寿命
+
壊れにくい

システムを実現すること。
