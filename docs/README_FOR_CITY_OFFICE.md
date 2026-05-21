# README FOR CITY OFFICE

## 概要

本システムは、

市民相談
陳情
請願

などを、

Excel
↓
TSV/TXT
↓
秀丸grep

で管理・検索するためのシステムです。

本システムは：

- 市役所職員
- 市議会議員
- 非エンジニア

でも扱えることを重視しています。

---

# システムの流れ

```text
Excelへ入力
↓
Pythonへドラッグ＆ドロップ
↓
TSV/TXT生成
↓
秀丸grepで検索
```

---

# 必要なもの

## 1

Python

---

## 2

openpyxl

---

## 3

秀丸grep

---

# フォルダー構成

```text
PetitionLobbyingManagementSystem/

    PetitionLobbyingManagementSystem_Cmd.py
    PetitionLobbyingManagementSystem_DnD.py

    TSV/
    Text/
    docs/
```

---

# Excelファイル

## ファイル名

```text
相談データ_yyyy年mm月.xlsx
```

---

## 例

```text
相談データ_2025年12月.xlsx
```

---

# Excelシート

## 相談一覧

メイン入力。

---

## 依頼課

G列プルダウン用。

---

# Excel列構成

```tsv
管理番号	受付番号	相談日	相談者	相談内容(表題)	依頼日	依頼課	受付担当者	処理可否_日	処理の可否_1	処理の可否_2	本文
```

---

# 管理番号について

## A列

全体通し番号。

---

## 表示形式

ユーザー定義：

```text
000000
```

---

## A2

手入力。

例：

```text
1
```

表示：

```text
000001
```

---

## A3

```excel
=A2+1
```

---

# 受付番号について

## B列

年月付き番号。

---

## 例

```text
2025-12-0001
```

---

## B2

```excel
=TEXT(C2,"yyyy-mm")&"-0001"
```

---

## B3以降

```excel
=LEFT(B2,8)&TEXT(VALUE(RIGHT(B2,4))+1,"0000")
```

---

# 日付列について

## 対象

- C列
- F列
- I列

---

## 表示形式

ユーザー定義：

```text
yyyy"年"mm"月"dd"日"
```

---

# 依頼課プルダウン

## G列

プルダウン入力。

---

## 設定方法

データ
↓
データの入力規則
↓
リスト

---

## 元の値

```excel
=依頼課!$A$1:$A$200
```

---

# Python実行方法

## 実行ファイル

```text
PetitionLobbyingManagementSystem_DnD.py
```

---

## 操作方法

Excelファイルを：

```text
PetitionLobbyingManagementSystem_DnD.py
```

へドラッグ＆ドロップ。

---

# 出力フォルダー

## TSV

```text
TSV/
```

---

## Text

```text
Text/
```

---

# TSVについて

## ファイル名例

```text
相談データ_2025年12月_search.tsv
```

---

## 用途

- 秀丸grep
- Excel再読込
- TSV解析

---

# TXTについて

## 1相談 = 1TXT

TXTファイルを生成。

---

## ファイル名例

```text
000001_2025-12-0001_道路騒音.txt
```

---

## 用途

- grep
- AI/RAG
- PDF連携
- 長期保存

---

# grep検索方法

## 推奨

```text
秀丸grep
```

---

## 基本操作

秀丸grep起動。

---

## 検索対象

```text
TSV/
```

または：

```text
Text/
```

---

## 検索例

```text
道路
```

```text
騒音
```

```text
土木課
```

```text
対応不可
```

---

# grepの利点

- 超高速
- 大量データ向き
- 一覧性が高い
- 壊れにくい

---

# なぜExcel検索しないのか

Excel検索は：

- 遅い
- 一覧性が弱い
- 大量データに弱い

ため。

---

# VBAを使わない理由

VBAは：

- 壊れやすい
- セキュリティ警告
- 市役所PC制約

があるため。

---

# システム思想

## grep中心

検索エンジンは：

```text
秀丸grep
```

---

## TSV中心

TSVを主データとする。

---

## TXT文化重視

1相談
=
1TXT

を重視。

---

## Python最小

Pythonは：

- Excel読込
- TSV生成
- TXT生成

のみ。

---

## VBA最小

VBA依存を避ける。

---

# 将来構想

将来的に：

- SQLite
- OCR
- AI検索
- RAG
- PDF管理

へ発展可能。

---

# 現段階で実装しないもの

- WebUI
- Flask
- FastAPI
- Django
- AI自動分類
- OCR

---

# エラー時

## 基本

MessageBox表示。

---

## 主な原因

- Excel開きっぱなし
- OneDrive同期
- ファイル名問題

---

# OneDrive注意

## 想定問題

同期中は：

- ファイルロック
- 一時アクセス不可

発生可能。

---

## 推奨

必要なら：

ローカルフォルダー

へコピーして実行。

---

# UTF-8について

TSV/TXTは：

```text
UTF-8
```

使用。

---

# 長期運用思想

本システムは：

10年以上運用可能

を重視。

---

# 最重要思想

本システムでは：

```text
壊れにくさ
+
単純さ
+
grep文化
```

を最優先する。

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
