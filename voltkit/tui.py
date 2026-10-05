"""
Interactive TUI Dashboard for VoltKit.
"""
import os
import sys
import psutil
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich.prompt import Prompt
from voltkit.utils.formatting import console, BANNER, print_info, print_error
from voltkit.hardware.usb import display_usb_table
from voltkit.hardware.serial_mon import list_com_ports, monitor_serial
from voltkit.hardware.adb_helper import display_adb_devices, take_adb_screenshot
from voltkit.rev.hexview import hex_dump
from voltkit.rev.strings import display_strings
from voltkit.rev.entropy import display_entropy_map
from voltkit.rev.converter import convert_value

def get_system_quick_stats() -> Panel:
    """Returns a quick summary panel of system hardware resources."""
    cpu_pct = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    mem_used_gb = mem.used / (1024 ** 3)
    mem_total_gb = mem.total / (1024 ** 3)

    content = (
        f"[bold cyan]Host OS:[/bold cyan] Windows | "
        f"[bold cyan]CPU Load:[/bold cyan] [yellow]{cpu_pct}%[/yellow] | "
        f"[bold cyan]Memory:[/bold cyan] [yellow]{mem_used_gb:.1f} / {mem_total_gb:.1f} GB ({mem.percent}%)[/yellow]"
    )
    return Panel(content, title="[SYS] System Quick Stats", border_style="cyan", padding=(0, 1))

def run_tui_loop():
    """Main interactive TUI loop."""
    while True:
        console.clear()
        console.print(BANNER)
        console.print(get_system_quick_stats())

        menu_table = Table(title="[HUB] VoltKit Hardware & Reverse Engineering Hub", border_style="dim cyan", header_style="bold magenta")
        menu_table.add_column("Key", justify="center", style="bold yellow", width=6)
        menu_table.add_column("Module", style="bold white", width=26)
        menu_table.add_column("Description", style="dim", width=48)

        menu_table.add_row("1", "USB Hardware Inspector", "Scan connected USB devices & detect dev targets")
        menu_table.add_row("2", "COM / Serial Ports", "List serial ports & open live serial monitor")
        menu_table.add_row("3", "Android / ADB Devices", "View ADB devices, status & pull screenshots")
        menu_table.add_row("4", "Binary Hex Inspector", "Colorized hex viewer with magic header detection")
        menu_table.add_row("5", "Strings Extractor", "Extract ASCII and UTF-16 strings with filters")
        menu_table.add_row("6", "Firmware Entropy Map", "Analyze Shannon entropy to spot encrypted code")
        menu_table.add_row("7", "Data & Endianness Calc", "Deconstruct hex/int/bits/floats/CRC32")
        menu_table.add_row("Q", "Exit", "Close VoltKit")

        console.print(menu_table)
        console.print()

        choice = Prompt.ask("[bold cyan]Select an option[/bold cyan]", choices=["1", "2", "3", "4", "5", "6", "7", "q", "Q"], default="1")
        console.print()

        if choice in ("q", "Q"):
            console.print("[bold yellow]Exiting VoltKit. Happy hacking![/bold yellow]\n")
            break

        elif choice == "1":
            console.clear()
            display_usb_table()
            Prompt.ask("\n[dim]Press Enter to return to menu...[/dim]")

        elif choice == "2":
            console.clear()
            ports = list_com_ports()
            if ports:
                sub_choice = Prompt.ask("\nMonitor a port? (y/n)", choices=["y", "n"], default="n")
                if sub_choice.lower() == "y":
                    port_name = Prompt.ask("Enter port name (e.g. COM3)")
                    baud = Prompt.ask("Baud rate", default="115200")
                    monitor_serial(port_name, int(baud))
            Prompt.ask("\n[dim]Press Enter to return to menu...[/dim]")

        elif choice == "3":
            console.clear()
            display_adb_devices()
            action = Prompt.ask("\nTake screenshot from active device? (y/n)", choices=["y", "n"], default="n")
            if action.lower() == "y":
                take_adb_screenshot("adb_screen.png")
            Prompt.ask("\n[dim]Press Enter to return to menu...[/dim]")

        elif choice == "4":
            console.clear()
            path = Prompt.ask("Enter binary file path")
            if os.path.isfile(path):
                offset_str = Prompt.ask("Start offset (hex or dec)", default="0x0")
                offset = int(offset_str, 16) if offset_str.lower().startswith("0x") else int(offset_str)
                hex_dump(path, offset=offset, length=256)
            else:
                print_error("File does not exist.")
            Prompt.ask("\n[dim]Press Enter to return to menu...[/dim]")

        elif choice == "5":
            console.clear()
            path = Prompt.ask("Enter binary file path")
            if os.path.isfile(path):
                min_len = int(Prompt.ask("Minimum string length", default="4"))
                regex_filt = Prompt.ask("Pattern / keyword filter (leave empty for none)", default="")
                display_strings(path, min_len=min_len, pattern_filter=regex_filt or None)
            else:
                print_error("File does not exist.")
            Prompt.ask("\n[dim]Press Enter to return to menu...[/dim]")

        elif choice == "6":
            console.clear()
            path = Prompt.ask("Enter firmware / binary path")
            if os.path.isfile(path):
                display_entropy_map(path)
            else:
                print_error("File does not exist.")
            Prompt.ask("\n[dim]Press Enter to return to menu...[/dim]")

        elif choice == "7":
            console.clear()
            val = Prompt.ask("Enter integer, hex literal (e.g. 0x1234), or binary (0b1010)")
            convert_value(val)
            Prompt.ask("\n[dim]Press Enter to return to menu...[/dim]")
