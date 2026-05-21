#!/usr/bin/env python3
"""PetitionLobbyingManagementSystem_DnD.py

Drag & Drop で受け取った Excel ファイルを Cmd 側へ渡す。
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


def v_show_info(pszTitle: str, pszMessage: str) -> None:
    objRoot = tk.Tk()
    objRoot.withdraw()
    messagebox.showinfo(pszTitle, pszMessage)
    objRoot.destroy()


def v_show_error(pszTitle: str, pszMessage: str) -> None:
    objRoot = tk.Tk()
    objRoot.withdraw()
    messagebox.showerror(pszTitle, pszMessage)
    objRoot.destroy()


def i_main() -> int:
    if len(sys.argv) < 2:
        v_show_error("入力エラー", "Excelファイルをこのスクリプトへドラッグ＆ドロップしてください。")
        return 1

    pathExcelFile = Path(sys.argv[1]).expanduser().resolve()
    if not pathExcelFile.exists() or pathExcelFile.suffix.lower() != ".xlsx":
        v_show_error("入力エラー", f"xlsxファイルを指定してください。\n\n{pathExcelFile}")
        return 1

    pathCurrentDirectory = Path(__file__).resolve().parent
    pathCmdScript = pathCurrentDirectory / "PetitionLobbyingManagementSystem_Cmd.py"

    if not pathCmdScript.exists():
        v_show_error("起動エラー", f"Cmdスクリプトが見つかりません。\n\n{pathCmdScript}")
        return 1

    try:
        objResult = subprocess.run(
            [sys.executable, str(pathCmdScript), str(pathExcelFile)],
            cwd=str(pathExcelFile.parent),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as objException:
        v_show_error("実行エラー", f"Cmd呼び出しに失敗しました。\n\n{objException}")
        return 1

    pszCombinedOutput = (objResult.stdout or "")
    if objResult.stderr:
        pszCombinedOutput += "\n" + objResult.stderr

    if objResult.returncode == 0:
        v_show_info("完了", f"TSV/TXT生成が完了しました。\n\n{pszCombinedOutput}")
        return 0

    v_show_error("変換エラー", f"TSV/TXT生成でエラーが発生しました。\n\n{pszCombinedOutput}")
    return 1


if __name__ == "__main__":
    raise SystemExit(i_main())
