"""
USB device enumeration and embedded hardware identification for Windows.
"""
import re
import json
import subprocess
from typing import List, Dict, Optional
from rich.table import Table
from rich.text import Text
from voltkit.utils.formatting import console, print_error, print_info

KNOWN_VENDORS: Dict[str, str] = {
    "0483": "STMicroelectronics (STM32 / ST-Link)",
    "2E8A": "Raspberry Pi Foundation (RP2040 / Pico / RP2350)",
    "303A": "Espressif Systems (ESP32 / S2 / S3 / C3 / C6)",
    "0451": "Texas Instruments (MSP430 / C2000 / TI-Nspire)",
    "0403": "FTDI (FT232 / FT2232 / FT4232 USB-UART/JTAG)",
    "1A86": "WCH / QinHeng (CH340 / CH341 / CH9102 / CH32V)",
    "10C4": "Silicon Labs (CP2102 / CP2104 / CP210x)",
    "1366": "SEGGER Microcontroller (J-Link / J-Trace)",
    "03EB": "Microchip / Atmel (AVR / SAM / ATmega)",
    "1FC9": "NXP Semiconductors (LPC / i.MX RT)",
    "2341": "Arduino SA",
    "239A": "Adafruit Industries (CircuitPython / Feather)",
    "16C0": "Teensy / PJRC / Open Source USB",
    "1209": "pid.codes (Open Source Hardware)",
    "04D8": "Microchip Technology (PIC / MCP)",
    "18D1": "Google Inc. (Android ADB / Fastboot / Pixel)",
    "05AC": "Apple Inc. (DFU / Recovery / Lightning)",
    "046D": "Logitech Inc.",
    "1038": "SteelSeries ApS",
    "8087": "Intel Corp.",
    "0BDA": "Realtek Semiconductor Corp.",
    "5986": "Sunplus / Bison (Integrated Camera)",
    "2109": "VIA Labs Inc. (USB Hub)",
    "05E3": "Genesys Logic (USB Hub)",
    "0409": "NEC Corp. / Renesas",
    "0B05": "ASUSTeK Computer",
}

DEV_TARGET_VIDS = {
    "0483", "2E8A", "303A", "0451", "0403", "1A86", "10C4", 
    "1366", "03EB", "1FC9", "2341", "239A", "16C0", "1209", "04D8"
}

def scan_usb_devices() -> List[Dict]:
    """Scans USB devices via PowerShell Get-CimInstance Win32_PnPEntity."""
    ps_cmd = (
        "Get-CimInstance Win32_PnPEntity | "
        "Where-Object { $_.DeviceID -like 'USB*' } | "
        "Select-Object Name, DeviceID, Manufacturer, Status, Description | "
        "ConvertTo-Json -Compress"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=10,
            check=True
        )
        output = proc.stdout.strip()
        if not output:
            return []
        data = json.loads(output)
        if isinstance(data, dict):
            data = [data]
    except Exception as e:
        print_error(f"Failed to query USB devices: {e}")
        return []

    devices = []
    seen_ids = set()
    vid_pid_pattern = re.compile(r"VID_([0-9A-Fa-f]{4})&PID_([0-9A-Fa-f]{4})", re.IGNORECASE)

    for item in data:
        device_id = item.get("DeviceID", "")
        if device_id in seen_ids:
            continue
        seen_ids.add(device_id)

        match = vid_pid_pattern.search(device_id)
        vid = match.group(1).upper() if match else "N/A"
        pid = match.group(2).upper() if match else "N/A"

        vendor_name = KNOWN_VENDORS.get(vid, item.get("Manufacturer") or "Unknown Vendor")
        is_embedded = vid in DEV_TARGET_VIDS
        is_android = vid == "18D1"

        name = item.get("Name") or item.get("Description") or "Unknown Device"

        devices.append({
            "name": name,
            "vid": vid,
            "pid": pid,
            "vendor": vendor_name,
            "status": item.get("Status", "OK"),
            "device_id": device_id,
            "is_embedded": is_embedded,
            "is_android": is_android
        })

    return devices

def display_usb_table(embedded_only: bool = False):
    """Displays the USB device table in a styled Rich view."""
    devices = scan_usb_devices()
    if not devices:
        print_info("No USB devices found.")
        return

    if embedded_only:
        devices = [d for d in devices if d["is_embedded"] or d["is_android"]]
        title = "[DEV] Connected Embedded / Target Devices"
    else:
        title = "[USB] Connected USB Devices & Hardware"

    table = Table(title=title, show_lines=False, header_style="bold magenta", border_style="dim cyan")
    table.add_column("Type", justify="center", width=8)
    table.add_column("Device Name", style="bold white", width=34)
    table.add_column("VID:PID", justify="center", style="cyan", width=12)
    table.add_column("Vendor / Target Hardware", style="yellow", width=42)
    table.add_column("Status", justify="center", style="green", width=8)

    for d in sorted(devices, key=lambda x: (not x["is_embedded"], not x["is_android"], x["vendor"])):
        if d["is_embedded"]:
            badge = "[bold yellow][DEV][/bold yellow]"
        elif d["is_android"]:
            badge = "[bold green][AND][/bold green]"
        else:
            badge = "[dim]USB[/dim]"

        vid_pid = f"{d['vid']}:{d['pid']}" if d['vid'] != 'N/A' else "-"
        status_style = "green" if d["status"] == "OK" else "red"

        table.add_row(
            badge,
            d["name"],
            vid_pid,
            d["vendor"],
            f"[{status_style}]{d['status']}[/{status_style}]"
        )

    console.print(table)
    console.print(f"[dim]Total detected devices: {len(devices)}[/dim]\n")
