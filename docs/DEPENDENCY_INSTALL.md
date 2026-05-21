# DEPENDENCY INSTALL

## 概要

本ドキュメントは、

PetitionLobbyingManagementSystem

を動作させるために必要な：

- Python
- pip
- ライブラリ

の導入方法を定義します。

本システムは：

- grep中心
- TSV中心
- TXT文化重視
- 市役所運用重視
- 長期保守重視

を前提として設計されています。

そのため、
導入方法も：

単純さ
+
分かりやすさ

を重視します。

---

# 必要環境

## OS

推奨：

```text
Windows 10
Windows 11
```

---

# Python

## 推奨バージョン

```text
Python 3.13 以上
```

推奨。

---

## 確認方法

cmdで：

```bash
python --version
```

または：

```bash
py --version
```

---

## 表示例

```text
Python 3.13.5
```

---

# pip

## 確認方法

```bash
python -m pip --version
```

---

# 必要ライブラリ

## 必須

```text
openpyxl
```

---

## 標準ライブラリ

以下はPython標準ライブラリのため、
追加install不要。

```text
pathlib
subprocess
sys
os
re
tkinter
```

---

# openpyxl install

## installコマンド

```bash
python -m pip install openpyxl
```

---

## pyコマンド版

```bash
py -m pip install openpyxl
```

---

# install確認

## 確認コマンド

```bash
python -m pip show openpyxl
```

---

## 表示例

```text
Name: openpyxl
Version: 3.1.5
```

---

# requirements.txt

## 将来的に追加可能

将来的に：

```text
requirements.txt
```

を追加可能。

---

## 現段階

最小構成重視。

---

# 推奨フォルダー構成

```text
PetitionLobbyingManagementSystem/

    PetitionLobbyingManagementSystem_Cmd.py
    PetitionLobbyingManagementSystem_DnD.py

    docs/

    TSV/

    Text/
```

---

# 推奨インストール手順

## 1

Python install。

---

## 2

openpyxl install。

```bash
python -m pip install openpyxl
```

---

## 3

Excelファイル準備。

```text
相談データ_2025年12月.xlsx
```

---

## 4

DnDへドラッグ＆ドロップ。

```text
PetitionLobbyingManagementSystem_DnD.py
```

---

## 5

TSV/TXT生成確認。

---

# grep推奨ソフト

## 推奨

```text
秀丸grep
```

---

## 理由

- 超高速
- 長寿命
- 安定
- 大量データ向き

---

# grep運用フロー

```text
Excel
↓
TSV/TXT生成
↓
秀丸grep
```

---

# UTF-8思想

## 文字コード

TSV/TXTは：

```text
UTF-8
```

使用。

---

## 理由

- grep相性
- AI相性
- Unicode対応
- 長期保存

---

# OneDrive注意事項

## 想定問題

OneDrive同期中は：

- ファイルロック
- 一時アクセス不可

が発生する可能性。

---

## 推奨

必要なら：

ローカルフォルダー

へコピーして実行。

---

# Windows Defender注意事項

## 想定

Python初回実行時：

警告

が出る可能性。

---

## 推奨

管理者へ確認。

---

# tkinterについて

## MessageBox表示

本システムでは：

```text
tkinter
```

を使用して：

MessageBox

表示を行う。

---

## install不要

標準ライブラリ。

---

# 実装しないもの

現段階では以下を導入しない。

- SQLite
- Flask
- FastAPI
- Django
- OCR
- AI
- Vector DB

---

# SQLite将来対応

## 将来構想

```text
TSV
↓
SQLite
```

---

## 現段階

未導入。

---

# AI/RAG将来対応

TXT群は：

将来的に：

- Embedding
- RAG
- AI検索

へ利用可能。

---

# トラブルシューティング

## openpyxl not found

### エラー例

```text
ModuleNotFoundError: No module named 'openpyxl'
```

---

### 対応

```bash
python -m pip install openpyxl
```

---

# Python path問題

## 確認

```bash
where python
```

---

## 理由

複数Python install時、
別Pythonが使用される可能性。

---

# pip更新

## 推奨

```bash
python -m pip install --upgrade pip
```

---

# openpyxl更新

## 推奨

```bash
python -m pip install --upgrade openpyxl
```

---

# 長期運用思想

## 10年以上運用可能構成

本システムは：

- 単純
- grep中心
- TXT中心
- TSV中心

を重視する。

---

# 市役所運用思想

## 非エンジニア重視

以下を重視。

- Drag & Drop
- MessageBox
- VBA最小
- 単純構成

---

# 最重要思想

## 壊れにくさ優先

本システムは：

高機能

より：

壊れにくさ

を優先する。

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
