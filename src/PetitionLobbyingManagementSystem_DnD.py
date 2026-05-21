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


def b_is_valid_excel_file(pathExcelFile: Path) -> bool:
    return pathExcelFile.exists() and pathExcelFile.suffix.lower() == ".xlsx"


def psz_merge_process_output(objResult: subprocess.CompletedProcess[str]) -> str:
    pszCombinedOutput = (objResult.stdout or "")
    if objResult.stderr:
        pszCombinedOutput += "\n" + objResult.stderr
    return pszCombinedOutput.strip()


def i_run_cmd_with_excel_file(pathExcelFile: Path) -> int:
    if not b_is_valid_excel_file(pathExcelFile):
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

    pszCombinedOutput = psz_merge_process_output(objResult)

    if objResult.returncode == 0:
        v_show_info("完了", f"TSV/TXT生成が完了しました。\n\n{pszCombinedOutput}")
        return 0

    v_show_error("変換エラー", f"TSV/TXT生成でエラーが発生しました。\n\n{pszCombinedOutput}")
    return 1


def list_parse_dnd_paths(pszDropData: str) -> list[Path]:
    listParsedPaths: list[Path] = []
    pszWorkingText = pszDropData.strip()

    while pszWorkingText:
        if pszWorkingText.startswith("{"):
            iClosingIndex = pszWorkingText.find("}")
            if iClosingIndex == -1:
                break
            pszToken = pszWorkingText[1:iClosingIndex]
            pszWorkingText = pszWorkingText[iClosingIndex + 1 :].lstrip()
        else:
            listTokens = pszWorkingText.split(maxsplit=1)
            pszToken = listTokens[0]
            pszWorkingText = listTokens[1] if len(listTokens) > 1 else ""

        if pszToken:
            listParsedPaths.append(Path(pszToken).expanduser().resolve())

    return listParsedPaths


def i_main() -> int:
    if len(sys.argv) >= 2:
        pathExcelFile = Path(sys.argv[1]).expanduser().resolve()
        return i_run_cmd_with_excel_file(pathExcelFile)

    objRoot = tk.Tk()
    objRoot.title("PetitionLobbyingManagementSystem DnD")
    objRoot.geometry("600x240")

    objLabelGuide = tk.Label(
        objRoot,
        text="このウインドウへ Excel(.xlsx) をドラッグ＆ドロップしてください",
        padx=12,
        pady=12,
    )
    objLabelGuide.pack(fill="x")

    objLabelDropArea = tk.Label(
        objRoot,
        text="Drop Here",
        relief="groove",
        borderwidth=2,
        height=6,
    )
    objLabelDropArea.pack(fill="both", expand=True, padx=16, pady=12)

    objLabelStatus = tk.Label(objRoot, text="待機中", anchor="w", padx=12)
    objLabelStatus.pack(fill="x", pady=(0, 8))

    def v_handle_drop_event(objEvent: tk.Event[tk.Misc]) -> None:
        pszDropData = str(objEvent.data)
        listDroppedPaths = list_parse_dnd_paths(pszDropData)
        if not listDroppedPaths:
            objLabelStatus.config(text="ドロップされたファイルを認識できませんでした")
            return

        pathExcelFile = listDroppedPaths[0]
        objLabelStatus.config(text=f"処理中: {pathExcelFile}")
        iReturnCode = i_run_cmd_with_excel_file(pathExcelFile)
        if iReturnCode == 0:
            objLabelStatus.config(text=f"完了: {pathExcelFile}")
        else:
            objLabelStatus.config(text=f"失敗: {pathExcelFile}")

    bDropEnabled = False
    try:
        objRoot.tk.call("package", "require", "tkdnd")
        objRoot.tk.call("tkdnd::drop_target", "register", str(objLabelDropArea), "DND_Files")
        objRoot.tk.call("bind", str(objLabelDropArea), "<<Drop>>", "{%d}")
    except Exception:
        pass

    try:
        objLabelDropArea.drop_target_register("DND_Files")
        objLabelDropArea.dnd_bind("<<Drop>>", v_handle_drop_event)
        bDropEnabled = True
    except Exception:
        try:
            objRoot.drop_target_register("DND_Files")
            objRoot.dnd_bind("<<Drop>>", v_handle_drop_event)
            bDropEnabled = True
        except Exception:
            bDropEnabled = False

    if not bDropEnabled:
        objLabelStatus.config(text="DnD機能を初期化できませんでした。ファイルをこのpyへ直接ドロップしてください。")

    objRoot.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(i_main())
