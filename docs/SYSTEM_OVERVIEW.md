# SYSTEM OVERVIEW

## 概要

PetitionLobbyingManagementSystem は、

市民相談
陳情
請願
ロビー活動

などの情報を、

Excel
↓
TSV
↓
TXT
↓
grep

という流れで管理・検索するためのシステムです。

本システムは、

- 市役所運用
- 市議会運用
- 長期保守
- grep文化
- AI/RAG対応
- SQLite移行可能性

を重視して設計されています。

---

# システム構成

## 入力

Excel ファイル：

```text
相談データ_yyyy年mm月.xlsx
