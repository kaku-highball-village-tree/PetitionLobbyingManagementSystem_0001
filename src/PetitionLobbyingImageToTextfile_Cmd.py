#!/usr/bin/env python3
"""Convert one dropped image file into grep-friendly TXT via ChatGPT."""

from __future__ import annotations

import base64
import mimetypes
import sys
from pathlib import Path
from typing import List

SCRIPT_DIR = Path(__file__).resolve().parent
SECRET_KEY_PATH = SCRIPT_DIR / "key" / "secret_key.bin"
ENCRYPTED_KEY_PATH = SCRIPT_DIR / "ciphertext" / "encrypted_key.bin"
SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
OPENAI_MODEL = "gpt-4o-mini"

PROMPT_IMAGE_TO_TEXT = (
    "画像から読み取れる内容を、できるだけ正確にテキスト化してください。\n"
    "目的は、市民相談、陳情、請願、相談メモなどをgrep検索できるテキストに変換することです。\n"
    "画像内にある文字を優先してください。\n"
    "レイアウト上意味が分かる項目名も整理してください。\n"
    "ただし、推測しすぎないでください。\n"
    "読めない文字は [判読不能] と書いてください。\n"
    "ファイル名案は不要です。\n"
    "タイトル案は不要です。\n"
    "出力は本文テキストだけにしてください。\n"
    "\n"
    "出力形式は以下の固定フォーマットに厳密に合わせてください。\n"
    "管理番号: <値>\n"
    "受付番号: <値>\n"
    "相談日: <値>\n"
    "相談者: <値>\n"
    "相談内容(表題): <値>\n"
    "依頼日: <値>\n"
    "依頼課: <値>\n"
    "受付担当者: <値>\n"
    "処理可否_日: <値>\n"
    "処理の可否_1: <値>\n"
    "処理の可否_2: <値>\n"
    "\n"
    "本文:\n"
    "<本文テキスト>\n"
)


def load_api_key_from_encrypted_files() -> str:
    from cryptography.fernet import Fernet

    with SECRET_KEY_PATH.open("rb") as objSecretFile:
        bytesSecretKey = objSecretFile.read()

    with ENCRYPTED_KEY_PATH.open("rb") as objEncryptedFile:
        bytesEncryptedToken = objEncryptedFile.read()

    objCipher = Fernet(bytesSecretKey)
    return objCipher.decrypt(bytesEncryptedToken).decode("utf-8")


def extract_response_text(objResponse: object) -> str | None:
    pszOutputText = getattr(objResponse, "output_text", None)
    if isinstance(pszOutputText, str) and pszOutputText.strip():
        return pszOutputText.strip()

    objOutputItems = getattr(objResponse, "output", None)
    if not isinstance(objOutputItems, list):
        return None

    listCollectedText: List[str] = []
    for objOutputItem in objOutputItems:
        objItemContent = getattr(objOutputItem, "content", None)
        if not isinstance(objItemContent, list):
            continue
        for objContentPart in objItemContent:
            pszTextValue = getattr(objContentPart, "text", None)
            if isinstance(pszTextValue, str) and pszTextValue.strip():
                listCollectedText.append(pszTextValue.strip())

    if not listCollectedText:
        return None
    return "\n".join(listCollectedText)


def build_data_url_from_image_file(objImageFilePath: Path) -> str:
    bytesImageData = objImageFilePath.read_bytes()
    pszMimeType = mimetypes.guess_type(str(objImageFilePath))[0] or "image/jpeg"
    pszImageBase64 = base64.b64encode(bytesImageData).decode("ascii")
    return f"data:{pszMimeType};base64,{pszImageBase64}"


def get_nonconflicting_output_txt_path(objImageFilePath: Path) -> Path:
    objOutputDirectoryPath = objImageFilePath.parent
    pszStemName = objImageFilePath.stem
    objPrimaryTextPath = objOutputDirectoryPath / f"{pszStemName}.txt"
    if not objPrimaryTextPath.exists():
        return objPrimaryTextPath

    iSuffixIndex = 1
    while True:
        objCandidateTextPath = objOutputDirectoryPath / f"{pszStemName}_{iSuffixIndex}.txt"
        if not objCandidateTextPath.exists():
            return objCandidateTextPath
        iSuffixIndex += 1


def write_error_file(objImageFilePath: Path, pszErrorMessage: str) -> Path:
    objErrorPath = objImageFilePath.parent / f"{objImageFilePath.stem}_error.txt"
    objErrorPath.write_text(pszErrorMessage + "\r\n", encoding="utf-8", newline="\r\n")
    return objErrorPath


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python PetitionLobbyingImageToTextfile_Cmd.py <image_file_path>", file=sys.stderr)
        return 1

    objImageFilePath = Path(sys.argv[1])
    if not objImageFilePath.exists():
        try:
            write_error_file(objImageFilePath, f"画像ファイルが存在しません: {objImageFilePath}")
        except Exception:
            pass
        print(f"画像ファイルが存在しません: {objImageFilePath}", file=sys.stderr)
        return 1

    pszLowerSuffix = objImageFilePath.suffix.lower()
    if pszLowerSuffix not in SUPPORTED_IMAGE_SUFFIXES:
        write_error_file(objImageFilePath, f"対象外拡張子です: {objImageFilePath.suffix}")
        print(f"対象外拡張子です: {objImageFilePath.suffix}", file=sys.stderr)
        return 1

    try:
        pszApiKey = load_api_key_from_encrypted_files()
    except Exception as objError:
        write_error_file(objImageFilePath, f"APIキー読込失敗: {objError}")
        print(f"APIキー読込失敗: {objError}", file=sys.stderr)
        return 1

    try:
        pszDataUrl = build_data_url_from_image_file(objImageFilePath)
    except Exception as objError:
        write_error_file(objImageFilePath, f"画像base64化失敗: {objError}")
        print(f"画像base64化失敗: {objError}", file=sys.stderr)
        return 1

    try:
        from openai import OpenAI

        objClient = OpenAI(api_key=pszApiKey)
        objResponse = objClient.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": PROMPT_IMAGE_TO_TEXT},
                        {"type": "input_image", "image_url": pszDataUrl},
                    ],
                }
            ],
        )
    except Exception as objError:
        write_error_file(objImageFilePath, f"OpenAI API失敗: {objError}")
        print(f"OpenAI API失敗: {objError}", file=sys.stderr)
        return 1

    pszResponseText = extract_response_text(objResponse)
    if not pszResponseText:
        write_error_file(objImageFilePath, "ChatGPT応答が空です")
        print("ChatGPT応答が空です", file=sys.stderr)
        return 1

    try:
        objOutputTextPath = get_nonconflicting_output_txt_path(objImageFilePath)
        objOutputTextPath.write_text(pszResponseText, encoding="utf-8", newline="\r\n")
    except Exception as objError:
        write_error_file(objImageFilePath, f"テキスト保存失敗: {objError}")
        print(f"テキスト保存失敗: {objError}", file=sys.stderr)
        return 1

    print(str(objOutputTextPath))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
