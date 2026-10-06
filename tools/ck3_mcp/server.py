#!/usr/bin/env python3
"""Local MCP server for Crusader Kings III mod development.

The server intentionally uses only the Python standard library.  CK3 exposes
developer-mode and console-action command line switches, so most automation can
run without brittle window scraping:

    ck3.exe -nolauncher -debug_mode -run_console_action=<command>

The MCP transport is newline-delimited JSON-RPC over stdin/stdout, as used by
the MCP stdio transport.  Diagnostics are sent to stderr so stdout remains a
clean protocol stream.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GAME_ROOT = Path(os.environ.get("CK3_GAME_ROOT", r"D:\SteamLibrary\steamapps\common\Crusader Kings III"))
GAME_EXE = Path(os.environ.get("CK3_EXE", str(GAME_ROOT / "binaries" / "ck3.exe")))
USER_DIR = Path(
    os.environ.get(
        "CK3_USER_DIR",
        str(Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Documents" / "Paradox Interactive" / "Crusader Kings III"),
    )
)
LOG_DIR = USER_DIR / "logs"
ARTIFACT_DIR = ROOT / "tools" / "ck3_mcp" / "artifacts"
SCRIPT_DIR = Path(r"C:\Users\Administrator\.codex\skills\rol-ck3-modder\scripts")
STATIC_AUDIT_SCRIPT = ROOT / "tools" / "ck3_mcp" / "rol_static_audit.py"
DDS_AUDIT_SCRIPT = ROOT / "tools" / "ck3_mcp" / "rol_dds_audit.py"

_tracked_process: subprocess.Popen[str] | None = None


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _text_result(text: str, **structured: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"content": [{"type": "text", "text": text}]}
    if structured:
        result["structuredContent"] = structured
    return result


def _error(message: str) -> dict[str, Any]:
    return {"isError": True, **_text_result(message)}


def _tail(path: Path, tail_lines: int, contains: str | None = None) -> str:
    if not path.exists():
        return f"<missing: {path}>"
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if contains:
        lines = [line for line in lines if contains.lower() in line.lower()]
    return "\n".join(lines[-max(1, min(tail_lines, 5000)):])


def _process_snapshot() -> dict[str, Any]:
    global _tracked_process
    tracked = _tracked_process
    if tracked is not None and tracked.poll() is not None:
        _tracked_process = None
        tracked = None
    # tasklist is available on Windows and avoids a third-party dependency.
    running = False
    pids: list[int] = []
    try:
        output = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq ck3.exe", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        ).stdout
        for line in output.splitlines():
            if "ck3.exe" in line.lower():
                fields = [part.strip('"') for part in line.split('","')]
                if len(fields) > 1 and fields[1].isdigit():
                    pids.append(int(fields[1]))
        running = bool(pids)
    except (OSError, subprocess.SubprocessError):
        running = tracked is not None
    return {"running": running, "pids": pids, "tracked_pid": tracked.pid if tracked else None}


def _launch(args: dict[str, Any]) -> dict[str, Any]:
    global _tracked_process
    if not GAME_EXE.exists():
        return _error(f"CK3 executable not found: {GAME_EXE}")
    if _process_snapshot()["running"]:
        return _error("CK3 is already running; stop it before starting another test session.")
    command = [str(GAME_EXE), "-nolauncher"]
    if args.get("debug_mode", True):
        command.append("-debug_mode")
    if args.get("suppress_error_log", True):
        command.append("-suppress_error_log")
    if args.get("skip_checksum", True):
        command.append("-skip_checksum")
    if args.get("window_title"):
        command.append(f"-window_title={args['window_title']}")
    if args.get("loadsave"):
        command.append(f"-loadsave={args['loadsave']}")
    if args.get("extra_args"):
        command.extend(str(value) for value in args["extra_args"])
    try:
        _tracked_process = subprocess.Popen(command, cwd=str(GAME_ROOT))
        wait_seconds = max(0.0, min(float(args.get("wait_seconds", 3)), 180.0))
        if wait_seconds:
            time.sleep(wait_seconds)
        window = _find_ck3_window(args.get("window_title"))
        return _text_result(
            f"Started CK3 (pid={_tracked_process.pid}) with developer mode={bool(args.get('debug_mode', True))}.",
            pid=_tracked_process.pid,
            command=command,
            process=_process_snapshot(),
            window_hwnd=window,
            window_ready=window is not None,
        )
    except OSError as exc:
        return _error(f"Could not start CK3: {exc}")


def _find_ck3_window(title_hint: str | None = None) -> int | None:
    if os.name != "nt":
        return None
    pids = set(_process_snapshot().get("pids", []))
    user32 = ctypes.windll.user32
    found: list[int] = []
    enum_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    @enum_proc
    def callback(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value not in pids:
            return True
        buffer = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buffer, len(buffer))
        title = buffer.value
        if title_hint and title_hint.lower() not in title.lower():
            return True
        if title_hint or "crusader kings" in title.lower() or "ck3" in title.lower():
            found.append(hwnd)
            return False
        return True

    user32.EnumWindows(callback, 0)
    return found[0] if found else None


def _send_key(hwnd: int, virtual_key: int) -> None:
    if os.name != "nt":
        raise RuntimeError("ck3_send_console requires Windows")
    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    INPUT_KEYBOARD = 1

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("ki", KEYBDINPUT), ("padding", wintypes.BYTE * 8)]

    for flags in (0, KEYEVENTF_KEYUP):
        event = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=virtual_key, wScan=0, dwFlags=flags, time=0, dwExtraInfo=None))
        if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
            raise OSError("SendInput failed")


def _send_enter() -> None:
    """Submit the developer console using the keyboard scan code."""
    if os.name != "nt":
        raise RuntimeError("ck3_send_console requires Windows")
    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_SCANCODE = 0x0008
    INPUT_KEYBOARD = 1

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", wintypes.DWORD),
            ("ki", KEYBDINPUT),
            ("padding", wintypes.BYTE * 8),
        ]

    # Enter is scan code 0x1C on the US keyboard layout.
    for flags in (KEYEVENTF_SCANCODE, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP):
        event = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=0, wScan=0x1C, dwFlags=flags, time=0, dwExtraInfo=None))
        if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
            raise OSError("SendInput failed")


def _send_unicode_text(text: str) -> None:
    if os.name != "nt":
        raise RuntimeError("ck3_send_console requires Windows")
    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_UNICODE = 0x0004
    INPUT_KEYBOARD = 1

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("ki", KEYBDINPUT), ("padding", wintypes.BYTE * 8)]

    for char in text:
        code = ord(char)
        if code > 0xFFFF or char in "\r\n":
            raise ValueError("console command must contain printable BMP characters only")
        for flags in (KEYEVENTF_UNICODE, KEYEVENTF_UNICODE | KEYEVENTF_KEYUP):
            event = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=0, wScan=code, dwFlags=flags, time=0, dwExtraInfo=None))
            if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
                raise OSError("SendInput failed")


def _send_console(args: dict[str, Any]) -> dict[str, Any]:
    command = str(args.get("command", "")).strip()
    if not command or len(command) > 2000 or "\n" in command or "\r" in command:
        return _error("command must be 1-2000 printable characters")
    if os.name != "nt":
        return _error("ck3_send_console requires Windows")
    hwnd = _find_ck3_window(args.get("window_title"))
    if hwnd is None:
        return _error("No visible CK3 window matched the running ck3.exe process.")
    try:
        if not _activate_window(hwnd):
            foreground = ctypes.windll.user32.GetForegroundWindow()
            return _error(f"Could not bring CK3 window {hwnd} to the foreground; refusing to inject input (foreground={foreground}).")
        # CK3's default developer console hotkey is the US Shift+backtick
        # (tilde) key. Some keyboard layouts expose the section key instead,
        # so the caller may select an alternate OEM key when needed.
        hotkey = str(args.get("console_hotkey", "shift_oem3")).lower()
        _send_console_hotkey(hotkey)
        time.sleep(0.15)
        _send_unicode_text(command)
        _send_enter()
        time.sleep(max(0.1, min(float(args.get("wait_seconds", 1.0)), 30.0)))
        if args.get("close_console", False):
            _send_console_hotkey(hotkey)
            time.sleep(0.2)
        return _text_result(f"Sent developer console command to window {hwnd}: {command}", hwnd=hwnd, command=command, logs={name: _tail(path, 80, args.get("log_filter")) for name, path in _log_paths().items()})
    except (OSError, RuntimeError, ValueError) as exc:
        return _error(f"Could not send console command: {exc}")


def _send_console_hotkey(hotkey: str) -> None:
    if hotkey not in {"oem3", "shift_oem3", "oem5", "shift_oem5"}:
        raise ValueError("console_hotkey must be oem3, shift_oem3, oem5, or shift_oem5")
    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_SCANCODE = 0x0008
    INPUT_KEYBOARD = 1

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]

    class INPUT(ctypes.Structure):
        _fields_ = [("type", wintypes.DWORD), ("ki", KEYBDINPUT), ("padding", wintypes.BYTE * 8)]

    # US keyboard scan codes: left Shift=0x2A, grave/tilde=0x29,
    # backslash/pipe=0x2B. Scan-code injection works with CK3's raw input path.
    scan = 0x29 if hotkey.endswith("oem3") else 0x2B

    def emit(scan_code: int, flags: int) -> None:
        event = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=0, wScan=scan_code, dwFlags=KEYEVENTF_SCANCODE | flags, time=0, dwExtraInfo=None))
        if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
            raise OSError("SendInput failed")

    shifted = hotkey.startswith("shift_")
    if shifted:
        emit(0x2A, 0)
    emit(scan, 0)
    emit(scan, KEYEVENTF_KEYUP)
    if shifted:
        emit(0x2A, KEYEVENTF_KEYUP)


_HOTKEY_SCANS = {
    "alt": 0x38,
    "ctrl": 0x1D,
    "shift": 0x2A,
    "a": 0x1E,
    "c": 0x2E,
    "d": 0x20,
    "e": 0x12,
    "f": 0x21,
    "i": 0x17,
    "l": 0x26,
    "m": 0x32,
    "p": 0x19,
    "q": 0x10,
    "r": 0x13,
    "s": 0x1F,
    "t": 0x14,
    "v": 0x2F,
    "x": 0x2D,
    "z": 0x2C,
    "enter": 0x1C,
    "escape": 0x01,
    "esc": 0x01,
}


def _send_hotkey(combo: str) -> list[str]:
    """Send a small allowlisted scan-code hotkey after foreground validation."""
    if os.name != "nt":
        raise RuntimeError("ck3_hotkey requires Windows")
    keys = [part.strip().lower() for part in combo.split("+") if part.strip()]
    if len(keys) < 2 or len(keys) > 3 or any(key not in _HOTKEY_SCANS for key in keys):
        raise ValueError("hotkey must use 2-3 allowlisted keys, for example alt+a")
    modifiers = [key for key in keys[:-1] if key in {"alt", "ctrl", "shift"}]
    if len(modifiers) != len(keys) - 1 or keys[-1] in {"alt", "ctrl", "shift"}:
        raise ValueError("hotkey modifiers must come first and the final key must be non-modifier")

    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_SCANCODE = 0x0008
    INPUT_KEYBOARD = 1

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", wintypes.DWORD),
            ("ki", KEYBDINPUT),
            ("padding", wintypes.BYTE * 8),
        ]

    def emit(key: str, flags: int) -> None:
        event = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=0, wScan=_HOTKEY_SCANS[key], dwFlags=KEYEVENTF_SCANCODE | flags, time=0, dwExtraInfo=None))
        if user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
            raise OSError("SendInput failed")

    for key in modifiers:
        emit(key, 0)
    emit(keys[-1], 0)
    emit(keys[-1], KEYEVENTF_KEYUP)
    for key in reversed(modifiers):
        emit(key, KEYEVENTF_KEYUP)
    return keys


def _window_rect(hwnd: int) -> tuple[int, int, int, int]:
    rect = wintypes.RECT()
    if not ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise OSError("GetWindowRect failed")
    return rect.left, rect.top, rect.right, rect.bottom


def _activate_window(hwnd: int) -> bool:
    user32 = ctypes.windll.user32
    foreground = user32.GetForegroundWindow()
    foreground_thread = user32.GetWindowThreadProcessId(foreground, None) if foreground else 0
    target_thread = user32.GetWindowThreadProcessId(hwnd, None)
    if foreground_thread and target_thread and foreground_thread != target_thread:
        user32.AttachThreadInput(foreground_thread, target_thread, True)
    try:
        # Windows may reject SetForegroundWindow when the caller is not the
        # current foreground process.  A short ALT tap clears that foreground
        # lock, after which the normal activation calls work reliably.
        VK_MENU = 0x12
        user32.keybd_event(VK_MENU, 0, 0, 0)
        user32.keybd_event(VK_MENU, 0, 0x0002, 0)
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        user32.BringWindowToTop(hwnd)
        user32.SetActiveWindow(hwnd)
        user32.SetFocus(hwnd)
        user32.SetForegroundWindow(hwnd)
        user32.SwitchToThisWindow(hwnd, True)
    finally:
        if foreground_thread and target_thread and foreground_thread != target_thread:
            user32.AttachThreadInput(foreground_thread, target_thread, False)
    for _ in range(3):
        time.sleep(0.1)
        if user32.GetForegroundWindow() == hwnd:
            return True
        # A foreground-lock policy can reject the first request. Retrying
        # after the ALT tap is safe and avoids sending input elsewhere.
        user32.SetForegroundWindow(hwnd)
    return user32.GetForegroundWindow() == hwnd


def _capture_screen(args: dict[str, Any]) -> dict[str, Any]:
    if os.name != "nt":
        return _error("ck3_capture_screen requires Windows")
    hwnd = _find_ck3_window(args.get("window_title"))
    if hwnd is None:
        return _error("No visible CK3 window matched the running ck3.exe process.")
    try:
        from PIL import ImageGrab

        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = ARTIFACT_DIR / "screenshots" / f"ck3_{stamp}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        left, top, right, bottom = _window_rect(hwnd)
        if not _activate_window(hwnd):
            foreground = ctypes.windll.user32.GetForegroundWindow()
            return _error(f"Could not bring CK3 window {hwnd} to the foreground; refusing to capture (foreground={foreground}).")
        # DirectX fullscreen windows often return a black PrintWindow frame;
        # after activation, a full desktop capture contains the selected CK3 window.
        image = ImageGrab.grab(all_screens=True)
        foreground_after = ctypes.windll.user32.GetForegroundWindow()
        if foreground_after != hwnd:
            return _error(f"CK3 lost the foreground during capture; refusing to save an unrelated desktop image (foreground={foreground_after}, target={hwnd}).")
        image.save(path)
        return _text_result(f"Captured CK3 screen to {path}.", path=str(path), hwnd=hwnd, window_rect=[left, top, right, bottom], size=list(image.size))
    except (OSError, RuntimeError, ImportError) as exc:
        return _error(f"Could not capture CK3 screen: {exc}")


def _click_window(args: dict[str, Any]) -> dict[str, Any]:
    if os.name != "nt":
        return _error("ck3_click requires Windows")
    try:
        x = int(args["x"])
        y = int(args["y"])
    except (KeyError, TypeError, ValueError):
        return _error("x and y are required window-relative integer coordinates")
    hwnd = _find_ck3_window(args.get("window_title"))
    if hwnd is None:
        return _error("No visible CK3 window matched the running ck3.exe process.")
    try:
        user32 = ctypes.windll.user32
        left, top, right, bottom = _window_rect(hwnd)
        if not (0 <= x < right - left and 0 <= y < bottom - top):
            return _error(f"Click coordinate ({x}, {y}) is outside window bounds {(right - left, bottom - top)}")
        if not _activate_window(hwnd):
            foreground = user32.GetForegroundWindow()
            return _error(f"Could not bring CK3 window {hwnd} to the foreground; refusing to click (foreground={foreground}).")
        time.sleep(0.15)
        user32.SetCursorPos(left + x, top + y)
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
        time.sleep(max(0.1, min(float(args.get("wait_seconds", 1.0)), 30.0)))
        return _text_result(f"Clicked CK3 window at ({x}, {y}).", hwnd=hwnd, window_rect=[left, top, right, bottom], x=x, y=y)
    except OSError as exc:
        return _error(f"Could not click CK3 window: {exc}")


def _hotkey_window(args: dict[str, Any]) -> dict[str, Any]:
    if os.name != "nt":
        return _error("ck3_hotkey requires Windows")
    combo = str(args.get("hotkey", "")).strip()
    hwnd = _find_ck3_window(args.get("window_title"))
    if hwnd is None:
        return _error("No visible CK3 window matched the running ck3.exe process.")
    try:
        if not _activate_window(hwnd):
            foreground = ctypes.windll.user32.GetForegroundWindow()
            return _error(f"Could not bring CK3 window {hwnd} to the foreground; refusing to inject hotkey (foreground={foreground}).")
        keys = _send_hotkey(combo)
        time.sleep(max(0.1, min(float(args.get("wait_seconds", 1.0)), 30.0)))
        return _text_result(f"Sent CK3 hotkey {combo}.", hwnd=hwnd, keys=keys)
    except (OSError, RuntimeError, ValueError) as exc:
        return _error(f"Could not send hotkey: {exc}")


def _stop() -> dict[str, Any]:
    global _tracked_process
    before = _process_snapshot()
    if not before["running"]:
        return _text_result("CK3 is not running.", process=before)
    if _tracked_process is not None and _tracked_process.poll() is None:
        _tracked_process.terminate()
        try:
            _tracked_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            _tracked_process.kill()
    else:
        subprocess.run(["taskkill", "/IM", "ck3.exe", "/T", "/F"], capture_output=True, text=True, check=False)
    _tracked_process = None
    deadline = time.monotonic() + 10
    after = _process_snapshot()
    while after["running"] and time.monotonic() < deadline:
        time.sleep(0.25)
        after = _process_snapshot()
    if after["running"]:
        return _error(f"Stop requested, but CK3 is still running: {after}")
    return _text_result("Stopped CK3.", process=after)


def _run_console_action(args: dict[str, Any]) -> dict[str, Any]:
    if not GAME_EXE.exists():
        return _error(f"CK3 executable not found: {GAME_EXE}")
    if _process_snapshot()["running"]:
        return _error("CK3 is already running; console-action mode starts a separate process and must run alone.")
    command = str(args.get("command", "")).strip()
    if not command or len(command) > 4000:
        return _error("command must be 1-4000 characters")
    stage = str(args.get("stage", "application")).lower()
    stage_flag = {
        "main": "-run_console_action_main",
        "clausewitz": "-run_console_action_clausewitz",
        "application": "-run_console_action",
    }.get(stage)
    if stage_flag is None:
        return _error("stage must be main, clausewitz, or application")
    before = {name: path.stat().st_mtime_ns if path.exists() else None for name, path in _log_paths().items()}
    argv = [str(GAME_EXE), "-nolauncher", "-suppress_error_log", "-skip_checksum"]
    if args.get("debug_mode", True):
        argv.append("-debug_mode")
    argv.append(f"{stage_flag}={command}")
    started = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            cwd=str(GAME_ROOT),
            capture_output=True,
            text=True,
            timeout=max(5, min(int(args.get("timeout_seconds", 120)), 600)),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return _error(f"Console action timed out after {exc.timeout}s: {command}")
    logs = {name: _tail(path, 80, args.get("log_filter")) for name, path in _log_paths().items()}
    return _text_result(
        f"Console action exited with code {completed.returncode} after {time.monotonic() - started:.1f}s.",
        command=command,
        stage=stage,
        returncode=completed.returncode,
        stdout=completed.stdout[-4000:],
        stderr=completed.stderr[-4000:],
        logs=logs,
        log_mtimes_before=before,
    )


def _log_paths() -> dict[str, Path]:
    return {name: LOG_DIR / f"{name}.log" for name in ("error", "game", "setup", "debug")}


def _read_logs(args: dict[str, Any]) -> dict[str, Any]:
    names = args.get("files") or ["error"]
    unknown = sorted(set(names) - set(_log_paths()))
    if unknown:
        return _error(f"Unknown log names: {', '.join(unknown)}")
    tail_lines = int(args.get("tail_lines", 200))
    contains = args.get("contains")
    logs = {name: _tail(_log_paths()[name], tail_lines, contains) for name in names}
    return _text_result("\n\n".join(f"[{name}.log]\n{body}" for name, body in logs.items()), logs=logs)


def _snapshot_logs() -> dict[str, Any]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = ARTIFACT_DIR / "log_snapshots" / stamp
    destination.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for path in _log_paths().values():
        if path.exists():
            target = destination / path.name
            shutil.copy2(path, target)
            copied.append(str(target))
    return _text_result(f"Copied {len(copied)} CK3 logs to {destination}.", destination=str(destination), files=copied)


def _validate_mod() -> dict[str, Any]:
    commands = [
        [sys.executable, str(STATIC_AUDIT_SCRIPT), str(ROOT)],
        [sys.executable, str(DDS_AUDIT_SCRIPT), str(ROOT)],
        [sys.executable, str(SCRIPT_DIR / "check_bom_utf8.py"), str(ROOT)],
        [sys.executable, str(SCRIPT_DIR / "check_rol_prefix.py"), str(ROOT)],
        [sys.executable, str(SCRIPT_DIR / "rol_smoke_checks.py"), str(ROOT)],
    ]
    results = []
    passed = True
    for argv in commands:
        completed = subprocess.run(argv, cwd=str(ROOT), capture_output=True, text=True, check=False)
        item = {"command": argv, "returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
        results.append(item)
        passed = passed and completed.returncode == 0
    text = "\n\n".join(f"$ {' '.join(item['command'])}\n{item['stdout']}{item['stderr']}" for item in results)
    return _text_result("RoL validation passed." if passed else "RoL validation failed.\n" + text, passed=passed, results=results)


def _static_audit() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(STATIC_AUDIT_SCRIPT), str(ROOT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    passed = completed.returncode == 0
    output = completed.stdout + completed.stderr
    return _text_result(
        "RoL static audit passed." if passed else "RoL static audit failed.\n" + output,
        passed=passed,
        output=output,
        returncode=completed.returncode,
    )


def _dds_audit() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(DDS_AUDIT_SCRIPT), str(ROOT)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    passed = completed.returncode == 0
    output = completed.stdout + completed.stderr
    return _text_result(
        "RoL DDS audit passed." if passed else "RoL DDS audit failed.\n" + output,
        passed=passed,
        output=output,
        returncode=completed.returncode,
    )
def _smoke_test() -> dict[str, Any]:
    validation = _validate_mod()
    validation_ok = bool(validation.get("structuredContent", {}).get("passed"))
    action = _run_console_action({"command": "debug_mode", "stage": "application", "timeout_seconds": 120, "log_filter": "rol"})
    action_data = action.get("structuredContent", {})
    action_ok = action.get("isError") is not True and action_data.get("returncode") == 0
    error_log = _tail(_log_paths()["error"], 500, "rol")
    passed = validation_ok and action_ok and not error_log.strip()
    message = "CK3/RoL smoke test passed." if passed else "CK3/RoL smoke test failed."
    return _text_result(message, passed=passed, validation=validation, console_action=action, rol_error_log=error_log)


TOOLS = [
    {
        "name": "ck3_environment",
        "description": "Return CK3, RoL, launcher descriptor, and log paths plus the installed executable state.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ck3_process",
        "description": "Inspect whether Crusader Kings III is currently running.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ck3_launch",
        "description": "Launch CK3 with developer mode enabled by default for an interactive test session.",
        "inputSchema": {"type": "object", "properties": {"debug_mode": {"type": "boolean"}, "suppress_error_log": {"type": "boolean"}, "skip_checksum": {"type": "boolean"}, "window_title": {"type": "string"}, "loadsave": {"type": "string"}, "wait_seconds": {"type": "number", "minimum": 0, "maximum": 180}, "extra_args": {"type": "array", "items": {"type": "string"}}}},
    },
    {
        "name": "ck3_stop",
        "description": "Stop the CK3 test process started by this server, or the visible ck3.exe process if needed.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ck3_run_console_action",
        "description": "Run one CK3 developer console command through the official -run_console_action interface and collect logs.",
        "inputSchema": {"type": "object", "required": ["command"], "properties": {"command": {"type": "string"}, "stage": {"type": "string", "enum": ["main", "clausewitz", "application"]}, "debug_mode": {"type": "boolean"}, "timeout_seconds": {"type": "integer"}, "log_filter": {"type": "string"}}},
    },
    {
        "name": "ck3_send_console",
        "description": "Send one developer console command to the visible CK3 window using Windows native input.",
        "inputSchema": {"type": "object", "required": ["command"], "properties": {"command": {"type": "string"}, "window_title": {"type": "string"}, "console_hotkey": {"type": "string", "enum": ["oem3", "shift_oem3", "oem5", "shift_oem5"]}, "wait_seconds": {"type": "number"}, "close_console": {"type": "boolean"}, "log_filter": {"type": "string"}}},
    },
    {
        "name": "ck3_capture_screen",
        "description": "Capture the visible CK3 desktop screen to an ignored local test artifact and return its window bounds.",
        "inputSchema": {"type": "object", "properties": {"window_title": {"type": "string"}}},
    },
    {
        "name": "ck3_click",
        "description": "Click a window-relative coordinate in the visible CK3 window for event and activity UI tests.",
        "inputSchema": {"type": "object", "required": ["x", "y"], "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "window_title": {"type": "string"}, "wait_seconds": {"type": "number"}}},
    },
    {
        "name": "ck3_hotkey",
        "description": "Send an allowlisted keyboard shortcut to the visible CK3 window after foreground validation.",
        "inputSchema": {"type": "object", "required": ["hotkey"], "properties": {"hotkey": {"type": "string", "description": "Two or three keys joined by +, for example alt+a."}, "window_title": {"type": "string"}, "wait_seconds": {"type": "number"}}},
    },
    {
        "name": "ck3_read_logs",
        "description": "Read a bounded tail of CK3 logs, optionally filtered by text.",
        "inputSchema": {"type": "object", "properties": {"files": {"type": "array", "items": {"type": "string", "enum": ["error", "game", "setup", "debug"]}}, "tail_lines": {"type": "integer"}, "contains": {"type": "string"}}},
    },
    {
        "name": "ck3_snapshot_logs",
        "description": "Copy current CK3 logs into a timestamped local artifact directory without deleting source logs.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ck3_static_audit",
        "description": "Run the fast repository-local RoL activity, localization, owned-gfx, and canonical generated-DDS static audit without launching CK3.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ck3_dds_audit",
        "description": "Audit all RoL-owned DDS headers, compression tags, dimensions, and legacy-size warnings without launching CK3.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ck3_validate_mod",
        "description": "Run the fast RoL static audit plus BOM, rol_ prefix, and RoL smoke validation scripts.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ck3_smoke_test",
        "description": "Run static RoL checks and a CK3 1.20 developer console initialization probe, then fail on RoL error-log entries.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def _call_tool(name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "ck3_environment":
        descriptor = ROOT / "descriptor.mod"
        return _text_result(
            f"RoL={ROOT}\nCK3={GAME_ROOT}\nExecutable={GAME_EXE}\nLogs={LOG_DIR}",
            rol_root=str(ROOT), game_root=str(GAME_ROOT), executable=str(GAME_EXE), executable_exists=GAME_EXE.exists(),
            descriptor=str(descriptor), descriptor_exists=descriptor.exists(), user_dir=str(USER_DIR), logs=str(LOG_DIR), process=_process_snapshot(),
        )
    if name == "ck3_process":
        return _text_result(_json(_process_snapshot()), process=_process_snapshot())
    if name == "ck3_launch":
        return _launch(args)
    if name == "ck3_stop":
        return _stop()
    if name == "ck3_run_console_action":
        return _run_console_action(args)
    if name == "ck3_send_console":
        return _send_console(args)
    if name == "ck3_capture_screen":
        return _capture_screen(args)
    if name == "ck3_click":
        return _click_window(args)
    if name == "ck3_hotkey":
        return _hotkey_window(args)
    if name == "ck3_read_logs":
        return _read_logs(args)
    if name == "ck3_snapshot_logs":
        return _snapshot_logs()
    if name == "ck3_static_audit":
        return _static_audit()
    if name == "ck3_dds_audit":
        return _dds_audit()
    if name == "ck3_validate_mod":
        return _validate_mod()
    if name == "ck3_smoke_test":
        return _smoke_test()
    return _error(f"Unknown tool: {name}")


def _handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if method == "initialize":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "rol-ck3-mcp", "version": "0.1.0"}}}
    if method in {"notifications/initialized", "notifications/cancelled"}:
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params") or {}
        return {"jsonrpc": "2.0", "id": request_id, "result": _call_tool(str(params.get("name", "")), params.get("arguments") or {})}
    if request_id is not None:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    return None


def main() -> int:
    for raw in sys.stdin.buffer:
        if not raw.strip():
            continue
        try:
            message = json.loads(raw.decode("utf-8"))
            response = _handle(message)
            if response is not None:
                sys.stdout.write(_json(response) + "\n")
                sys.stdout.flush()
        except Exception as exc:  # Keep the stdio server alive for the next request.
            print(f"ck3_mcp error: {exc}", file=sys.stderr)
            if isinstance(locals().get("message"), dict) and "id" in message:
                sys.stdout.write(_json({"jsonrpc": "2.0", "id": message["id"], "error": {"code": -32603, "message": str(exc)}}) + "\n")
                sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
