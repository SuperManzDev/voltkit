"""
Android Debug Bridge (ADB) device manager and fast-actions for VoltKit.
"""
import os
import shutil
import subprocess
from typing import List, Dict, Optional
from rich.table import Table
from voltkit.utils.formatting import console, print_error, print_info, print_success

def find_adb_path() -> Optional[str]:
    """Finds adb binary in PATH or common local user paths."""
    which_adb = shutil.which("adb")
    if which_adb:
        return which_adb
    
    candidates = [
        r"C:\Users\MNZ\adb.exe",
        r"C:\Users\MNZ\platform-tools\adb.exe",
        os.path.expanduser(r"~\platform-tools\adb.exe"),
        os.path.expanduser(r"~\AppData\Local\Android\Sdk\platform-tools\adb.exe")
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None

def get_adb_devices() -> List[Dict]:
    """Lists connected ADB devices and basic device info."""
    adb_bin = find_adb_path()
    if not adb_bin:
        print_error("adb executable not found on system or user paths.")
        return []

    try:
        proc = subprocess.run([adb_bin, "devices", "-l"], capture_output=True, text=True, timeout=5)
        lines = proc.stdout.strip().splitlines()
        devices = []
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            serial = parts[0]
            state = parts[1] if len(parts) > 1 else "unknown"
            details = " ".join(parts[2:]) if len(parts) > 2 else ""
            devices.append({"serial": serial, "state": state, "details": details})
        return devices
    except Exception as e:
        print_error(f"Failed to query ADB devices: {e}")
        return []

def display_adb_devices():
    """Displays ADB devices in a styled table."""
    adb_bin = find_adb_path()
    if not adb_bin:
        print_error("ADB binary not found.")
        return

    devices = get_adb_devices()
    if not devices:
        print_info("No Android / ADB devices currently detected.")
        return

    table = Table(title="[ADB] Connected Android / ADB Devices", header_style="bold green", border_style="dim green")
    table.add_column("Serial / Device ID", style="bold cyan", width=22)
    table.add_column("State", justify="center", width=12)
    table.add_column("Hardware & Model Details", style="yellow", width=42)

    for d in devices:
        state_style = "green" if d["state"] == "device" else "red"
        table.add_row(
            d["serial"],
            f"[{state_style}]{d['state']}[/{state_style}]",
            d["details"] or "N/A"
        )

    console.print(table)

def take_adb_screenshot(dest_path: str = "screenshot.png"):
    """Captures a screenshot from the active Android device and pulls it."""
    adb_bin = find_adb_path()
    if not adb_bin:
        print_error("ADB binary not found.")
        return

    print_info("Capturing screenshot on Android device...")
    try:
        subprocess.run([adb_bin, "shell", "screencap", "-p", "/sdcard/volt_screen.png"], check=True, timeout=10)
        subprocess.run([adb_bin, "pull", "/sdcard/volt_screen.png", dest_path], check=True, timeout=10)
        subprocess.run([adb_bin, "shell", "rm", "/sdcard/volt_screen.png"], check=True, timeout=5)
        print_success(f"Screenshot saved to: {dest_path}")
    except Exception as e:
        print_error(f"Screenshot capture failed: {e}")
