#!/usr/bin/env python3
"""PetitionLobbyingManagementSystem_DnD.py

WindowsネイティブDnDウインドウでExcel(.xlsx)を受け取り、
Cmdスクリプトを呼び出す。
"""

from __future__ import annotations

from pathlib import Path
import ctypes
import subprocess
import sys

import win32api
import win32con
import win32gui


pszWINDOW_CLASS_NAME: str = "PetitionLobbyingManagementSystemDnDWindowClass"
pszWINDOW_TITLE: str = "PetitionLobbyingManagementSystem DnD"
INSTRUCTION_FONT_HEIGHT: int = -17
INSTRUCTION_FONT_FACE: str = "Meiryo UI"


def show_message_box(pszMessage: str, pszTitle: str = "完了") -> None:
    win32gui.MessageBox(0, pszMessage, pszTitle, win32con.MB_OK | win32con.MB_ICONINFORMATION)


def show_error_message_box(pszMessage: str, pszTitle: str = "エラー") -> None:
    win32gui.MessageBox(0, pszMessage, pszTitle, win32con.MB_OK | win32con.MB_ICONERROR)


def b_is_excel_file(pathFile: Path) -> bool:
    return pathFile.exists() and pathFile.suffix.lower() == ".xlsx"


def b_is_image_file(pathFile: Path) -> bool:
    return pathFile.exists() and pathFile.suffix.lower() in {".jpg", ".jpeg", ".png"}


def draw_instruction_text(hWnd: int) -> None:
    hdc, objPaintStruct = win32gui.BeginPaint(hWnd)
    try:
        hFont = ctypes.windll.gdi32.CreateFontW(
            INSTRUCTION_FONT_HEIGHT,
            0,
            0,
            0,
            win32con.FW_NORMAL,
            0,
            0,
            0,
            win32con.SHIFTJIS_CHARSET,
            win32con.OUT_DEFAULT_PRECIS,
            win32con.CLIP_DEFAULT_PRECIS,
            win32con.CLEARTYPE_QUALITY,
            win32con.DEFAULT_PITCH | win32con.FF_DONTCARE,
            INSTRUCTION_FONT_FACE,
        )

        iOldFontHandle = win32gui.SelectObject(hdc, hFont)
        try:
            iMargin: int = 5
            iLeft, iTop, iRight, iBottom = win32gui.GetClientRect(hWnd)
            objRect = (iLeft + iMargin, iTop + iMargin, iRight - iMargin, iBottom - iMargin)
            pszInstructionText: str = (
                "相談データExcel(.xlsx) または 相談メモ画像(.jpg/.jpeg/.png) を\r\n"
                "このウインドウへドラッグ＆ドロップしてください。\r\n\r\n"
                "Excelの場合:\r\n"
                "TSV/TXTを生成します。\r\n\r\n"
                "画像の場合:\r\n"
                "ChatGPTで画像内容を読み取り、\r\n"
                "同じフォルダーにテキストファイル(.txt)を作成します。"
            )
            win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
            win32gui.DrawText(
                hdc,
                pszInstructionText,
                -1,
                objRect,
                win32con.DT_LEFT | win32con.DT_TOP | win32con.DT_WORDBREAK,
            )
        finally:
            win32gui.SelectObject(hdc, iOldFontHandle)
            ctypes.windll.gdi32.DeleteObject(hFont)
    finally:
        win32gui.EndPaint(hWnd, objPaintStruct)


def run_cmd_script(pathInputFile: Path, pszCmdScriptName: str, pszSuccessMessage: str, pszErrorMessage: str) -> int:
    pathCurrentDirectory: Path = Path(__file__).resolve().parent
    pathCmdScript: Path = pathCurrentDirectory / pszCmdScriptName

    if not pathCmdScript.exists():
        show_error_message_box(f"Cmdスクリプトが見つかりません。\n\n{pathCmdScript}", "起動エラー")
        return 1

    try:
        objResult = subprocess.run(
            [sys.executable, str(pathCmdScript), str(pathInputFile)],
            cwd=str(pathInputFile.parent),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as objException:
        show_error_message_box(f"Cmd呼び出しに失敗しました。\n\n{objException}", "実行エラー")
        return 1

    pszOutput: str = (objResult.stdout or "").strip()
    pszErrorOutput: str = (objResult.stderr or "").strip()
    if pszErrorOutput:
        if pszOutput:
            pszOutput = f"{pszOutput}\n{pszErrorOutput}"
        else:
            pszOutput = pszErrorOutput

    if objResult.returncode == 0:
        show_message_box(f"{pszSuccessMessage}\n\n{pszOutput}", "完了")
        return 0

    show_error_message_box(f"{pszErrorMessage}\n\n{pszOutput}", "変換エラー")
    return 1


def handle_drop_files(hDrop: int) -> None:
    iFileCount: int = win32api.DragQueryFile(hDrop, -1)

    if iFileCount != 1:
        show_error_message_box("ドラッグ＆ドロップできるファイルは1件のみです。", "入力エラー")
        win32api.DragFinish(hDrop)
        return

    pszDroppedFilePath: str = win32api.DragQueryFile(hDrop, 0)
    win32api.DragFinish(hDrop)

    pathInputFile: Path = Path(pszDroppedFilePath).expanduser().resolve()

    if b_is_excel_file(pathInputFile):
        run_cmd_script(
            pathInputFile,
            "PetitionLobbyingManagementSystem_Cmd.py",
            "TSV/TXT生成が完了しました。",
            "TSV/TXT生成でエラーが発生しました。",
        )
        return

    if b_is_image_file(pathInputFile):
        run_cmd_script(
            pathInputFile,
            "PetitionLobbyingImageToTextfile_Cmd.py",
            "画像テキスト化が完了しました。",
            "画像テキスト化でエラーが発生しました。",
        )
        return

    show_error_message_box(
        f".xlsx / .jpg / .jpeg / .png ファイルのみ受け付けます。\n\n{pathInputFile}",
        "入力エラー",
    )


def window_proc(hWnd: int, msg: int, wParam: int, lParam: int) -> int:
    if msg == win32con.WM_CREATE:
        win32gui.DragAcceptFiles(hWnd, True)
        return 0

    if msg == win32con.WM_DROPFILES:
        handle_drop_files(wParam)
        return 0

    if msg == win32con.WM_PAINT:
        draw_instruction_text(hWnd)
        return 0

    if msg == win32con.WM_DESTROY:
        win32gui.PostQuitMessage(0)
        return 0

    return win32gui.DefWindowProc(hWnd, msg, wParam, lParam)


def register_window_class(hInstance: int) -> int:
    objWindowClass = win32gui.WNDCLASS()
    objWindowClass.hInstance = hInstance
    objWindowClass.lpszClassName = pszWINDOW_CLASS_NAME
    objWindowClass.lpfnWndProc = window_proc
    objWindowClass.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
    objWindowClass.hbrBackground = win32con.COLOR_WINDOW + 1
    return win32gui.RegisterClass(objWindowClass)


def create_main_window(hInstance: int) -> int:
    iDesktopWidth: int = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    iDesktopHeight: int = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
    iWindowWidth: int = int(iDesktopWidth * 0.5)
    iWindowHeight: int = int(iDesktopHeight * 0.5)

    return win32gui.CreateWindowEx(
        win32con.WS_EX_ACCEPTFILES,
        pszWINDOW_CLASS_NAME,
        pszWINDOW_TITLE,
        win32con.WS_OVERLAPPED | win32con.WS_CAPTION | win32con.WS_SYSMENU | win32con.WS_MINIMIZEBOX,
        win32con.CW_USEDEFAULT,
        win32con.CW_USEDEFAULT,
        iWindowWidth,
        iWindowHeight,
        0,
        0,
        hInstance,
        None,
    )


def i_main() -> int:
    try:
        hInstance: int = win32api.GetModuleHandle(None)
    except Exception as objException:
        show_error_message_box(f"モジュールハンドル取得に失敗しました。\n\n{objException}", "起動エラー")
        return 1

    try:
        register_window_class(hInstance)
    except Exception as objException:
        show_error_message_box(f"ウインドウクラス登録に失敗しました。\n\n{objException}", "起動エラー")
        return 1

    try:
        hWnd: int = create_main_window(hInstance)
    except Exception as objException:
        show_error_message_box(f"ウインドウ作成に失敗しました。\n\n{objException}", "起動エラー")
        return 1

    if not hWnd:
        show_error_message_box("ウインドウ作成に失敗しました。", "起動エラー")
        return 1

    try:
        win32gui.SetWindowPos(
            hWnd,
            win32con.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE,
        )
        win32gui.ShowWindow(hWnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(hWnd)
    except Exception as objException:
        show_error_message_box(f"ウインドウ表示に失敗しました。\n\n{objException}", "起動エラー")
        return 1

    try:
        win32gui.PumpMessages()
    except Exception as objException:
        show_error_message_box(f"メッセージループでエラーが発生しました。\n\n{objException}", "実行エラー")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(i_main())
