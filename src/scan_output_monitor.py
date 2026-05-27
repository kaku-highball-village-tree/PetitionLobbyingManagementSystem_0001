#!/usr/bin/env python3
"""Monitor C:\\Scan_Output and copy scanned files in safe batches.

Implemented behavior summary:
- Watch only newly created .jpg/.jpeg/.pdf files under C:\\Scan_Output.
- Start a batch when the first target file appears.
- Create destination folder named yyyy年mm月dd日hh時mm分ss秒
  using the first file's creation timestamp.
- File stability check: unchanged size/mtime for 3 consecutive checks.
- Batch end: 20 seconds with no new target file.
- Polling interval: 3 seconds.
- OpenAI naming key files (script-relative):
  ./key/secret_key.bin and ./ciphertext/encrypted_key.bin
- At batch end, show Yes/No dialog only for non-mixed batches.
  * Dialog wait: 20 seconds
  * Timeout default: Yes (auto proceed)
  * If No: wait 20 seconds and show same dialog again
- If OpenAI naming fails, allow manual filename input.
- Write daily logs to ./logs/scan_output_monitor_YYYYMMDD.log
"""

from __future__ import annotations

import base64
import shutil
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Set

WATCH_DIR = Path(r"C:\Scan_Output")
TARGET_SUFFIXES = {".jpg", ".jpeg", ".pdf"}
JPEG_SUFFIXES = {".jpg", ".jpeg"}
POLL_INTERVAL_SECONDS = 3
STABLE_REQUIRED_COUNT = 3
BATCH_TIMEOUT_SECONDS = 20
COPY_RETRY_COUNT = 3
COPY_RETRY_WAIT_SECONDS = 1
DIALOG_TIMEOUT_SECONDS = 20

SCRIPT_DIR = Path(__file__).resolve().parent
SECRET_KEY_PATH = SCRIPT_DIR / "key" / "secret_key.bin"
ENCRYPTED_KEY_PATH = SCRIPT_DIR / "ciphertext" / "encrypted_key.bin"
LOG_DIR = SCRIPT_DIR / "logs"
OPENAI_MODEL = "gpt-4o-mini"
MAX_SUGGESTED_NAME_LENGTH = 80


@dataclass
class FileState:
    """Track file stability via size/mtime observations."""

    path: Path
    last_size: int
    last_mtime_ns: int
    stable_count: int = 0
    is_stable: bool = False


class Batch:
    """Manage one scan batch from first detection to copy completion."""

    def __init__(self, first_file: Path) -> None:
        stat = first_file.stat()
        self.first_detected_file = first_file
        self.first_created_datetime = datetime.fromtimestamp(stat.st_ctime)
        self.destination_dir = WATCH_DIR / self.first_created_datetime.strftime(
            "%Y年%m月%d日%H時%M分%S秒"
        )
        self.files: Dict[Path, FileState] = {}
        self.add_file(first_file)
        self.last_new_file_monotonic = time.monotonic()
        self.suggested_name_stem: str | None = None

    def add_file(self, file_path: Path) -> None:
        if file_path in self.files:
            return
        try:
            stat = file_path.stat()
        except FileNotFoundError:
            return
        self.files[file_path] = FileState(
            path=file_path,
            last_size=stat.st_size,
            last_mtime_ns=stat.st_mtime_ns,
            stable_count=0,
            is_stable=False,
        )
        self.last_new_file_monotonic = time.monotonic()

    def update_stability(self) -> None:
        for path, state in list(self.files.items()):
            if state.is_stable:
                continue
            try:
                stat = path.stat()
            except FileNotFoundError:
                continue

            same_size = stat.st_size == state.last_size
            same_mtime = stat.st_mtime_ns == state.last_mtime_ns
            if same_size and same_mtime:
                state.stable_count += 1
            else:
                state.stable_count = 0
                state.last_size = stat.st_size
                state.last_mtime_ns = stat.st_mtime_ns

            if state.stable_count >= STABLE_REQUIRED_COUNT:
                state.is_stable = True

    def timed_out(self) -> bool:
        return time.monotonic() - self.last_new_file_monotonic >= BATCH_TIMEOUT_SECONDS

    def stable_files(self) -> List[Path]:
        return [state.path for state in self.files.values() if state.is_stable]



def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



def write_log(level: str, message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_name = f"scan_output_monitor_{datetime.now():%Y%m%d}.log"
    log_path = LOG_DIR / log_name
    line = f"{now_str()} [{level}] {message}"
    print(line)
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(line + "\n")



def is_target_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in TARGET_SUFFIXES



def list_current_target_files() -> Set[Path]:
    if not WATCH_DIR.exists():
        return set()
    return {path for path in WATCH_DIR.iterdir() if is_target_file(path)}



def copy_with_retry(src: Path, dst: Path) -> bool:
    for attempt in range(1, COPY_RETRY_COUNT + 1):
        try:
            shutil.copy2(src, dst)
            return True
        except OSError as exc:
            write_log(
                "WARN",
                f"copy failed ({attempt}/{COPY_RETRY_COUNT}): {src} -> {dst}: {exc}",
            )
            if attempt < COPY_RETRY_COUNT:
                time.sleep(COPY_RETRY_WAIT_SECONDS)
    return False



def load_api_key_from_encrypted_files() -> str:
    from cryptography.fernet import Fernet

    with SECRET_KEY_PATH.open("rb") as secret_file:
        secret_key = secret_file.read()

    with ENCRYPTED_KEY_PATH.open("rb") as encrypted_file:
        token = encrypted_file.read()

    cipher = Fernet(secret_key)
    return cipher.decrypt(token).decode("utf-8")



def sanitize_filename_stem(name: str) -> str:
    invalid_chars = '\\/:*?"<>|'
    cleaned = "".join("_" if ch in invalid_chars else ch for ch in name)
    cleaned = cleaned.strip().strip(".")
    if not cleaned:
        cleaned = "scan_file"
    return cleaned[:MAX_SUGGESTED_NAME_LENGTH]



def ask_manual_name(default_name: str) -> str:
    try:
        import tkinter as tk
        from tkinter import simpledialog

        root = tk.Tk()
        root.withdraw()
        response = simpledialog.askstring(
            "ファイル名入力",
            "API命名に失敗しました。ファイル名（拡張子なし）を入力してください。",
            initialvalue=default_name,
            parent=root,
        )
        root.destroy()
        if response:
            return sanitize_filename_stem(response)
    except Exception as exc:
        write_log("WARN", f"manual name dialog unavailable: {exc}")
    return default_name



def extract_response_text(response: object) -> str | None:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    output_items = getattr(response, "output", None)
    if not isinstance(output_items, list):
        return None

    collected: List[str] = []
    for item in output_items:
        item_content = getattr(item, "content", None)
        if not isinstance(item_content, list):
            continue
        for content_part in item_content:
            text_value = getattr(content_part, "text", None)
            if isinstance(text_value, str) and text_value.strip():
                collected.append(text_value.strip())

    if not collected:
        return None
    return " ".join(collected)



def build_pdf_first_page_data_url(file_path: Path) -> str | None:
    """Render first PDF page to JPEG and return as data URL for OpenAI input_image."""
    try:
        import io
        import pypdfium2 as pdfium
        from PIL import Image

        pdf = pdfium.PdfDocument(str(file_path))
        if len(pdf) == 0:
            return None
        page = pdf[0]
        bitmap = page.render(scale=2.0)
        pil_image = bitmap.to_pil()
        with io.BytesIO() as buffer:
            pil_image.convert("RGB").save(buffer, format="JPEG", quality=90)
            image_base64 = base64.b64encode(buffer.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{image_base64}"
    except Exception as exc:
        write_log("WARN", f"PDF render failed for OpenAI image input: {exc}")
        return None



def suggest_name_for_first_file(file_path: Path) -> str | None:
    try:
        api_key = load_api_key_from_encrypted_files()
    except Exception as exc:
        write_log("WARN", f"OpenAI key load failed: {exc}")
        return None

    prompt = (
        "次のスキャン文書のファイル名を作成してください。\n\n"
        "【画像ファイルの場合】\n"
        "画像の内容（文字・レイアウト・文書の種類）を読み取り、\n"
        "文書内容を表す日本語の簡潔なファイル名を作成してください。\n\n"
        "【PDFファイルの場合】\n"
        "PDFのページ内容（文字・レイアウト）を読み取り、\n"
        "文書内容を表す日本語の簡潔なファイル名を作成してください。\n"
        "PDFファイル名だけを根拠にして命名してはいけません。\n"
        "むしろ、PDFファイル名は使用しないでください。\n\n"
        "【出力ルール】\n"
        "・ファイル名は1つだけ出力する\n"
        "・拡張子は付けない\n"
        "・1行のみ出力する\n"
        "・Windows禁止文字 \\ / : * ? \" < > | は使わない\n"
        "・できるだけ20文字以内で簡潔にする\n\n"
        "【例】\n"
        "請求書_株式会社山田\n"
        "領収書_アマゾン\n"
        "契約書_賃貸契約\n\n"
        "ファイル名以外の文章は一切出力しないでください。"
    )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        if file_path.suffix.lower() == ".pdf":
            image_data_url = build_pdf_first_page_data_url(file_path)
            if image_data_url is None:
                write_log("WARN", "PDF content could not be rendered; skip OpenAI naming for PDF")
                return None
            user_payload = [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": image_data_url,
                },
            ]
        else:
            image_bytes = file_path.read_bytes()
            image_base64 = base64.b64encode(image_bytes).decode("ascii")
            image_data_url = f"data:image/jpeg;base64,{image_base64}"
            user_payload = [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": image_data_url,
                },
            ]

        response = client.responses.create(
            model=OPENAI_MODEL,
            input=[
                {
                    "role": "user",
                    "content": user_payload,
                }
            ],
        )

        raw_name = extract_response_text(response)
        if not raw_name:
            write_log("WARN", "OpenAI naming failed: empty response text")
            return None
        return sanitize_filename_stem(raw_name)
    except Exception as exc:
        write_log("WARN", f"OpenAI naming failed: {exc}")
        return None



def destination_with_collision_avoidance(destination_dir: Path, file_name: str) -> Path:
    dst = destination_dir / file_name
    if not dst.exists():
        return dst

    stem = dst.stem
    suffix = dst.suffix
    index = 1
    while True:
        candidate = destination_dir / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1



def destination_dir_with_collision_avoidance(base_dir: Path) -> Path:
    if not base_dir.exists():
        return base_dir

    index = 1
    while True:
        candidate = base_dir.parent / f"{base_dir.name}_{index}"
        if not candidate.exists():
            return candidate
        index += 1



def batch_is_mixed(files: List[Path]) -> bool:
    has_jpeg = any(path.suffix.lower() in JPEG_SUFFIXES for path in files)
    has_pdf = any(path.suffix.lower() == ".pdf" for path in files)
    return has_jpeg and has_pdf



def ask_copy_confirmation(batch: Batch) -> Literal["yes", "no", "timeout_yes"]:
    """Show Yes/No dialog and auto-select Yes if no response in 20 seconds."""
    try:
        import tkinter as tk

        result: Dict[str, Literal["yes", "no", "timeout_yes"]] = {"value": "timeout_yes"}

        root = tk.Tk()
        root.title("コピー確認")
        root.attributes("-topmost", True)
        root.resizable(False, False)

        message = (
            "フォルダーにファイルをコピーしていいですか？\n"
            f"バッチ: {batch.destination_dir.name}\n"
            f"待機時間: {DIALOG_TIMEOUT_SECONDS}秒"
        )
        label = tk.Label(root, text=message, padx=16, pady=12, justify="left")
        label.pack()

        button_frame = tk.Frame(root)
        button_frame.pack(pady=8)

        def on_yes() -> None:
            result["value"] = "yes"
            root.destroy()

        def on_no() -> None:
            result["value"] = "no"
            root.destroy()

        yes_button = tk.Button(button_frame, text="Yes", width=12, command=on_yes)
        no_button = tk.Button(button_frame, text="No", width=12, command=on_no)
        yes_button.pack(side="left", padx=6)
        no_button.pack(side="left", padx=6)

        root.after(DIALOG_TIMEOUT_SECONDS * 1000, root.destroy)
        root.mainloop()
        return result["value"]
    except Exception as exc:
        write_log("WARN", f"dialog unavailable, use timeout-yes fallback: {exc}")
        return "timeout_yes"



def build_destination_name(src: Path, base_name: str, jpeg_index: int, pdf_index: int) -> str:
    suffix = src.suffix.lower()
    if suffix in JPEG_SUFFIXES:
        return f"{base_name}_{jpeg_index:04d}.jpg"
    if pdf_index == 1:
        return f"{base_name}.pdf"
    return f"{base_name}_{pdf_index:02d}.pdf"



def handle_batch_copy(batch: Batch) -> None:
    targets = sorted(batch.stable_files(), key=lambda p: (p.stat().st_ctime_ns, p.name))
    if not targets:
        write_log("WARN", "batch finished with no stable files")
        return

    mixed = batch_is_mixed(targets)
    write_log(
        "INFO",
        f"batch complete candidate: {batch.destination_dir.name}, files={len(targets)}, mixed={mixed}",
    )

    if batch.suggested_name_stem is None:
        first_state = batch.files.get(batch.first_detected_file)
        naming_source = batch.first_detected_file
        if first_state is None or not first_state.is_stable:
            naming_source = targets[0]

        suggested = suggest_name_for_first_file(naming_source)
        if suggested is None:
            write_log("WARN", "API naming failed; request manual filename input")
            suggested = ask_manual_name("scan_file")
            write_log("INFO", f"manual filename input used={bool(suggested)}")
        batch.suggested_name_stem = sanitize_filename_stem(suggested)

    renamed_dir = destination_dir_with_collision_avoidance(
        batch.destination_dir.parent / f"{batch.destination_dir.name}_{batch.suggested_name_stem}"
    )
    if renamed_dir != batch.destination_dir:
        try:
            batch.destination_dir.rename(renamed_dir)
            batch.destination_dir = renamed_dir
            write_log("INFO", f"batch folder renamed: {batch.destination_dir.name}")
        except OSError as exc:
            write_log("WARN", f"batch folder rename failed, keep original: {exc}")

    if not mixed:
        while True:
            write_log("INFO", f"dialog shown: batch={batch.destination_dir.name}")
            decision = ask_copy_confirmation(batch)
            write_log("INFO", f"dialog response={decision}")

            if decision == "yes":
                break
            if decision == "timeout_yes":
                write_log("INFO", "auto decision applied: no response -> Yes")
                break

            write_log("INFO", "operator selected No; wait 20s then re-show dialog")
            time.sleep(20)

    jpeg_index = 1
    pdf_index = 1
    success = 0
    failed = 0

    for src in targets:
        dst_name = build_destination_name(src, batch.suggested_name_stem, jpeg_index, pdf_index)
        if src.suffix.lower() in JPEG_SUFFIXES:
            jpeg_index += 1
        elif src.suffix.lower() == ".pdf":
            pdf_index += 1

        dst = destination_with_collision_avoidance(batch.destination_dir, dst_name)
        ok = copy_with_retry(src, dst)
        if ok:
            success += 1
            write_log("INFO", f"copied: {src.name} -> {dst.name}")
        else:
            failed += 1
            write_log("ERROR", f"failed to copy: {src}")

    write_log("INFO", f"copy result: success={success}, failed={failed}")



def run_monitor() -> None:
    write_log("INFO", f"watching: {WATCH_DIR}")
    write_log(
        "INFO",
        "settings: "
        f"poll={POLL_INTERVAL_SECONDS}s, stable={STABLE_REQUIRED_COUNT}, timeout={BATCH_TIMEOUT_SECONDS}s",
    )
    write_log("INFO", f"key path: {SECRET_KEY_PATH}")
    write_log("INFO", f"ciphertext path: {ENCRYPTED_KEY_PATH}")

    seen_files: Set[Path] = list_current_target_files()
    batch: Batch | None = None

    while True:
        current_files = list_current_target_files()
        new_files = sorted(current_files - seen_files)

        if new_files and batch is None:
            batch = Batch(new_files[0])
            batch.destination_dir.mkdir(parents=True, exist_ok=True)
            write_log("INFO", f"batch started: {batch.destination_dir.name}")
            write_log("INFO", f"first file: {new_files[0].name}")

        if batch is not None:
            for file_path in new_files:
                batch.add_file(file_path)
                write_log("INFO", f"detected: {file_path.name}")

            batch.update_stability()

            if batch.timed_out():
                handle_batch_copy(batch)
                batch = None
                seen_files = list_current_target_files()
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

        seen_files = current_files
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run_monitor()
